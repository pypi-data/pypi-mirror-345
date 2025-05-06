#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RTSP server util functions.
"""

from wotpy.wot.interaction import Property


def inject_video_property(exposed_thing):
    """Creates and adds a new video property
    to a specific Thing."""

    thing = exposed_thing.thing
    proprty = Property(thing=thing, name="video", type="null")
    thing.add_interaction(proprty)
