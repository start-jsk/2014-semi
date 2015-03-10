#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
This script is to match objects with sift features which is extracted by
jsk_2014_picking_challenge/scripts/extract_sift_from_objdata.py.

Usage
-----

    $ roslaunch jsk_2014_picking_challenge sift_matcher_usbcamera.launch
    $ rosrun jsk_2014_picking_challenge sift_matcher.py
    $ rosservice call /semi/sift_matcher \
        "{objects: ['oreo_mega_stuf', 'safety_works_safety_glasses']}"

"""
from __future__ import print_function, division
from future_builtins import zip
import os
import gzip
import cPickle as pickle

import numpy as np
import yaml

import rospy
from posedetection_msgs.msg import ImageFeature0D
from jsk_2014_picking_challenge.srv import ObjectMatch, ObjectMatchResponse

from sift_matcher_oneimg import SiftMatcherOneImg


class SiftMatcher(object):
    def __init__(self):
        # load object list
        dirname = os.path.dirname(os.path.abspath(__file__))
        ymlfile = os.path.join(dirname, '../data/object_list.yml')
        self.object_list = yaml.load(open(ymlfile))
        self.siftdata_cache = {}

        rospy.Service('/semi/sift_matcher', ObjectMatch, self._cb_matcher)
        rospy.wait_for_message('/ImageFeature0D', ImageFeature0D)
        sub_imgfeature = rospy.Subscriber('/ImageFeature0D', ImageFeature0D,
                                          self._cb_imgfeature)

    def _cb_matcher(self, req):
        """Callback function for sift match request"""
        probs = self._get_object_probability(req.objects)
        return ObjectMatchResponse(probabilities=probs)

    def _cb_imgfeature(self, msg):
        """Callback function of Subscribers to listen ImageFeature0D"""
        self.query_features = msg.features

    def _get_object_probability(self, obj_names):
        """Get object match probabilities"""
        query_features = self.query_features
        n_matches = []
        siftdata_set = self._handle_siftdata_cache(obj_names)
        for obj_name, siftdata in zip(obj_names, siftdata_set):
            if obj_name not in self.object_list:
                n_matches.append(0)
                continue
            if siftdata is None:  # does not exists data file
                n_matches.append(0)
                continue
            # find best match in train features
            rospy.loginfo('searching matches: {}'.format(obj_name))
            train_matches = []
            for train_des in siftdata['descriptors']:
                matches = SiftMatcherOneImg.find_match(
                    query_features.descriptors, train_des)
                train_matches.append(len(matches))
            n_matches.append(max(train_matches))  # best match

        n_matches = np.array(n_matches)
        rospy.loginfo('n_matches: {}'.format(n_matches))
        if n_matches.sum() == 0:
            return n_matches
        else:
            return n_matches / n_matches.sum()

    def _handle_siftdata_cache(self, obj_names):
        """Sift data cache handler
        if same obj_names set: don't update, else: update
        """
        siftdata_cache = self.siftdata_cache
        if set(obj_names) != set(siftdata_cache.keys()):
            siftdata_cache = {}  # reset cache
        for obj_name in obj_names:
            if obj_name in siftdata_cache:
                siftdata = siftdata_cache[obj_name]
            else:
                siftdata = self.load_siftdata(obj_name)
            yield siftdata
            # set cache
            if siftdata is None:
                continue
            if len(siftdata_cache) > 3:
                # free cache data to avoid becoming too big
                del siftdata_cache[np.random.choice(siftdata_cache.keys())]
                siftdata_cache[obj_name] = siftdata
            self.siftdata_cache = siftdata_cache

    @staticmethod
    def load_siftdata(obj_name):
        """Load sift data from pkl file"""
        dirname = os.path.dirname(os.path.abspath('__file__'))
        datafile = os.path.join(dirname, '../data/siftdata',
            obj_name+'.pkl.gz')
        if not os.path.exists(datafile):
            return  # does not exists
        rospy.loginfo('Loading siftdata: {obj}'.format(obj=obj_name))
        with gzip.open(datafile, 'rb') as f:
            return pickle.load(f)


def main():
    rospy.init_node('sift_matcher')
    sm = SiftMatcher()
    rospy.spin()


if __name__ == '__main__':
    main()

