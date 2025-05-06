#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Note**

This program is an application of the main module 'audio_and_video_manipulation',
and it relies on the method 'merge_individual_media_files'.
YOU MAY REDISTRIBUTE this program along any other directory,
but keep in mind that the module is designed to work with absolute paths.
"""

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.audio_and_video.audio_and_video_manipulation import merge_individual_media_files

#-------------------#
# Define parameters #
#-------------------#

# Simple data #
#-------------#

OUTPUT_EXT = "mp4"

# Input media #
#-------------#

# Media input can be a list of files or a single file containing file names
MEDIA_INPUT = []
# MEDIA_INPUT = "media_name_containing_file.txt"

# Output media #
#--------------#

# Merged media file #
OUTPUT_FILE_NAME = f"merged_media_file.{OUTPUT_EXT}"
# OUTPUT_FILE_NAME = None

# Zero-padding and bit rate factor #
"""The factor is multiplied by 32, so that the bit rate is in range [32, 320] kBps"""
ZERO_PADDING = 1
QUALITY = 4

#------------#
# Operations #
#------------#

merge_individual_media_files(MEDIA_INPUT,
                             output_file_name=OUTPUT_FILE_NAME,
                             ZERO_PADDING=ZERO_PADDING,
                             quality=QUALITY)