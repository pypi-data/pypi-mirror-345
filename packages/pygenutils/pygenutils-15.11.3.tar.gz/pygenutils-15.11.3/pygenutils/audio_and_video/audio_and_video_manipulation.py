#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import os

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_caller_args
from pygenutils.operative_systems.os_operations import run_system_command, exit_info
from pygenutils.strings.text_formatters import format_string
from pygenutils.time_handling.time_formatters import parse_time_string

#------------------#
# Define functions #
#------------------#
            
# Merge files #
#-------------#

# %% 

def merge_media_files(audio_file_list_or_file, 
                      video_file_list_or_file, 
                      output_file_list=None, 
                      zero_padding=1, 
                      quality=1):
    """
    Merges audio and video files into a single output file for each pair.

    Parameters
    ----------
    audio_file_list_or_file : list or str
        A list of audio file paths or a path to a text file containing audio file names.
    video_file_list_or_file : list or str
        A list of video file paths or a path to a text file containing video file names.
    output_file_list : list, optional
        A list of output file names. If not provided, default names will be generated.
    zero_padding : int, optional
        Zero-padding to apply to the output file numbers. 
        Must be greater than or equal to 1.
    quality : int, optional
        The quality level for the merged output (1=lowest, 10=highest). Default is 1.

    Raises
    ------
    ValueError
        If the lengths of the audio and video file lists do not match,
        or if any parameter is invalid.

    Returns
    -------
    None
    """
    
    # Helper functions #
    #-#-#-#-#-#-#-#-#-#-
    
    # Get all arguments #
    param_keys = get_caller_args()
    zero_pad_pos = param_keys.index("zero_padding")

    # Helper function to load file list from external file if necessary
    def load_file_list(file_or_list):
        if isinstance(file_or_list, list):
            return file_or_list
        try:
            with open(file_or_list) as f:
                return f.read().splitlines()
        except Exception as e:
            raise ValueError(f"Error reading file '{file_or_list}': {e}")
            
    # File existence
    def validate_files(file_list, list_name):
        for file in file_list:
            if not os.path.exists(file):
                raise FileNotFoundError(f"{list_name}: '{file}' not found.")
    
    # Load the file lists, automatically detecting whether input is file or list
    audio_file_list = load_file_list(audio_file_list_or_file)
    video_file_list = load_file_list(video_file_list_or_file)

    # Validations #
    #-#-#-#-#-#-#-#
    
    # Validate lists are of the same length
    if len(video_file_list) != len(audio_file_list):
        raise ValueError("Input audio and video file lists must have the same length.")
        
    # Output file list length
    if output_file_list is not None:
        if len(output_file_list) != len(video_file_list):
            raise ValueError("Output file name list must match the length of input lists.")
        
    # Zero-padding
    if not isinstance(zero_padding, int) or zero_padding < 1:
        raise ValueError(f"'zero_padding' (number {zero_pad_pos}) "
                         f"must be an integer >= 1, got {zero_padding}.")
        
    # Quality input 
    if not isinstance(quality, int) or not (1 <= quality <= 10):
        raise ValueError("Quality must be an integer between 1 and 10.")
    
    # File existence validation
    validate_files(video_file_list, "Video file list (arg number 0)")
    validate_files(audio_file_list, "Audio file list (arg number 1)")
    
    # Operations #
    #-#-#-#-#-#-#-
    
    # Generate default output file names if not provided
    if output_file_list is None:
        output_file_list = [
            f"merged_video_{str(i + 1).zfill(zero_padding)}"
            for i in range(len(video_file_list))
        ]
    
    # Try multiple ffmpeg merge template strings with different variations to handle errors
    template_strings_to_try = []
    for audio_file, video_file, output_file in zip(audio_file_list,
                                                   video_file_list,
                                                   output_file_list):
        # Create a list of ffmpeg template strings to try
        merge_template = f"ffmpeg -i {audio_file} -i {video_file} "\
                         f"-c:v copy -c:a aac -b:a {quality*32}k {output_file}"
        template_strings_to_try.append(merge_template)

        # Additional ffmpeg template string variations for error handling
        template_strings_to_try.append(f"ffmpeg -i {audio_file} -i {video_file} "
                                       f"-c:v libx264 -b:a {quality*32}k "
                                       f"-preset fast {output_file}")
        template_strings_to_try.append(f"ffmpeg -i {audio_file} -i {video_file} "
                                       f"-c:v libx265 -b:a {quality*32}k -c:a copy {output_file}")

    # Try each command and pass on errors
    for merge_template in template_strings_to_try:
        try:
            process_exit_info = run_system_command(format_string(merge_template))
            exit_info(process_exit_info)
            break  # Exit loop if successful
        except RuntimeError:
            pass  # Continue with the next ffmpeg command if there's an error

# %%
def merge_individual_media_files(input_file_list_or_file,
                                 safe=True, 
                                 output_file_name=None,
                                 quality=1):
    """
    Merges either audio or video files into a single output file.

    Parameters
    ----------
    input_file_list_or_file : list or str
        A list of file paths (either audio or video) or a path to a text file 
        containing file names.
    safe : bool, optional
        If True, ffmpeg runs in safe mode to prevent unsafe file operations.
        Default is True.
    output_file_name : str, optional
        The name of the output file. If not provided, a default name will be used.
    quality : int, optional
        The quality level for the merged output (1=lowest, 10=highest). Default is 1.

    Raises
    ------
    ValueError
        If both audio and video files are provided in the input,
        or if any parameter is invalid.

    Returns
    -------
    None
    """
    
    # Helper functions #
    #------------------#
    
    # Helper function to load file list from external file if necessary
    def load_file_list(file_or_list):
        if isinstance(file_or_list, list):
            return file_or_list
        try:
            with open(file_or_list) as f:
                return f.read().splitlines()
        except Exception as e:
            raise ValueError(f"Error reading file '{file_or_list}': {e}")
    
    # Automatically detect file type
    def is_audio_file(file):
        return file.endswith(tuple(COMMON_AUDIO_FORMATS))

    def is_video_file(file):
        return file.endswith(tuple(COMMON_VIDEO_FORMATS))
    
    # Validations #
    #-------------#
    
    # Quality input 
    if not isinstance(quality, int) or not (1 <= quality <= 10):
        raise ValueError("Quality must be an integer between 1 and 10.")

    # Load the file list, automatically detecting whether input is file or list
    file_list = load_file_list(input_file_list_or_file)

    # Check if all files are either audio or video, not both #
    audio_files = [file for file in file_list if is_audio_file(file)]
    video_files = [file for file in file_list if is_video_file(file)]
    
    if audio_files and video_files:
        raise ValueError("Input list contains both audio and video files. "
                         "Only one type is allowed.")
    
    # Operations #
    #------------#
    
    # Generate default output file names if not provided #
    if not output_file_name:
        output_file_name = "out_file"
    
    # Attempt multiple ffmpeg template strings to handle potential errors
    template_strings_to_try = []
    input_str = '|'.join(file_list)
    template_strings_to_try.append(f"ffmpeg -i 'concat:{input_str}' -b:a {quality*32}k "
                           f"-c copy {output_file_name}.mp4")

    # Add variations of ffmpeg commands in case errors occur
    template_strings_to_try.append(f"ffmpeg -safe {int(safe)} -f concat -i {input_file_list_or_file} "
                           f"-c:v libx264 -b:a {quality*32}k -preset slow {output_file_name}.mp4")
    template_strings_to_try.append(f"ffmpeg -i 'concat:{input_str}' -b:a {quality*32}k "
                           f"-c:v libx265 -c:a copy {output_file_name}.mp4")

    # Try each command until one succeeds or all fail
    for merge_template in template_strings_to_try:
        try:
            process_exit_info = run_system_command(format_string(merge_template))
            exit_info(process_exit_info)
            break  # Exit loop if successful
        except RuntimeError:
            pass  # Continue with the next ffmpeg command if there's an error

# %%

# Cut files #
#-----------#

def cut_media_files(input_file_list_or_file, 
                    start_time_list,
                    end_time_list, 
                    output_file_list=None,
                    zero_padding=1,
                    quality=1):
    """
    Cuts media files (audio or video) based on specified start and end times.

    Parameters
    ----------
    input_file_list_or_file : list or str
        A list of media file paths or a path to a text file containing file names.
    start_time_list : str or list of str
        The start time in the format '%H:%M:%S' or '%H:%M:%S.%f'. 
        If any set to 'start', cutting starts from the beginning.
    start_time_list : str or list of str
        The end time in the format '%H:%M:%S' or '%H:%M:%S.%f'.
        If any set to 'end', cutting proceeds until the end of the file.
    output_file_list : list, optional
        A list of output file names. If not provided, default names will be generated.
    zero_padding : int, optional
        Zero-padding to apply to the output file numbers. 
        Must be greater than or equal to 1.
    quality : int, optional
        The quality level for the cut output (1=lowest, 10=highest). Default is 1.

    Raises
    ------
    RuntimeError
        If a file is passed as an input argument, when for some reason 
        Python is unable to read it.
    ValueError
        - If any start and end is set to default values
        - If any parameter is invalid.
        - If the lengths of the start and end time lists do not match,

    Returns
    -------
    None
    
    Notes
    -----
    For arg 'input_file_list_or_file', note that if a single file is passed, 
    it must be enclosed in a list, otherwise the function will interpret it
    as being a file, which Python will almost surely unable to read it.
    """
    
    # Helper functions #
    #------------------#
    
    def validate_time_format(time_str):
        try:
            for time_fmt in TIME_FMT_STR_LIST:
                parse_time_string(time_str, time_fmt)
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}. "
                             f"Expected one from {TIME_FMT_STR_LIST}")

    # Helper function to load file list from external file if necessary
    def load_file_list(file_or_list):
        if isinstance(file_or_list, list):
            return file_or_list
        try:
            with open(file_or_list) as f:
                return f.read().splitlines()
        except Exception as e:
            raise RuntimeError(f"Error reading file '{file_or_list}': {e}")
            
    # Validations #
    #-------------#
    
    # Load the file list, automatically detecting whether input is file or list
    file_list = load_file_list(input_file_list_or_file)

    # Validate lists of start and end times are of the same length
    if len(start_time_list) != len(end_time_list):
        raise ValueError("Start and end time lists must have the same length.")

    # Validate start and end times
    for start_time, end_time in zip(start_time_list, end_time_list):
        if (start_time, end_time) == ('start', 'end'):
            raise ValueError("Both start and end cannot be default values.")
        else:
            if start_time != 'start':
                validate_time_format(start_time)
            if end_time != 'end':
                validate_time_format(end_time)

    # Zero-padding
    if not isinstance(zero_padding, int) or zero_padding < 1:
        raise ValueError(f"zero_padding must be an integer >= 1, got {zero_padding}.")
        
    # Quality input 
    if not isinstance(quality, int) or not (1 <= quality <= 10):
        raise ValueError("Quality must be an integer between 1 and 10.")
    
        
    # Operations #
    #------------#
    
    # If output file list is not provided, create default names
    if output_file_list is None:
        output_file_list = [f"cut_file_{str(i + 1).zfill(zero_padding)}.mp4" 
                            for i in range(len(file_list))]
    
    # Try multiple ffmpeg cut template strings with different variations to handle errors
    template_strings_to_try = []
    for input_file, output_file, start_time, end_time in zip(file_list, 
                                                             output_file_list,
                                                             start_time_list,
                                                             end_time_list):
        cut_template = f"ffmpeg -i {input_file}"
        if start_time != 'start':
            cut_template += f" -ss {start_time}"
        if end_time != 'end':
            cut_template += f" -to {end_time}"
        cut_template += f" -b:a {quality*32}k -c copy {output_file}"
    
        template_strings_to_try.append(cut_template)
        template_strings_to_try.append(f"ffmpeg -i {input_file} -b:a {quality*32}k "
                                       f"-c:v libx264 -preset medium {output_file}")

    # Try each command and pass on errors
    for cut_template in template_strings_to_try:
        try:
            process_exit_info = run_system_command(format_string(cut_template))
            exit_info(process_exit_info)
            break  # Exit loop if successful
        except RuntimeError:
            pass  # Continue with the next ffmpeg command if there's an error


# %%

#--------------------------#
# Parameters and constants #
#--------------------------#

# Supported options #
#-------------------#

# Time format strings #
TIME_FMT_STR_LIST = ['%H:%M:%S', '%H:%M:%S.%f']

# Common audio and video formats #
COMMON_AUDIO_FORMATS = ('.mp3', '.aac', '.wav')
COMMON_VIDEO_FORMATS = ('.mp4', '.avi', '.mkv')
