"""
ard.py

This module contains a collection of functions for analysis-ready-data (ARD) operations on climate data at NCI.
Author = {"name": "Thomas Moore", "affiliation": "CSIRO", "email": "thomas.moore@csiro.au", "orcid": "0000-0003-3930-1946"}

NOTE: This module needs to be updated to remove the dependency on config settings via `load_config()`.
"""

# Standard library imports
import datetime
import os

# Third-party imports
# import numpy as np
import intake_esm
import numpy as np
import xarray as xr
from tabulate import tabulate

# Local application imports (if needed)
# from .my_local_module import my_function


def load_ACCESS_ESM_ensemble(
    catalog_search,
    use_cftime=False,
    chunking_settings=None,
    chunking_key=None,
    drop_extra_variables=True,
    drop_list=["vertices_longitude", "vertices_latitude", "time_bnds"],
):
    """
    Load the ACCESS-ESM ensemble data from an esm_datastore.

    Parameters
    ----------
    catalog_search : intake_esm.core.esm_datastore object -  This will come from filtering an intake catalog that contains the ACCESS-ESM ensemble data.
    chunking_settings : dict - A dictionary containing the chunking settings for the dataset. The default is None.
    drop_extra_variables : bool - A flag to drop extra variables that are not the primary variable. The default is True.

    Returns
    -------
    ds_sorted : xarray.Dataset - The concatenated dataset with the ACCESS-ESM ensemble data labelled and sorted based on the member names.

    """
    # check if the catalog_search is an esm_datastore object, specifically intake_esm.core.esm_datastore
    if not isinstance(catalog_search, intake_esm.core.esm_datastore):
        raise TypeError(
            "catalog_search must be an instance of intake_esm.core.esm_datastore!!! Did catalog_search come from filtering an intake catalog?"
        )
    # check if the catalog_search contains ACCESS-ESM ensemble data
    # is there one and only one source_id in the catalog_search?
    if len(catalog_search.df["source_id"].unique()) != 1:
        raise ValueError("The catalog_search must contain only one source_id!!!")
    # is the source_id ACCESS-ESM?
    if not any(
        source_id.startswith("ACCESS-ESM")
        for source_id in catalog_search.df["source_id"].unique()
    ):
        raise ValueError("The catalog_search must contain ACCESS-ESM data!!!")
    # check that there is at least 2 ensembles in the catalog_search
    if len(catalog_search.df["member_id"].unique()) < 2:
        raise ValueError("The catalog_search must contain at least 2 ensembles!!!")
    # Get the dictionary of datasets and the corresponding keys (member names)
    # if chunking_key is provided, use it to load the dataset
    if chunking_key:
        from .util import load_config

        config = load_config()  # Load the configuration file from yaml
        xarray_open_kwargs = config["chunking"][chunking_key]
        print(
            f"Loading the dataset using the chunking settings for '{chunking_key}' from the configuration file: {xarray_open_kwargs}"
        )
    # if chunking_settings is provided, use it to load the dataset
    elif chunking_settings:
        xarray_open_kwargs = chunking_settings
        print(
            f"Loading the dataset using the provided chunking settings: {xarray_open_kwargs}"
        )
    else:
        xarray_open_kwargs = {}
        print("Loading the dataset using the default chunking settings")
    if use_cftime:
        xarray_open_kwargs["use_cftime"] = use_cftime
        print(f"Loading the dataset with cftime = {use_cftime}")
    dataset_dict = catalog_search.to_dataset_dict(
        progressbar=False, xarray_open_kwargs=xarray_open_kwargs
    )
    # Drop extra variables that are not the primary variable if condition is True
    if drop_extra_variables:
        dataset_dict_clean = {
            key: ds.drop_vars(drop_list, errors="ignore")
            for key, ds in dataset_dict.items()
        }
        dataset_dict = dataset_dict_clean
    # check that the member names are unique
    if len(dataset_dict.keys()) != len(
        set([key.split(".")[5] for key in dataset_dict.keys()])
    ):
        raise ValueError("The member names are not unique!!!")
    # Extract the member names from the keys
    member_names = [
        key.split(".")[5] for key in dataset_dict.keys()
    ]  # Extract 'r9i1p1f1' as the member name from each key
    # check that the member names are in the format 'r[integer 1-99]i[integer 1-99]p[integer 1-99]f[integer 1-99]'
    if not all(
        member_name.startswith("r")
        and member_name[1:].split("i")[0].isdigit()
        and member_name[1:].split("i")[1].split("p")[0].isdigit()
        and member_name[1:].split("i")[1].split("p")[1].split("f")[0].isdigit()
        and member_name[1:].split("i")[1].split("p")[1].split("f")[1].isdigit()
        for member_name in member_names
    ):
        raise ValueError(
            "The member names are not in the format 'r[integer 1-99]i[integer 1-99]p[integer 1-99]f[integer 1-99]'!!!"
        )
    # Concatenate the datasets along the 'member' dimension and retain the member names
    ds = xr.concat(
        dataset_dict.values(),
        dim=xr.DataArray(member_names, dims="member", name="member"),
    )
    # Extract the numeric part from each member name and sort based on it
    sorted_member_indices = np.argsort(
        [int(member[1:].split("i")[0]) for member in ds["member"].values]
    )
    # Reorder the dataset based on the sorted member indices
    ds_sorted = ds.isel(member=sorted_member_indices)
    return ds_sorted


def load_ACCESS_ESM(
    catalog_search,
    use_cftime=False,
    chunking_settings=None,
    chunking_key=None,
    drop_extra_variables=True,
    drop_list=["vertices_longitude", "vertices_latitude", "time_bnds"],
):
    """
    Load single ensemble ACCESS-ESM data from an esm_datastore.

    Parameters
    ----------
    catalog_search : intake_esm.core.esm_datastore object -  This will come from filtering an intake catalog that contains the ACCESS-ESM ensemble data.
    chunking_settings : dict - A dictionary containing the chunking settings for the dataset. The default is None.
    drop_extra_variables : bool - A flag to drop extra variables that are not the primary variable. The default is True.

    Returns
    -------
    ds : xarray.Dataset - The loaded dataset.

    """
    # check if the catalog_search is an esm_datastore object, specifically intake_esm.core.esm_datastore
    if not isinstance(catalog_search, intake_esm.core.esm_datastore):
        raise TypeError(
            "catalog_search must be an instance of intake_esm.core.esm_datastore!!! Did catalog_search come from filtering an intake catalog?"
        )
    # check if the catalog_search contains ACCESS-ESM ensemble data
    # is there one and only one source_id in the catalog_search?
    if len(catalog_search.df["source_id"].unique()) != 1:
        raise ValueError("The catalog_search must contain only one source_id!!!")
    # is the source_id ACCESS-ESM?
    if not any(
        source_id.startswith("ACCESS-ESM")
        for source_id in catalog_search.df["source_id"].unique()
    ):
        raise ValueError("The catalog_search must contain ACCESS-ESM data!!!")
    # check that there is at least 2 ensembles in the catalog_search
    if len(catalog_search.df["member_id"].unique()) > 1:
        raise ValueError("The catalog_search must contain only one ensemble!!!")
    # Get the dictionary of datasets and the corresponding keys (member names)
    # if chunking_key is provided, use it to load the dataset
    if chunking_key:
        from .util import load_config

        config = load_config()  # Load the configuration file from yaml
        xarray_open_kwargs = config["chunking"][chunking_key]
        print(
            f"Loading the dataset using the chunking settings for '{chunking_key}' from the configuration file: {xarray_open_kwargs}"
        )
    # if chunking_settings is provided, use it to load the dataset
    elif chunking_settings:
        xarray_open_kwargs = chunking_settings
        print(
            f"Loading the dataset using the provided chunking settings: {xarray_open_kwargs}"
        )
    else:
        xarray_open_kwargs = {}
        print("Loading the dataset using the default chunking settings")
    if use_cftime:
        xarray_open_kwargs["use_cftime"] = use_cftime
        print(f"Loading the dataset with cftime = {use_cftime}")
    ds = catalog_search.to_dask(
        progressbar=False, xarray_open_kwargs=xarray_open_kwargs
    )
    # Drop extra variables that are not the primary variable if condition is True
    if drop_extra_variables:
        ds.drop_vars(drop_list, errors="ignore")
    return ds


def find_chunking_info(catalog_search, var_name, return_results=False):
    """
    Find the chunking information for a dataset in an esm_datastore.  This takes a simple approach to the possibility of different
    chunking information between file paths in the catalog search by comparing the first and the last files in the list of paths.

    Parameters
    ----------
    catalog_search : intake_esm.core.esm_datastore object -  This will come from filtering an intake catalog.

    Returns
    -------
    chunking_info : dict - A dictionary containing the chunking information for each variable in the dataset.

    """
    # check if the catalog_search is an esm_datastore object, specifically intake_esm.core.esm_datastore
    if not isinstance(catalog_search, intake_esm.core.esm_datastore):
        raise TypeError(
            "catalog_search must be an instance of intake_esm.core.esm_datastore!!! Did catalog_search come from filtering an intake catalog?"
        )
    # get the first and the last paths in the catalog_search
    first_path = catalog_search.df["path"].iloc[0]
    last_path = catalog_search.df["path"].iloc[-1]
    # Construct the command to run ncdump on the first file path
    command = f"ncdump -hs {first_path}"
    # Run the command and capture the output
    output = os.popen(command).read()
    # Parse the output to extract the chunking information
    chunking_info_first = {}
    lines = output.split("\n")
    for line in lines:
        if "_ChunkSizes" in line:
            chunk_sizes = line.split("=")[1].strip()
            chunking_info_first[var_name] = {
                "chunk_sizes": chunk_sizes,
                "file_path": first_path,
            }
    # Construct the command to run ncdump on the last file path
    command = f"ncdump -hs {last_path}"
    # Run the command and capture the output
    output = os.popen(command).read()
    # Parse the output to extract the chunking information
    chunking_info_last = {}
    lines = output.split("\n")
    for line in lines:
        if "_ChunkSizes" in line:
            chunk_sizes = line.split("=")[1].strip()
            chunking_info_last[var_name] = {
                "chunk_sizes": chunk_sizes,
                "file_path": last_path,
            }
    # compare the chunking information from the first and the last files - if the chunking information isn't the same, raise a warning
    if (
        chunking_info_first[var_name]["chunk_sizes"]
        != chunking_info_last[var_name]["chunk_sizes"]
    ):
        print(
            f"WARNING: The chunking information for the variable '{var_name}' is different between the first and the last files in the list of paths!!!"
        )
    # Create a table with the chunking information
    max_chars_per_line = 50  # Maximum number of characters per line
    max_words_per_line = 10  # Maximum number of words per line
    table_data_formatted = []
    # use the tabulate function to format the table
    table_data = [
        ["Variable", var_name],
        ["Chunk sizes (first file)", chunking_info_first[var_name]["chunk_sizes"]],
        ["File path (first file)", chunking_info_first[var_name]["file_path"]],
        ["Chunk sizes (last file)", chunking_info_last[var_name]["chunk_sizes"]],
        ["File path (last file)", chunking_info_last[var_name]["file_path"]],
    ]
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
            # Break up long lines over max_chars_per_line on forward slashes
            lines_formatted = []
            for line in lines:
                if len(line) > max_chars_per_line:
                    line_parts = line.split("/")
                    current_line = ""
                    for part in line_parts:
                        if len(current_line) + len(part) + 1 <= max_chars_per_line:
                            current_line += part + "/"
                        else:
                            lines_formatted.append(current_line.strip())
                            current_line = part + "/"
                    lines_formatted.append(current_line.strip())
                else:
                    lines_formatted.append(line)
            table_data_formatted.append([key, "\n".join(lines_formatted)])
        else:
            table_data_formatted.append([key, value])
    print(tabulate(table_data_formatted, tablefmt="fancy_grid"))

    # Conditionally return results based on the flag
    if return_results:
        # Combine the chunking information from the first and the last files
        chunking_info = {
            var_name: {
                "chunk_sizes_first": chunking_info_first[var_name]["chunk_sizes"],
                "file_path_first": chunking_info_first[var_name]["file_path"],
                "chunk_sizes_last": chunking_info_last[var_name]["chunk_sizes"],
                "file_path_last": chunking_info_last[var_name]["file_path"],
            }
        }
        return chunking_info
    else:
        return None


def save_n_drop_multidim_lat_lon(
    ds,
    save_coords_dir,
    coords_name="ACCESS-ESM1.5",
    variable_name="var_name_unknown",
    drop_list=["latitude", "longitude", "vertices_latitude", "vertices_longitude"],
):
    # check if the objects in drop_list are in the dataset
    final_drop_list = []
    for item in drop_list:
        if item in ds:
            print(f"The item '{item}' was found in the dataset and will be dropped!!!")
            final_drop_list.append(item)
    coords = ds[final_drop_list]
    current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{coords_name}_{variable_name}_coords_{current_datetime}.nc"
    coords.to_netcdf(save_coords_dir + filename)
    ds_dropped = ds.drop(final_drop_list)
    ds_dropped.attrs["coords_filename"] = save_coords_dir + filename
    ds_dropped.attrs["NOTE on coordinates"] = (
        "the multidimensional latitude and longitude coordinates have been saved as a separate NetCDF file"
    )
    return ds_dropped
