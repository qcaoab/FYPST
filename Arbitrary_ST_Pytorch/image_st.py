# import
from pathlib import Path
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.utils import save_image

import Arbitrary_ST_Pytorch.NNs as NNs
from Arbitrary_ST_Pytorch.utilities import adain_layer, color_prev


## set device to use, for compatibility, set to cpu as default, can be
## changed through the following line

device = "cpu"
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



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
    if img.mode != 'RGB':
        img= img.convert('RGB')
    img_tensor = img_transf(img)
    if img_tensor.size()[0] > 3:
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


def arbi_trans(content_imgs, style_imgs, ColorPresrv=False, level=1.0,
               addr_vgg='Arbitrary_ST_Pytorch/models/vgg_normalised.pth', addr_decoder='Arbitrary_ST_Pytorch/models/decoder.pth',
               ContentSize=0, StyleSize=0, crop=False, Out_Extension='.jpg', out_folder='static/pics/output'):

    style_length = len(style_imgs)
    bool_interpolate = False

    if style_length > 1:
        bool_interpolate = True

    style_name = ''
    for style_img in style_imgs:

        style_img=Path(style_img)
        style_name = style_name + '-'+ str(style_img.stem)[0:3]
            #flash (style_InterpolateWeights != ''), \
            #    'Please specify interpolation weights'
            #weights = [int(i) for i in style_InterpolateWeights
        #InterpolateWeights = [w / sum(weights) for w in weights]
    InterpolateWeights = np.full(style_length,1/style_length, dtype = float)


    output_director = Path(out_folder)
    output_director.mkdir(exist_ok=True, parents=True)

    decoder_m = NNs.decoder
    decoder_m.eval()
    vgg_m = NNs.vgg
    vgg_m.eval()
    vgg_m.load_state_dict(torch.load(addr_vgg))
    vgg_m = nn.Sequential(*list(vgg_m.children())[:31])

    decoder_m.load_state_dict(torch.load(addr_decoder))
    decoder_m.to(device)

    vgg_m.to(device)

    content_imgs = [Path(content_imgs)]

    for content_img in content_imgs:

        if bool_interpolate:  # This case for interpolating multiple styles
            # steps for color preserve
            temp_content = process_img(content_img, ContentSize, True)
            if ColorPresrv:
                styleIMG = torch.stack([color_prev(process_img(p, StyleSize, True), temp_content) for p in style_imgs])
            else:
                styleIMG = torch.stack([process_img(p, StyleSize, True) for p in style_imgs])
            contentIMG = temp_content.unsqueeze(0).expand_as(styleIMG)

            contentIMG = contentIMG.to(device)
            styleIMG = styleIMG.to(device)

            ## conduct
            with torch.no_grad():
                outputIMG = StyleTransfer(contentIMG, styleIMG, vgg_m, decoder_m, level, InterpolateWeights)

        else:
            for style_img in style_imgs:

                contentIMG = process_img(content_img, ContentSize, crop)
                styleIMG = process_img(style_img, StyleSize, crop)

                if ColorPresrv:
                    styleIMG = color_prev(styleIMG, contentIMG)

                contentIMG = contentIMG.to(device).unsqueeze(0)
                styleIMG = styleIMG.to(device).unsqueeze(0)
                with torch.no_grad():
                    outputIMG = StyleTransfer(contentIMG, styleIMG, vgg_m, decoder_m, level)


        # path
        output_path = output_director / '{:s}-{:s}_{:s}_{:s}{:s}'.format(
                content_img.stem, style_name,  str(level),str(int(ColorPresrv)),Out_Extension)

        #save
        outputIMG = outputIMG.cpu()
        save_image(outputIMG, str(output_path))

    #return path
    return str(output_path)
