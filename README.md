# Style Transfer
Project in progress

## Components
### Web part
- flask (main.py)
- html (adapted from https://github.com/yenchiah/project-website-template)
  - overview
  - gallary
  - upload
  - style page for each genre
- css, js and img(logos) in static
- put other images in static/pics
### ML part
- AdaIN-Style (adapted from https://github.com/naoto0804/pytorch-AdaIN)  
  (original implentation and explanation https://github.com/xunhuang1995/AdaIN-style) 
- CycleGAN ( adapted from https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix)
### Dataset

## How to use
at home directory enter  
python main.py

## TODO
- [x] html and css skeleton
- [x] text and pics editing
- [x] nn ready to use
- [x] open html in flask
- [ ] handle selections in flask
- [ ] upload and download pics
- [ ] pass pic through nn via flask
- [ ] interactive web features
- [ ] migrate selection of existing genres
- [ ] additional features realized by nn
- [ ] tbc...



