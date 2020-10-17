#!/usr/bin/env python

import argparse
import numpy as np
import os
import os.path as osp
import scipy.misc
import scipy.ndimage
import shutil


def main(data_dir, visualize, occluded):
    objectnames = os.listdir(data_dir)
    # copy objects
    for objectname in objectnames:
        print('object: {}'.format(objectname))
        recog_dir = osp.join(data_dir, objectname, 'recognition')
        result_dir = osp.join(data_dir, objectname, 'result')
        if occluded:
            bg_label = -1
        else:
            bg_label = 0
        for d in os.listdir(recog_dir):
            save_dir = osp.join(data_dir, objectname, d)
            if osp.exists(osp.join(result_dir, d)):
                if not osp.exists(save_dir):
                    os.makedirs(save_dir)
                    for f in os.listdir(osp.join(recog_dir, d)):
                        shutil.copy(osp.join(recog_dir, d, f), save_dir)
                    for f in os.listdir(osp.join(result_dir, d)):
                        shutil.copy(osp.join(result_dir, d, f), save_dir)
                imgpath = osp.join(save_dir, 'input_image.png')
                input_maskpath = osp.join(save_dir, 'input_mask.png')
                img = scipy.misc.imread(imgpath, mode='RGB')
                input_mask = scipy.misc.imread(input_maskpath, mode='L')
                if occluded:
                    label = np.load(
                        osp.join(save_dir, 'vis_cls_label.npz'))['arr_0']
                else:
                    label = scipy.misc.imread(osp.join(save_dir, 'label.png'))
                img[input_mask == 0] = np.array([0, 0, 0])
                img[label == bg_label] = np.array([0, 0, 0])
                mask = generate_mask(img, visualize)
                maskpath = osp.join(save_dir, 'object_mask.png')
                scipy.misc.imsave(maskpath, mask)


def generate_mask(img, visualize=False):
    mask = img.sum(axis=2) > 0
    if visualize:
        negative_mask = ~mask
        img_viz = img[:]
        img_viz[negative_mask] = np.array([255, 0, 0])
        scipy.misc.imshow(img_viz)
    mask = mask.astype(np.uint32) * 255
    return mask


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--visualize', action='store_true')
    parser.add_argument('--occluded', action='store_true')
    parser.add_argument('data_dir', metavar='data-dir', default=None)
    args = parser.parse_args()

    main(args.data_dir, args.visualize, args.occluded)
