import cv2
from PIL import Image
import numpy as np
import os
from PIL import Image, ImageFilter



def marking(input_image_path):
    base_image = Image.open(input_image_path).convert('RGBA')
    watermark = Image.open('..\watermark\img\mark.png').convert('RGBA')
    width, height = base_image.size
    print(height)
    watermark=watermark.resize((width,int(height/3)))
    transparent = Image.new('RGBA', (width, height), (0,0,0,0))
    transparent.paste(base_image, (0,0))
    transparent.paste(watermark, (0,int(height/2)),watermark)
    transparent.save('../watermark/img/temp.png')

    img=cv2.imread('../watermark/img/temp.png')
    h_img , w_img , i =img.shape
    footer = cv2.imread('../watermark/img/footer.png')
    footer=cv2.resize(footer,(w_img,footer.shape[0]))

    header=cv2.imread('../watermark/img/header.png')
    header=cv2.resize(header,(w_img,header.shape[0]))
    
    v_img = cv2.vconcat([img, footer])
    v_img=cv2.vconcat([header,v_img])
    cv2.imwrite('../watermark/img/temp.png', v_img)
    im=Image.open('../watermark/img/temp.png')
    im.save(input_image_path)

