import argparse
from pathlib import Path
from tqdm import tqdm

import torch
import torch.nn as nn
import numpy as np
from PIL import Image
import cv2
import imageio
from torchvision import transforms
from torchvision.utils import save_image

import Arbitrary_ST_Pytorch.net as net
from Arbitrary_ST_Pytorch.function import adaptive_instance_normalization, coral

import warnings
warnings.filterwarnings("ignore")

def test_transform(size, crop):
    transform_list = []
    if size != 0:
        transform_list.append(transforms.Resize(size))
    if crop:
        transform_list.append(transforms.CenterCrop(size))
    transform_list.append(transforms.ToTensor())
    transform = transforms.Compose(transform_list)
    return transform


def style_transfer(vgg, decoder, content, style, alpha=1.0,
                   interpolation_weights=None):
    assert (0.0 <= alpha <= 1.0)
    content_f = vgg(content)
    style_f = vgg(style)
    if interpolation_weights:
        _, C, H, W = content_f.size()
        feat = torch.FloatTensor(1, C, H, W).zero_().to(device)
        base_feat = adaptive_instance_normalization(content_f, style_f)
        for i, w in enumerate(interpolation_weights):
            feat = feat + w * base_feat[i:i + 1]
        content_f = content_f[0:1]
    else:
        feat = adaptive_instance_normalization(content_f, style_f)
    feat = feat * alpha + content_f * (1 - alpha)
    return decoder(feat)

def process_img(path, size, crop):

    img_tf = test_transform(size, crop)
    img = Image.open(str(path))
    if img.mode == 'CMYK':
        img= img.convert('RGB')
    img_tensor = img_tf(img)
    if img_tensor.size()[0] >3:
        img_tensor = img_tensor[ :3, :, : ]

    return img_tensor


def video_trans(content_p, style_p, vgg_p='Arbitrary_ST_Pytorch/models/vgg_normalised.pth',
                decoder_p='Arbitrary_ST_Pytorch/models/decoder.pth', preserve_color=False, alpha = 1.0,
                content_size=0, style_size=0, crop=False, save_ext='.mp4', output_p='static/pics/output'):


    device = torch.device("cuda" if torch.cuda.is_available() else "cpu") 

    output_dir = Path(output_p)
    output_dir.mkdir(exist_ok = True, parents = True)

    assert (content_p)
    assert (style_p)
    content_path = Path(content_p)
    style_path = Path(style_p)

    decoder = net.decoder
    vgg = net.vgg
    decoder.eval()
    vgg.eval()

    vgg.load_state_dict(torch.load(vgg_p))
    vgg = nn.Sequential(*list(vgg.children())[:31])
    vgg.to(device)
    decoder.load_state_dict(torch.load(decoder_p))
    decoder.to(device)

    content_transform = test_transform(content_size, crop)
    style_transform = test_transform(style_size, crop)

    #video details
    content_video = cv2.VideoCapture(content_p)
    fps = int(content_video.get(cv2.CAP_PROP_FPS))
    content_video_length = int(content_video.get(cv2.CAP_PROP_FRAME_COUNT))
    output_width = int(content_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    output_height = int(content_video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    assert fps != 0, 'Fps is zero, Please enter proper video path'

    pbar = tqdm(total = content_video_length)

    if style_path.suffix in [".jpg", ".png", ".JPG", ".PNG", ".jpeg", ".JPEG"]:
        output_video_path = output_dir / '{:s}_stylized_{:s}_{:s}_{:s}{:s}'.format(
                content_path.stem, style_path.stem, str(alpha), str(int(preserve_color)), save_ext)
        writer = imageio.get_writer(output_video_path, mode='I', fps=fps)

        style_img = Image.open(style_path)
        if style_img.mode == 'CMYK':
            style_img= style_img.convert('RGB')

        while(True):
            ret, content_img = content_video.read()

            if not ret:
                break

            content = content_transform(Image.fromarray(content_img))
            style = style_transform(style_img)
            if style.size()[0] >3:
                style = style[ :3, :, : ]

            if preserve_color:
                style = coral(style, content)

            style = style.to(device).unsqueeze(0)
            content = content.to(device).unsqueeze(0)
            with torch.no_grad():
                output = style_transfer(vgg, decoder, content, style, alpha)
            output = output.cpu()
            output = output.squeeze(0)
            output = np.array(output)*255
            output = np.transpose(output, (1,2,0))
            output = cv2.resize(output, (output_width, output_height), interpolation=cv2.INTER_CUBIC)

            writer.append_data(np.array(output))
            pbar.update(1)

        content_video.release()


    return str(output_video_path)
