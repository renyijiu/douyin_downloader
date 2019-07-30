# -*- coding: utf-8 -*-

from PIL import Image
import math
import os


def resize_image(origin_img, optimize_img, threshold):
    """
    shrink image by size
    :param origin_img:
    :param optimize_img:
    :param threshold:
    :return:
    """
    file_size = os.path.getsize(origin_img)
    with Image.open(origin_img) as im:
        if file_size > threshold:
            width, height = im.size

            if width >= height:
                new_width = int(math.sqrt(threshold / 2))
                new_height = int(new_width * height * 1.0 / width)
            else:
                new_height = int(math.sqrt(threshold / 2))
                new_width = int(new_height * width * 1.0 / height)

            resized_im = im.resize((new_width, new_height))
            resized_im.save(optimize_img)
        else:
            im.save(optimize_img)


def crop_image(origin_img, optimize_img, x, y, width, height):
    """
    crop imgae by size

    :param origin image
    :param optimize image
    :param x , start point
    :paran y , start point
    :param width, the width of image
    :param height, the height of image
    """
    file_size = os.path.getsize(origin_img)
    with Image.open(origin_img) as im:
        old_width, old_height = im.size
        if old_width < (x + width) or (old_height < y + height):
            im.save(optimize_img)
        else:
            crop_img = im.crop((x, y, width, height))
            crop_img.save(optimize_img)


