# Style Transfer
Project in progress   
C'est de l'art!
## Components
### Web part
- flask (main.py)
- html (adapted from https://github.com/yenchiah/project-website-template)
  - overview
  - gallary
  - create1 with given styles
  - create2 with with customized style images
  - style page for each genre
- css, js and img(logos) in static
- put other images in static/pics, including output, uploads, gallery
### ML part
- AdaIN-Style (adapted from https://github.com/naoto0804/pytorch-AdaIN)  
  (original implentation and explanation https://github.com/xunhuang1995/AdaIN-style) 
- CycleGAN ( adapted from https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix)
### Dataset

## How to use
At home directory, enter  
python main.py

## TODO
- [x] html and css skeleton
- [x] text and pics editing
- [x] nn ready to use
- [x] open html in flask
- [x] handle selections in flask
- [x] upload and display pics
- [x] pass pic through nn via flask
- [ ] cycleGan issues
- [ ] interactive web features
- [ ] migrate selection of existing genres
- [ ] additional features realized by nn
- [ ] tbc...



