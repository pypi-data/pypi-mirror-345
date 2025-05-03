"""Utilities to get chunking information from netCDF files."""

import warnings
from collections.abc import Iterable
from enum import Enum
from pathlib import Path
from random import sample
from typing import Any, Literal

import netCDF4 as nc
from intake_esm import esm_datastore
from xarray import DataArray, Dataset


class ChunkingWarning(Warning):
    """
    A warning to be raised when the chunking information is not as expected.
    """

    pass


class ValidateMode(str, Enum):
    """
    This lets us specify how we want to validate the chunking. We can either go
    with `single`, `bookend` ,`sample` or `all`.
    - `single`: Only validate the chunking for the first file in the dataset.
    - `bookend`: Validate the chunking for the first and last file in the dataset.
    - `sample`: Validate the chunking for a random sample of files in the dataset.
    - `all`: Validate the chunking for all files in the dataset.
    """

    SINGLE = "single"
    BOOKEND = "bookend"
    SAMPLE = "sample"
    ALL = "all"

    def __str__(self) -> str:
        return self.value

    def __all__(self) -> list[str]:
        return [mode.value for mode in ValidateMode]


def get_disk_chunks(
    f_path: str,
    varnames: str | list[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Read a netCDF file and get the disk chunks out. Note these are disk chunks &
    are not the same as xarray chunks.

    This uses the netCDF4 library to extract the on disk chunking information
    from the netCDF file. It returns a dictionary with the variable names as keys
    and a nested dictionary with the chunking information as values.
    The nested dictionary contains the dimension names as keys and the chunk sizes
    as integer values, if available.

    Parameters
    ----------
    f_path : str
        The path to the netCDF file.

    Returns
    -------
    dict[str, dict[str, Any]]
    """

    ds = nc.Dataset(f_path)
    vars = ds.variables

    chunk_dict = {}

    for varname, var in vars.items():
        chunk_list = var.chunking()
        dimsizes = [ds.dimensions[dim].size for dim in var.dimensions]

        if chunk_list == "contiguous":
            chunk_list = dimsizes

        var_chunk_info = {
            dim: min(chunk, dimsize)
            for dim, chunk, dimsize in zip(var.dimensions, chunk_list, dimsizes)
        }
        chunk_dict[varname] = var_chunk_info

    if varnames is not None:
        if isinstance(varnames, str):
            varnames = [varnames]
        chunk_dict = {
            varname: chunk_dict[varname]
            for varname in varnames
            if varname in chunk_dict
        }

    return chunk_dict


def validate_chunkspec(
    dataset: str | Path | Iterable[str | Path] | Dataset | DataArray | esm_datastore,
    chunkspec: dict[str, Any],
    varnames: str | list[str] | None = None,
    validate_mode: Literal["single", "bookend", "sample", "all"] = "single",
    sample_size: int = 10,
) -> dict | dict[Path, dict]:
    """
    Validate the chunk sizes for a given variable name.


    This function attempts to validate that user specified chunks are compatible
    with chunking on disk, by ensuring that chunk sizes are integer multiples of
    the chunk sizes on disk.

    Parameters
    ----------
    dataset: str | Path | Iterable[str | Path] | Dataset | DataArray | esm_datastore
        A very general object that can be used to open a single (or many) netCDF
        files.
    chunkspec : dict[str, Any]
        The chunk specification dictionary, used to tell xarray how to chunk the data.
    varnames : str | list[str] | None
        The variable name(s) to validate. If none, all variables in the dataset
        will be validated.
    validate_mode : Literal["single", "bookend", "sample", "all"]
        The mode to use for validation. This lets us specify how we want to
        validate the chunking.
        - `single`: Only validate the chunking for the first file in the dataset.
        - `bookend`: Validate the chunking for the first and last file in the dataset.
        - `sample`: Validate the chunking for a random sample of files in the dataset.
        - `all`: Validate the chunking for all files in the dataset.
    sample_size : int
        The number of files to sample from the dataset if `validate_mode` is
        `sample`. Default is 10. Ignored if `validate_mode` is not `sample`.

    Returns
    -------
    dict
        An optimised chunk specification dictionary, as close as possible to the
        original chunk specification, but with chunk sizes that are integer
        multiples of the chunk sizes on disk.
    dict[dict]
        A dictionary of dictionaries, each containing the chunk specification for a
        single file in the dataset as key value pairs. This is only returned if
        files in the provided dataset are found to have inconsistent chunking.
    """

    if validate_mode not in {mode.value for mode in ValidateMode}:
        valid_modes = ", ".join([mode.value for mode in ValidateMode])
        raise ValueError(
            f"Invalid validate_mode: {validate_mode}. Must be one of {valid_modes}"
        )

    match dataset:
        case str():
            path_list = [Path(dataset)]
        case Path():
            path_list = [dataset]
        case esm_datastore():
            path_list = [Path(f) for f in dataset.unique().path]
        case Dataset() | DataArray():
            if not dataset.encoding.get("source", False):
                raise ValueError(
                    " Dataset/DataArray does contain source attribute describing file path(s)."
                    " Please provide a dataset with a source attribute, an esm_datastore,"
                    " or a list of file paths."
                )
            path_list = [Path(f) for f in dataset.encoding["source"]]
        case Iterable() if all(isinstance(f, (str | Path)) for f in dataset):
            path_list = [Path(str(f)) for f in dataset]
        case _:
            raise TypeError(
                "dataset must be a string, Path, list of strings or Paths, "
                f"Dataset, DataArray, or esm_datastore, not {type(dataset)}"
            )

    match validate_mode:
        case "single":
            path_list = [path_list[0]]
        case "bookend":
            path_list = [path_list[0], path_list[-1]]
        case "sample":
            path_list = sample(path_list, min(sample_size, len(path_list)))
        case "all":
            pass

    if isinstance(varnames, str):
        varnames = [varnames]

    disk_chunks_list = []

    for path in path_list:
        disk_chunks = get_disk_chunks(str(path), varnames)
        disk_chunks_list.append(disk_chunks)

    if not all(disk_chunk == disk_chunks_list[0] for disk_chunk in disk_chunks_list):
        warnings.warn(
            "Disk chunks differ between files in provided dataset. Generating optimal"
            " chunk specification may not be possible. Please check your dataset carefully."
            " We recommend rerunning in validate_mode `all` if you have not already done so."
            " Returning per file chunk specifications for examination.",
            ChunkingWarning,
            stacklevel=2,
        )
        return {P: disk_chunk for P, disk_chunk in zip(path_list, disk_chunks_list)}

    # From here on in, we assume that all disk chunks are the same.
    disk_chunks = disk_chunks_list[0]

    # Disk chunks don't come in quite the same format that we would pass into
    # the xarray chunkspec. We need to marry the two up.

    min_valid_chunks: dict[str, int] = {}

    for varname, chunk_dict in disk_chunks.items():
        # We need to ensure that the chunk_dict is a dict of dicts
        # with the variable name as the key.
        if varname not in chunkspec and not any(
            dimname in chunkspec for dimname in chunk_dict
        ):
            continue

        for dimname, chunksize in chunk_dict.items():
            if (
                min_valid_chunks.get(dimname, None) is None
            ):  # Add it to our specification if not found
                min_valid_chunks[dimname] = chunksize
            elif (
                min_valid_chunks[dimname] < chunksize
            ):  # If a new variable uses a larger chunk size, use that
                min_valid_chunks[dimname] = chunksize

    # Remove all `-1` values from chunkspec - these are 'the full length'
    # specifiers, so we don't need to worry about them.
    _chunkspec = {k: v for k, v in chunkspec.items() if v != -1}
    _full_length = {k: v for k, v in chunkspec.items() if v == -1}

    suggested_chunks = {}

    for dim in _chunkspec.keys():
        disk_chunksize = min_valid_chunks[dim]
        mem_chunksize = _chunkspec[dim]

        if mem_chunksize % disk_chunksize != 0:
            nchunk = round(mem_chunksize / disk_chunksize) or 1
            _chunk = nchunk * disk_chunksize
            suggested_chunks[dim] = _chunk
        else:
            suggested_chunks[dim] = mem_chunksize

    if suggested_chunks != _chunkspec:
        warnings.warn(
            "Specified chunks are not integer multiples of the disk chunks."
            " Returning suggested chunks as a dictionary.",
            category=ChunkingWarning,
            stacklevel=2,
        )

    suggested_chunks.update(_full_length)

    return suggested_chunks
