#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import os

#------------------------#
# Import project modules # 
#------------------------#

from paramlib.global_parameters import FILESYSTEM_CONTEXT_MODULES
from pygenutils.strings.string_handler import get_type_str
from pygenutils.strings.text_formatters import format_string

# %%

#------------------#
# Define functions #
#------------------#

# Main method #
#-------------#

def run_system_command(command,
                       module="subprocess", 
                       _class="run",
                       capture_output=False,
                       return_output_name=False,
                       encoding="utf-8",
                       shell=True):
   
    """
    Execute a system command using the specified module and class combination.

    This method runs a command using either the 'os' or 'subprocess' module,
    depending on the provided parameters. It returns relevant output attributes
    like stdout, stderr, stdin, and the return code, depending on the system 
    command execution method.

    Parameters
    ----------
    command : str or list
        The command to execute, either as a string (for 'os' and 'subprocess')
        or a list of arguments (only for 'subprocess' module).
    module : str, optional, default: "subprocess"
        The module to use for executing the command.
        Valid options are 'os' or 'subprocess'.
    _class : str, optional, default "run"
        The class within the module to use.
        Valid options are:
        - 'os': {'system', 'popen'}.
        - 'subprocess': {'Popen', 'call', 'run'}.
    capture_output : bool, optional, default: False
        If True, captures the command's stdout and stderr.
    return_output_name : bool, optional, default: False
        If True, returns the file descriptors' names (if applicable) for stdin,
        stdout, and stderr.
    encoding : str, optional, default 'utf-8'
        The encoding to use when decoding stdout and stderr. 
        If None, no decoding is applied.
    shell : bool, optional
        Only applicable if (module, _class) == ("subprocess", "run").
        If True, the command will be executed through the shell. Default is True        
        
    Raises
    ------
    ValueError
        If the combo (module, _class) is neither of the allowed ones in 'command_helpers' 

    Returns
    -------
    result : dict
        A dictionary containing relevant output characteristics such as:
        - 'stdout': Captured standard output (if applicable)
        - 'stderr': Captured standard error (if applicable)
        - 'stdin': The name of the input stream (if applicable)
        - 'return_code': The exit code of the command
        - 'errors': Any errors encountered during command execution (if applicable)
    """

    
    # Validate module and class
    if (module, _class) not in COMMAND_HELPERS:
        raise ValueError(f"Unsupported module-class combo '{module}'-'{_class}'.")
    
    # Get the appropriate helper function
    helper_func = COMMAND_HELPERS.get((module, _class))
    
    # Run the command via the helper
    result = helper_func(command, capture_output=capture_output, encoding=encoding, shell=shell)
    
    return result


# Helpers #
#---------#

def os_system_helper(command, capture_output):
    """
    Helper function to execute a command using os.system.

    Parameters
    ----------
    command : str
        The system command to execute.
    capture_output : bool, optional
        Cannot capture output with os.system. This argument raises a ValueError 
        if set to True.

    Returns:
    --------
    dict
        A dictionary containing:
        - 'return_code': The exit code of the command.
    """
    
    # Validations #
    #-------------#
    
    # Command and class #
    if not isinstance(command, str):
        obj_type = get_type_str(command)
        raise TypeError(f"Expected str, not '{obj_type}'.")
     
    # Output capturing #
    if capture_output:
        raise ValueError("os.system cannot capture output.")
    
    # Operations #
    #------------#
    
    # Execute the command
    exit_code = os.system(command)
    
    # Return the exit status
    return dict(return_code=exit_code)


def os_popen_helper(command, capture_output):
    """
    Helper function to execute a command using os.popen.

    Parameters
    ----------
    command : str
        The system command to execute.
    capture_output : bool, optional
        Must be True for os.popen to capture output.

    Returns:
    --------
    dict
        A dictionary containing:
        - 'stdout': The captured standard output.
        - 'return_code': None, as os.popen does not provide a return code.
    """
    
    # Validations #
    #-------------#
    
    # Command and class #
    if not isinstance(command, str):
        obj_type = get_type_str(command)
        raise TypeError(f"Expected str, not '{obj_type}'.")
        
    # Output capturing #
    if not capture_output:
        raise ValueError("os.popen must capture output.")
    
    # Operations #
    #------------#
    
    # Capture the output
    output = os.popen(command).read()
    
    # No return code is available for os.popen, return the output
    return dict(stdout=output, return_code=None)


def subprocess_popen_helper(command, capture_output, encoding):
    """
    Helper function to execute a command using subprocess.Popen.

    Parameters
    ----------
    command : list or str
        The system command to execute.
    capture_output : bool, optional
        If True, captures stdout, stderr, and stdin.
    encoding : str, optional
        The encoding to use when decoding stdout and stderr.

    Returns:
    --------
    dict
        A dictionary containing:
        - 'stdin': Captured standard input (if applicable).
        - 'stdout': The captured standard output (if applicable).
        - 'stderr': The captured standard error (if applicable).
        - 'return_code': The exit code of the command.
        - 'errors': Any errors encountered during command execution.
    """
    from subprocess import Popen, PIPE
    
    # Define the I/O streams
    pipe_kwargs = dict(stdin=PIPE, stdout=PIPE, stderr=PIPE) if capture_output else {}
    
    # Execute the command
    process = Popen(command, **pipe_kwargs)
    
    # Wait for command to complete
    process.wait()
    
    # Capture stdin, stdout, stderr and command exit status errors if requested
    stdin = process.stdin.name if (capture_output and process.stdin) else None
    stdout = process.stdout.read().decode(encoding) if capture_output and process.stdout else None
    stderr = process.stderr.read().decode(encoding) if capture_output and process.stderr else None
    errors = process.errors if hasattr(process, "errors") else None
    
    # Return relevant data
    return dict(stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                return_code=process.returncode,
                errors=errors)


def subprocess_call_helper(command, capture_output):
    """
    Helper function to run a command using subprocess.call.
    
    Parameters
    ----------
    command : str or list
        The command to run, either as a string or a list of strings.
    capture_output : bool
        If True, output capturing is requested (not supported by this method).

    Raises
    ------
    ValueError
        If capture_output is set to True, since subprocess.call does not support capturing output.

    Returns:
    --------
    dict
        A dictionary containing the return code of the command execution.
    """
    from subprocess import call
    
    # Validate capture_output (not applicable for subprocess.call)
    if capture_output:
        raise ValueError("subprocess.call does not support capturing output.")
    
    # Execute the command
    return_code = call(command)
    
    # Return the return code
    return dict(return_code=return_code)


def subprocess_run_helper(command, capture_output, encoding, shell):
    """
    Helper function to execute a command using subprocess.run.

    Parameters
    ----------
    command : list or str
        The system command to execute.
    capture_output : bool, optional
        If True, captures stdout and stderr.
    encoding : str, optional, default: None
        The encoding to use when decoding stdout and stderr.

    Returns
    -------
    dict
        A dictionary containing:
        - 'stdout': The captured standard output.
        - 'stderr': The captured standard error.
        - 'return_code': The exit code of the command.

    Raises
    ------
    CalledProcessError
        If the command returns a non-zero exit code.
    """
    from subprocess import run, CalledProcessError
    
    # Execute the command and capture output
    result = run(command, capture_output=capture_output, text=bool(encoding), shell=shell)
    
    # Decode stdout/stderr if encoding is provided
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    
    # Raise an error for non-zero return codes
    if result.returncode != 0:
        raise CalledProcessError(result.returncode, command)
    return dict(stdout=stdout, stderr=stderr, return_code=result.returncode)

# %%

# Auxiliary methods #
#-------------------#

def exit_info(process_exit_info_obj):
    """
    Print the exit information of a process.

    This function checks the exit status of a process represented by the 
    provided `process_exit_info_obj`. If the command string fails to execute,
    it raises a RuntimeError indicating that the command was interpreted 
    as a path.

    Parameters
    ----------
    process_exit_info_obj : subprocess.CompletedProcess
        An object containing the exit information of the process, 
        typically returned by subprocess.run.

    Raises
    ------
    RuntimeError
    - If the command string is interpreted as a path and fails to execute,
      in which case Python would originally rise a FileNotFoundError.
    - If an error occurs during command execution, that is, the exit status in non-zero.

    Prints
    ------
    A message indicating whether the process completed successfully or 
    details about the non-zero exit status, including the return code 
    and any error message from stderr.
    """
    try:
        process_exit_info_obj
    except FileNotFoundError:
        # If a str command fails, bash will usually interpret 
        # that a path is trying to be searched,
        # and if it fails to find, it will raise a Python-equivalent FileNotFoundError.
        raise RuntimeError("Command string interpreted as a path. "
                           "Please check the command.")
    else:
        return_code = process_exit_info_obj.get("return_code")
        if return_code == 0:
            print("Process completed succesfully")
        else:
            format_args_error = (return_code, process_exit_info_obj.get("stderr"))
            raise RuntimeError("An error ocurred during command execution: "
                               f"{format_string(NONZERO_EXIT_STATUS_TEMPLATE, format_args_error)}")

# %%

#--------------------------#
# Parameters and constants #
#--------------------------#

# Supported options #
#-------------------#

# Modules #
SYSTEM_COMMAND_MODULES = FILESYSTEM_CONTEXT_MODULES[0::3]

# Command run classes #
CLASS_LIST = ["system", "popen", "Popen", "call", "run"]

# Template strings #
#------------------#

# Errors #
NONZERO_EXIT_STATUS_TEMPLATE = """Process exited with status {} with the following error:\n{}"""

# Switch case dictionaries #
#--------------------------#

# System command run helpers #
COMMAND_HELPERS = {
    ("os", "system"): os_system_helper,
    ("os", "popen"): os_popen_helper,
    ("subprocess", "Popen"): subprocess_popen_helper,
    ("subprocess", "run"): subprocess_run_helper,
    ("subprocess", "call"): subprocess_call_helper
}
