# import
from pathlib import Path
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.utils import save_image

import cv2
import imageio
from tqdm import tqdm

import Arbitrary_ST_Pytorch.NNs as NNs
from Arbitrary_ST_Pytorch.utilities import adain_layer, color_prev

import warnings
warnings.filterwarnings("ignore")

# set the device
#device = "cpu"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def all_transform(new_size, crop):
    transformation_seq = []
    if new_size != 0:
        transformation_seq.append(transforms.Resize(new_size))
    if crop:
        transformation_seq.append(transforms.CenterCrop(new_size))

    transformation_seq.append(transforms.ToTensor())
    final_transform = transforms.Compose(transformation_seq)
    return final_transform

def process_img(path, new_size, crop):

    img_transf = all_transform(new_size, crop)
    img = Image.open(str(path))
    if img.mode == 'CMYK':
        img= img.convert('RGB')
    img_tensor = img_transf(img)
    if img_tensor.size()[0] >3:
        img_tensor = img_tensor[ :3, :, : ]

    return img_tensor


def StyleTransfer(contentIMG, styleIMG, vgg_m, decoder_m, level=1.0, InterpolateWeights=None):

    style_feat = vgg_m(styleIMG)
    content_feat = vgg_m(contentIMG)
    assert (0.0<=level<=1.0)

    if InterpolateWeights is not None:
        _, a, b, c = content_feat.size()
        BaseFeat = adain_layer(style_feat, content_feat)
        features = torch.FloatTensor(1, a, b, c).zero_().to(device)
        for j, weight in enumerate(InterpolateWeights):
            features = features + weight*BaseFeat[j:j+1]
        content_feat = content_feat[0:1]
    else:
        features = adain_layer(style_feat, content_feat)
    features = features*level + content_feat*(1-level)
    return decoder_m(features)


def video_trans(content_p, style_p, ColorPresrv=False, level = 1.0,
                addr_vgg='Arbitrary_ST_Pytorch/models/vgg_normalised.pth', addr_decoder='Arbitrary_ST_Pytorch/models/decoder.pth',
                ContentSize=0, StyleSize=0, crop=False, Out_Extension='.mp4', output_p='static/pics/output'):


    ## models
    decoder_m = NNs.decoder
    decoder_m.eval()
    decoder_m.load_state_dict(torch.load(addr_decoder))
    vgg_m = NNs.vgg

    decoder_m.to(device)

    vgg_m.eval()
    vgg_m.load_state_dict(torch.load(addr_vgg))
    vgg_m = nn.Sequential(*list(vgg_m.children())[:31])
    vgg_m.to(device)

    ## input path
    style_img_pa = Path(style_p)
    content_vid_pa = Path(content_p)

    #video details
    contentVID = cv2.VideoCapture(content_p)

    VID_height = int(contentVID.get(cv2.CAP_PROP_FRAME_HEIGHT))
    VID_width = int(contentVID.get(cv2.CAP_PROP_FRAME_WIDTH))
    VID_length = int(contentVID.get(cv2.CAP_PROP_FRAME_COUNT))
    VID_fps = int(contentVID.get(cv2.CAP_PROP_FPS))
    assert VID_fps!=0, 'The fps of the video cannot be zero, make sure you uploaded the correct one.'

    # prepare output paths
    output_folder = Path(output_p)
    output_folder.mkdir(exist_ok = True, parents = True)

    # prepare transsformations
    c_transformation = all_transform(ContentSize, crop)
    s_transformation = all_transform(StyleSize, crop)

    iter_tq = tqdm(total = VID_length)

    if style_img_pa.suffix in [".jpeg", ".JPEG", ".jpg", ".JPG", ".png", ".PNG"]:

        # conversion
        style_temp = Image.open(style_img_pa)
        if style_temp.mode != 'RGB':
            style_temp= style_temp.convert('RGB')

        OutputPath = output_folder / '{:s}-{:s}_{:s}_{:s}{:s}'.format(
                content_vid_pa.stem,style_img_pa.stem, str(level), str(int(ColorPresrv)),Out_Extension)

        io_writer = imageio.get_writer(OutputPath, mode='I', fps=VID_fps)

        while(True):
            styleIMG = s_transformation(style_temp)
            if styleIMG.size()[0] >3:
                styleIMG = styleIMG[ :3, :, : ]

            r, content_temp = contentVID.read()
            if not r:
                break

            contentIMG = c_transformation(Image.fromarray(content_temp))

            if ColorPresrv:
                styleIMG = color_prev(styleIMG, contentIMG)

            contentIMG = contentIMG.to(device).unsqueeze(0)
            styleIMG = styleIMG.to(device).unsqueeze(0)

            with torch.no_grad():
                outputIMG = StyleTransfer(contentIMG, styleIMG, vgg_m, decoder_m, level)

            outputIMG = outputIMG.cpu()
            outputIMG = outputIMG.squeeze(0)
            outputIMG = np.array(outputIMG)*255
            outputIMG = np.transpose(outputIMG, (1,2,0))

            outputIMG = cv2.resize(outputIMG, (VID_width, VID_height), interpolation=cv2.INTER_CUBIC)

            io_writer.append_data(np.array(outputIMG))
            iter_tq.update(1)

        contentVID.release()


    return str(OutputPath)
