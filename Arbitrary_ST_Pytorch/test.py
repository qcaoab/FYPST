import argparse
from pathlib import Path
import os
import torch
import torch.nn as nn
from PIL import Image
import numpy as np
from torchvision import transforms
from torchvision.utils import save_image

import Arbitrary_ST_Pytorch.net as net
from Arbitrary_ST_Pytorch.function import adaptive_instance_normalization, coral


def test_transform(size, crop):
    transform_list = []
    if size != 0:
        transform_list.append(transforms.Resize(size))
    if crop:
        transform_list.append(transforms.CenterCrop(size))
        
    #transform_list.append(transforms.ToPILImage())
    transform_list.append(transforms.ToTensor())
    transform = transforms.Compose(transform_list)
    return transform


def style_transfer(vgg, decoder, content, style, alpha=1.0,
                   interpolation_weights=None):
    assert (0.0 <= alpha <= 1.0)
    content_f = vgg(content)
    style_f = vgg(style)
    if interpolation_weights is not None:
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


parser = argparse.ArgumentParser()
# Basic options
parser.add_argument('--content', type=str,
                    help='File path to the content image')
parser.add_argument('--content_dir', type=str,
                    help='Directory path to a batch of content images')
parser.add_argument('--style', type=str,
                    help='File path to the style image, or multiple style \
                    images separated by commas if you want to do style \
                    interpolation or spatial control')
parser.add_argument('--style_dir', type=str,
                    help='Directory path to a batch of style images')
parser.add_argument('--vgg', type=str, default='models/vgg_normalised.pth')
parser.add_argument('--decoder', type=str, default='models/decoder.pth')

# Additional options
parser.add_argument('--content_size', type=int, default=512,
                    help='New (minimum) size for the content image, \
                    keeping the original size if set to 0')
parser.add_argument('--style_size', type=int, default=512,
                    help='New (minimum) size for the style image, \
                    keeping the original size if set to 0')
parser.add_argument('--crop', action='store_true',
                    help='do center crop to create squared image')
parser.add_argument('--save_ext', default='.jpg',
                    help='The extension name of the output image')
parser.add_argument('--output', type=str, default='output',
                    help='Directory to save the output image(s)')

# Advanced options
parser.add_argument('--preserve_color', action='store_true',
                    help='If specified, preserve color of the content image')
parser.add_argument('--alpha', type=float, default=1.0,
                    help='The weight that controls the degree of \
                             stylization. Should be between 0 and 1')
parser.add_argument(
    '--style_interpolation_weights', type=str, default='',
    help='The weight for blending the style of multiple style images')


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

'''
args = parser.parse_args()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

output_dir = Path(args.output)
output_dir.mkdir(exist_ok=True, parents=True)

# Either --content or --contentDir should be given.
assert (args.content or args.content_dir)
if args.content:
    content_paths = [Path(args.content)]
else:
    content_dir = Path(args.content_dir)
    content_paths = [f for f in content_dir.glob('*')]

# Either --style or --styleDir should be given.
assert (args.style or args.style_dir)
if args.style:
    style_paths = args.style.split(',')
    if len(style_paths) == 1:
        style_paths = [Path(args.style)]
    else:
        do_interpolation = True
        assert (args.style_interpolation_weights != ''), \
            'Please specify interpolation weights'
        weights = [int(i) for i in args.style_interpolation_weights.split(',')]
        interpolation_weights = [w / sum(weights) for w in weights]
else:
    style_dir = Path(args.style_dir)
    style_paths = [f for f in style_dir.glob('*')]

decoder = net.decoder
vgg = net.vgg

decoder.eval()
vgg.eval()

decoder.load_state_dict(torch.load(args.decoder))
vgg.load_state_dict(torch.load(args.vgg))
vgg = nn.Sequential(*list(vgg.children())[:31])

vgg.to(device)
decoder.to(device)

content_tf = test_transform(args.content_size, args.crop)
style_tf = test_transform(args.style_size, args.crop)

for content_path in content_paths:
    if do_interpolation:  # one content image, N style image
        style = torch.stack([style_tf(Image.open(str(p))) for p in style_paths])
        content = content_tf(Image.open(str(content_path))) \
            .unsqueeze(0).expand_as(style)
        style = style.to(device)
        content = content.to(device)
        with torch.no_grad():
            output = style_transfer(vgg, decoder, content, style,
                                    args.alpha, interpolation_weights)
        output = output.cpu()
        output_name = output_dir / '{:s}_interpolation{:s}'.format(
            content_path.stem, args.save_ext)
        save_image(output, str(output_name))

    else:  # process one content and one style
        for style_path in style_paths:
            content = content_tf(Image.open(str(content_path)))
            style = style_tf(Image.open(str(style_path)))
            if args.preserve_color:
                style = coral(style, content)
            style = style.to(device).unsqueeze(0)
            content = content.to(device).unsqueeze(0)
            with torch.no_grad():
                output = style_transfer(vgg, decoder, content, style,
                                        args.alpha)
            output = output.cpu()

            output_name = output_dir / '{:s}_stylized_{:s}{:s}'.format(
                content_path.stem, style_path.stem, args.save_ext)
            save_image(output, str(output_name))
            
''' 
def process_img(path, size, crop):
    
    img_tf = test_transform(size, crop)
    img = Image.open(str(path))
    if img.mode == 'CMYK':
        img= img.convert('RGB')
    img_tensor = img_tf(img)
    if img_tensor.size()[0] >3:
        img_tensor = img_tensor[ :3, :, : ]
        
    return img_tensor

def arbi_trans(content_imgs, style_imgs, preserve_color = False, alpha = 1.0, 
               a_vgg= 'Arbitrary_ST_Pytorch/models/vgg_normalised.pth', a_decoder ='Arbitrary_ST_Pytorch/models/decoder.pth', 
               content_size = 512, style_size = 512, crop = False, save_ext = '.jpg', output = 'static/pics/output'):
    do_interpolation = False
    style_length = len(style_imgs)
    if style_length > 1:
        do_interpolation = True
        
    style_name = ''
    for style_img in style_imgs:
        
        style_img=Path(style_img)
        style_name = style_name + '-'+ str(style_img.stem)[0:3]
            #flash (args.style_interpolation_weights != ''), \
            #    'Please specify interpolation weights'
            #weights = [int(i) for i in style_interpolation_weights
        #interpolation_weights = [w / sum(weights) for w in weights]
        interpolation_weights = np.full(style_length,1/style_length, dtype = float)
       
   
    output_dir = Path(output)
    output_dir.mkdir(exist_ok=True, parents=True)
    decoder = net.decoder
    vgg = net.vgg
    
    decoder.eval()
    vgg.eval()
    
    decoder.load_state_dict(torch.load(a_decoder))
    vgg.load_state_dict(torch.load(a_vgg))
    vgg = nn.Sequential(*list(vgg.children())[:31])
    
    vgg.to(device)
    decoder.to(device)
    content_imgs = [Path(content_imgs)]
    
    for content_img in content_imgs:
        
            
        if do_interpolation:  # one content image, N style image
            style = torch.stack([process_img(p,style_size, True) for p in style_imgs])
            content = process_img(content_img, content_size, True).unsqueeze(0).expand_as(style)
            style = style.to(device)
            content = content.to(device)
            with torch.no_grad():
                output = style_transfer(vgg, decoder, content, style, alpha, interpolation_weights)
        
        else:
            for style_img in style_imgs:
                '''
                content_tf = test_transform(content_size, crop)
                style_tf = test_transform(style_size, crop)
                content = content_tf(Image.open(str(content_img)))
                
                style = style_tf(Image.open(str(style_img)))
                '''
                content = process_img(content_img, content_size, crop)
                style = process_img(style_img, style_size, crop)
                if preserve_color:
                    style = coral(style, content)
                style = style.to(device).unsqueeze(0)
                content = content.to(device).unsqueeze(0)
                with torch.no_grad():
                    output = style_transfer(vgg, decoder, content, style, alpha)
               
        
     
        output = output.cpu()
        output_name = output_dir / '{:s}-{:s}_{:s}_{:s}{:s}'.format(
                content_img.stem, style_name,  str(alpha), str(int(preserve_color)),save_ext)
   
        save_image(output, str(output_name))
            
    return str(output_name)