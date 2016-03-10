#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path as osp

import yaml
import rospkg
import json

import cv2
import numpy as np

import jsk_apc2015_common
import rospkg

rp = rospkg.RosPack()
PKG = 'jsk_apc2016_common'
PKG_PATH = rp.get_path(PKG)
OLD_PKG = 'jsk_apc2015_common'##Delete this path and change all OLD_PKG_PATH to PKG_PATH after new objects for apc2016 arrive from Amazon
OLD_PKG_PATH = rp.get_path(OLD_PKG)

def get_object_data():
    fname = osp.join(rp.get_path(PKG), 'data/object_data.yaml')
    data = yaml.load(open(fname))
    return data

def load_stow_json(json_file):
    json_data = json.load(open(json_file))
    bin_contents = {}
    for bin, item in json_data['bin_contents'].items():
        bin = bin[len('bin_'):].lower()
        bin_contents[bin] = item
    work_order = []
    for contents in json_data['work_order']:
        work_order.append(contents)
    return bin_contents, work_order

def visualize_stow_json(json_file):
    from jsk_apc2015_common.util import rescale
    bin_contents, work_order = load_stow_json(json_file)
    kiva_pod_img = jsk_apc2015_common.visualize_json(json_file,bin_contents)
    tote_img = cv2.imread(osp.join(PKG_PATH, 'models/tote/image.jpg'))
    object_list = jsk_apc2015_common.get_object_list()
    object_imgs = {}
    for obj in object_list:
        img_path = osp.join(OLD_PKG_PATH, 'models/{obj}/image.jpg'.format(obj=obj))
        img = cv2.imread(img_path)
        h, w = img.shape[:2]
        if h > w:
            img = np.rollaxis(img, 1)
        object_imgs[obj] = img

  # draw objects in tote
    tote_region = [[190,230],[1080,790]]
    region_h = tote_region[1][1] - tote_region[0][1]
    region_w = tote_region[1][0] - tote_region[0][0]
    max_obj_h,max_obj_w = region_h / 3, region_w / 4
    tote_x_min,tote_y_min = tote_region[0][0], tote_region[0][1]
    x_min, y_min = tote_x_min, tote_y_min
    for obj in work_order:
        obj_img = object_imgs[obj]
        scale_h = 1. * max_obj_h / obj_img.shape[0]
        scale_w = 1. * max_obj_w / obj_img.shape[1]
        scale = min([scale_h, scale_w])
        obj_img = rescale(obj_img, scale)
        obj_h, obj_w = obj_img.shape[:2]
        x_max, y_max = x_min + obj_w, y_min + obj_h
        tote_img[y_min:y_max, x_min:x_max] = obj_img
        x_min += max_obj_w
        if x_max >= region_w :
            x_min = tote_x_min
            y_min += max_obj_h

    # merge two images
    kiva_w,kiva_h = kiva_pod_img.shape[1],kiva_pod_img.shape[0]
    tote_w,tote_h = tote_img.shape[1],tote_img.shape[0]
    tote_img = cv2.resize(tote_img,(kiva_w,tote_h*kiva_w//tote_w))
    dest = np.concatenate((kiva_pod_img,tote_img),axis=0)
    return dest
