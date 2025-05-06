#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Note**

This program is an application of the main module 'audio_and_video_manipulation',
and it relies on the method 'cut_media_files'.
YOU MAY REDISTRIBUTE this program along any other directory,
but keep in mind that the module is designed to work with absolute paths.
"""

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.audio_and_video.audio_and_video_manipulation import cut_media_files

#-------------------#
# Define parameters #
#-------------------#

# Input media #
#-------------#

# Media input can be a list of files or a single file containing file names
MEDIA_INPUT = []
# MEDIA_INPUT = "media_name_containing_file.txt"

# Output media #
#--------------#

# Merged media file #
OUTPUT_FILE_LIST = []
# OUTPUT_FILE_LIST = None

# Starting and ending times #
START_TIME_LIST = ["start", "00:01:28", "00:02:28.345"]
END_TIME_LIST = ["00:05:21", "end", "00:07:56.851"]

# Zero-padding and bit rate factor #
"""The factor is multiplied by 32, so that the bit rate is in range [32, 320] kBps"""
ZERO_PADDING = 1
QUALITY = 4

#------------#
# Operations #
#------------#

cut_media_files(MEDIA_INPUT,
                START_TIME_LIST,
                END_TIME_LIST,
                output_file_list=OUTPUT_FILE_LIST,
                ZERO_PADDING=ZERO_PADDING,
                quality=QUALITY)