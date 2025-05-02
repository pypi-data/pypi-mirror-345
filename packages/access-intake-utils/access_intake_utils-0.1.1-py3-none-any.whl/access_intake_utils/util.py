"""
util.py

This module contains a collection of utility functions.
Author = {"name": "Thomas Moore", "affiliation": "CSIRO", "email": "thomas.moore@csiro.au", "orcid": "0000-0003-3930-1946"}
"""

# Standard library imports

import intake
import xarray as xr

# Third-party imports
# import numpy as np
from tabulate import tabulate

# Local application imports (if needed)
# from .my_local_module import my_function


def report_esm_unique(
    esm_datastore_object,
    drop_list=["path", "time_range", "member_id", "version", "derived_variable_id"],
    keep_list=None,
    header=["Category", "Unique values"],
    return_results=False,
):
    """
    Generate a table of unique values for each category in the esm_datastore_object, optionally returning the data.

    Parameters
    ----------
    esm_datastore_object : object
        An object that has a `.unique()` method to generate unique entries for each category.
    drop_list : list, optional
        A list of keys to exclude from the final dictionary (default is ['path','time_range','member_id','version','derived_variable_id']).
    keep_list : list, optional
        A list of keys to keep in the final dictionary, dropping all others (default is None).
    header : list, optional
        The header for the output table (default is ["Category", "Unique values"]).
    return_results : bool, optional
        Whether to return the unique_dict and table_data (default is False).

    Returns
    -------
    unique_dict : dict or None
        A dictionary of unique values for each category (returned only if `return_results=True`).
    table_data : list or None
        A list of lists formatted for tabulation (returned only if `return_results=True`).
    """
    # Get the unique values from the esm_datastore_object
    unique = esm_datastore_object.unique()

    # Convert to dictionary
    unique_dict = unique.to_dict()

    # Keep only specified keys if keep_list is provided
    if keep_list is not None:
        unique_dict = {
            key: value for key, value in unique_dict.items() if key in keep_list
        }
    # Drop specified keys if drop_list is provided
    elif drop_list is not None:
        unique_dict = {
            key: value for key, value in unique_dict.items() if key not in drop_list
        }

    # Sort each list of values in the dictionary and sort the keys alphabetically
    sorted_unique_dict = {
        key: sorted(value) if isinstance(value, list) else value
        for key, value in sorted(unique_dict.items())
    }

    # Prepare data for tabulation
    table_data = []
    for key, value in sorted_unique_dict.items():
        # If value is a list, join elements by newline; otherwise, use the value as is
        table_data.append([key, "\n".join(value) if isinstance(value, list) else value])

    # Print the table
    print(tabulate(table_data, headers=header, tablefmt="fancy_grid"))

    # Conditionally return results based on the flag
    if return_results:
        return sorted_unique_dict, table_data


def var_name_info(catalog_object, var_name, return_results=False):
    """
    Extracts information about a variable from an intake-esm catalog object.

    Parameters
    ----------
    catalog_object : intake_esm.core.esm_datastore object
        An intake-esm catalog object, likely containing many variables.
    var_name : str
        The name of the variable to extract information for.
    return_results : bool, optional
        Whether to return the variable information (default is False).

    Returns
    -------
    var_info : dict or None
        A dictionary containing the variable information (returned only if `return_results=True`).
    """
    var_ds = xr.open_mfdataset(
        (catalog_object.search(variable_id=var_name).unique().path)[0], chunks={}
    )
    var_info = var_ds[var_name].attrs
    # turn the dictionary into a table for easy reading - adding a header that reports the variable name and name of the catalog object
    print(f"*** Variable: \033[1m{var_name}\033[0m from catalog: {catalog_object} ***")
    table_data = []
    for key, value in var_info.items():
        table_data.append([key, value])
    # Print the table
    max_chars_per_line = 100  # Maximum number of characters per line
    max_words_per_line = 30  # Maximum number of words per line
    table_data_formatted = []
    for key, value in table_data:
        if isinstance(value, str):
            # Split the value into words
            words = value.split()
            # Create a new list to store the formatted lines
            lines = []
            current_line = ""
            for word in words:
                # Check if adding the current word exceeds the maximum characters or words per line
                if (
                    len(current_line) + len(word) + 1 <= max_chars_per_line
                    and len(lines) < max_words_per_line
                ):
                    current_line += word + " "
                else:
                    # Add the current line to the lines list and start a new line with the current word
                    lines.append(current_line.strip())
                    current_line = word + " "
            # Add the last line to the lines list
            lines.append(current_line.strip())
            # Join the lines with newline characters
            formatted_value = "\n".join(lines)
            table_data_formatted.append([key, formatted_value])
        else:
            table_data_formatted.append([key, value])
    print(
        tabulate(
            table_data_formatted, headers=["Attribute", "Value"], tablefmt="fancy_grid"
        )
    )
    # Conditionally return results
    if return_results:
        return var_info


def list_catalog_query_kwargs(esmds):
    """
    List all possible keyword arguments for the **query argument
    in the search method of an intake_esm.core.esm_datastore object.

    Parameters:
        esmds (intake_esm.core.esm_datastore): The ESM datastore object.

    Returns:
        list: A list of column names that can be used as keyword arguments for **query.

    Example usage:
    Assuming `esmds` is your intake_esm.core.esm_datastore object
    query_kwargs = list_query_kwargs(cmip6_fs38_datastore)
    print("Possible query kwargs for search method:", query_kwargs)
    """
    # Get the columns of the dataframe inside the esm_datastore
    query_kwargs = esmds.df.columns.tolist()
    print(
        tabulate(
            [[kw] for kw in query_kwargs],
            headers=["Possible query kwargs"],
            tablefmt="fancy_grid",
        )
    )
    return query_kwargs


def load_cmip6_fs38_datastore():
    """
    Load the CMIP6 FS38 data catalog as an intake-esm datastore object.

    Returns:
    intake_esm.core.esm_datastore: The CMIP6 FS3.8 data catalog as an intake-esm datastore object.
    """

    # Load the CMIP6 FS38 data catalog
    nri_catalog = intake.cat.access_nri
    cmip6_fs38_datastore = nri_catalog.search(name="cmip6_fs38").to_source()
    return cmip6_fs38_datastore


def load_cmip6_CLEX_datastore():
    """
    Load the CMIP6 FS38 data catalog as an intake-esm datastore object using the frozen CLEX NCI catalog.
    Using the 'cmip6' entry of the 'esgf' sub-catalog of the CLEX "nci" catalog provides access to only the latest CMIP6 data.
    See: https://github.com/Thomas-Moore-Creative/ACDtools/issues/2#issuecomment-2510304106

    Returns:
    intake_esm.core.esm_datastore: The CMIP6 FS3.8 CLEX data catalog as an intake-esm datastore object.
    """

    # Load the CMIP6 CLEX FS38 data catalog
    clex_esgf_cat = intake.cat.nci["esgf"]
    clex_cmip6_cat = clex_esgf_cat["cmip6"]
    return clex_cmip6_cat


def show_methods(your_object):
    # Get all attributes of the object
    all_methods = dir(your_object)

    # Filter the list to only show callable methods
    methods_only = []
    for method in all_methods:
        try:
            if callable(getattr(your_object, method)):
                methods_only.append(method)
        except AttributeError:
            pass

    # Print all the methods
    for method in methods_only:
        print(method)
