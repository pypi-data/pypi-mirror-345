#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import numpy as np

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_type_str

#------------------#
# Define functions #
#------------------#

# Data types #
#------------#
        
def convert_data_type(obj_data, old_type, new_type, colnames=None, convert_to_list=False):
    """
    Function that converts the original data type of the values in a given object 
    (numpy array, pandas DataFrame/Series) to the desired one.
    If the new data type is the same as the original, the function returns 
    the object unchanged, and prints a message showing the latter.

    Parameters
    ----------
    obj_data : pandas.DataFrame, pandas.Series, numpy.ndarray, or list
        Object containing the data to be converted.
    old_type : str
        Current type of the object's values.
    new_type : str
        Type to which the data should be converted.
    colnames : str, list of str, or '__all_columns__', optional
        Column(s) to apply conversion in case of pandas DataFrame.
        If '__all_columns__', conversion will be applied to all columns.
        Not applicable for pandas Series or numpy arrays.
    convert_to_list : bool, optional
        If True, converts the result to a list before returning.
    
    Returns
    -------
    obj_data : pandas.DataFrame, pandas.Series, numpy.ndarray, or list
        Object with the converted data type, or unchanged if no conversion was made.

    Raises
    ------
    TypeError
        If the conversion to the new type cannot be done or if the object type is invalid.
    KeyError
        If specified columns are not found in pandas DataFrame.
    """
    # Get input object's type
    obj_type = get_type_str(obj_data)
    
    # Handle pandas DataFrames
    if obj_type == "DataFrame":
        if colnames is None:
            raise ValueError("Please specify 'colnames' for pandas DataFrame.")
        if colnames == '__all_columns__':  # apply to all columns
            colnames = obj_data.columns
        elif isinstance(colnames, str):
            colnames = [colnames]  # convert to list for consistency
        elif isinstance(colnames, list):
            pass
        else:
            raise TypeError("'colnames' must be a string, list of strings, or '__all_columns__'.")

        # Find missing columns
        missing_cols = [col for col in colnames if col not in obj_data.columns]
        if missing_cols:
            raise KeyError(f"The following columns were not found: {missing_cols}")

        # Apply conversion
        data_converted = obj_data.copy()
        for col in colnames:
            if obj_data[col].dtype == old_type:
                try:
                    data_converted[col] = obj_data[col].astype(new_type)
                except:
                    raise TypeError(f"Cannot convert column '{col}' to type '{new_type}'.")
            else:
                print(f"Column '{col}' data type unchanged.")
        
        return data_converted

    # Handle pandas Series
    elif obj_type == "Series":       
        if obj_data.dtype == old_type:
            try:
                return obj_data.astype(new_type)
            except:
                raise TypeError(f"Cannot convert Series to type '{new_type}'.")
        else:
            print("Series data type unchanged.")
            return obj_data

    # Handle numpy arrays and lists
    elif obj_type in ["ndarray", "list"]:
        try:
            obj_data = np.array(obj_data)  # convert to numpy array if it's not already
            if obj_data.dtype == old_type:
                try:
                    data_converted = obj_data.astype(new_type)
                except:
                    raise TypeError(f"Cannot convert array to type '{new_type}'.")
                if convert_to_list:
                    return list(data_converted)
                return data_converted
            else:
                print("Array data type unchanged.")
                if convert_to_list:
                    return list(obj_data)
                return obj_data
        except Exception as e:
            raise TypeError(f"Error occurred during conversion: {e}")

    # Raise TypeError if the object type is not supported
    else:
        raise TypeError("Unsupported object type. "
                        "Expected pandas DataFrame/Series, numpy array, or list.")

            
def combine_arrays(array_of_lists):
    """
    Combine a list of NumPy arrays or lists into a single NumPy array.
    
    This function takes a list of NumPy arrays (or lists) and combines them 
    into a single NumPy array. It supports arrays with up to 3 dimensions.
    If the arrays have inhomogeneous lengths, it uses `np.hstack` to flatten 
    and concatenate the arrays.
    
    Parameters
    ----------
    array_of_lists : list
        A list of NumPy arrays or lists to be combined.
    
    Returns
    -------
    array : numpy.ndarray
        A single NumPy array formed by combining the input arrays.
    
    Raises
    ------
    ValueError
        - If the arrays in the list have more than 3 dimensions.
        - If the shapes of the arrays are inconsistent and cannot be combined.
    
    Example
    -------
    >>> import numpy as np
    >>> array1 = np.array([[1, 2], [3, 4]])
    >>> array2 = np.array([[5, 6], [7, 8]])
    >>> array_of_lists = [array1, array2]
    >>> result = combine_arrays(array_of_lists)
    >>> print(result)
    [[1 2]
     [3 4]
     [5 6]
     [7 8]]
    
    Notes
    -----
    - If the arrays have different shapes, they are concatenated and flattened 
      using `np.hstack`.
    - This function assumes that the input contains valid NumPy arrays or lists.
    """    
    # Get the list of unique dimensions of the arrays #
    dim_list = np.unique([arr.ndim for arr in array_of_lists])
    ld = len(dim_list)
    
    # If all arrays/lists are of the same dimension #
    if ld == 1:
        dims = dim_list[0]
        
        if dims == 2:
            array = np.vstack(array_of_lists)
        elif dims == 3:
            array = np.stack(array_of_lists)
        else:
            raise ValueError("Cannot handle arrays with dimensions greater than 3.")
            
    # If the arrays/lists have inconsistent dimensions #
    else:
        array = np.hstack(array_of_lists)
        
    return array


def flatten_to_string(obj, delim=" ", add_final_space=False):
    """
    Flatten the content of a list, NumPy array, or pandas DataFrame/Series 
    into a single string, where elements are separated by a specified delimiter.

    This method takes an input object (list, NumPy array, pandas DataFrame, or Series),
    flattens it (if needed), converts all elements to strings, and joins them into 
    a single string. Optionally, a final delimiter can be added to the end of the string.

    Parameters
    ----------
    obj : list, numpy.ndarray, pandas.DataFrame, or pandas.Series
        The input object containing data to be flattened and converted to a string.
    delim : str, optional
        The delimiter to use for separating elements in the resulting string.
        By default, a space character (' ') is used.
    add_final_space : bool, optional
        If True, adds a delimiter (or space) at the end of the string.
        Default is False.
    
    Returns
    -------
    str
        A single string containing all elements of the input object, 
        separated by the specified delimiter.

    Raises
    ------
    TypeError
        If the input object is not a list, numpy array, pandas DataFrame, or Series.

    Example
    -------
    >>> import numpy as np
    >>> arr = np.array([[1, 2], [3, 4]])
    >>> flatten_to_string(arr, delim=',', add_final_space=True)
    '1,2,3,4,'
    
    Notes
    -----
    This method is particularly useful for converting arrays or lists of file names 
    into a single string to pass as arguments to shell commands or other processes 
    that require string input.
    """
    # Get input object type 
    obj_type = get_type_str(obj)
    
    # Validate input type #
    if obj_type not in ["list", "ndarray", "DataFrame", "Series"]:
        raise TypeError("'flatten_to_string' supports lists, NumPy arrays, and pandas DataFrames/Series.")
    
    # Convert pandas DataFrame/Series to NumPy array #
    if obj_type not in ["DataFrame", "Series"]:
        obj_val_array = obj.values
    else:
        obj_val_array = np.array(obj)  # Ensure it's a NumPy array if it's a list
    
    # Flatten the array if it has more than one dimension #
    if hasattr(obj_val_array, "flatten"):
        obj_val_array = obj_val_array.flatten()

    # Convert all elements to strings #
    obj_list = [str(el) for el in obj_val_array]
    
    # Join all elements into a single string #
    allobj_string = delim.join(obj_list)
    
    # Optionally add a final delimiter/space #
    if add_final_space:
        allobj_string += delim
    
    return allobj_string
