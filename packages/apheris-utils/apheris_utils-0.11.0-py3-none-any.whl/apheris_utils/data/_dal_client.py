from pathlib import Path
from typing import Any, Dict, List, Union

from apheris_utils.data.primitives import (
    get,
    get_settings,
    list_remote_files,
    to_folder,
)
from apheris_utils.data.primitives._session import create_session_with_retries

_session = create_session_with_retries()


def get_asset_policies(
    dataset_ids: Union[str, List[str]],
) -> Dict[str, Dict[str, Any]]:
    """
    Retrieves policy details for one or more datasets from the configured policy endpoint.

    Args:
        dataset_ids (Union[str, List[str]]): A single dataset id or a list of dataset ids for which policies are requested.

    Raises:
        RuntimeError: If the request to the policy endpoint fails.

    Returns:
        Union[Dict[str, Any], Dict[str, Dict[str, Any]]]: A dictionary containing the policy details for the requested dataset(s).
        If called with a single dataset id, returns a dictionary with the policy details. If called with a list of dataset ids,
        returns a dictionary of dictionaries with each dataset's policy details.
    """
    if isinstance(dataset_ids, str):
        settings = get_settings()
        r = _session.get(
            f"{settings.policy_endpoint}{settings.data[dataset_ids]}",
            headers=settings.headers,
        )
        if r.status_code != 200:
            raise RuntimeError(f"Failed to get policy: {r.text}")

        return {dataset_ids: r.json()}

    policies = {}
    for d in dataset_ids:
        policies.update(get_asset_policies(d))

    return policies


# Alias to load_dataset
def download_dataset(dataset_id: str, folder: Union[str, Path]) -> Dict[str, Path]:
    """
    Load a dataset from the DAL and save it to a folder.

    Args:
        dataset_id (str): The ID of the dataset to load.
        folder (Union[str, Path]): The folder where the dataset will be saved.

    Returns:
        Dict[str,str]: A dictionary mapping dataset id to their saved locations
    """
    return get(list_remote_files(dataset_id), to_folder(folder))


def list_dataset_ids() -> List[str]:
    """
    List all available dataset ids.

    Returns:
        List[str]: A list of all available dataset ids.
    """
    settings = get_settings()
    return list(settings.data.keys())


# Alias to download all datasets
def download_all(folder: Union[str, Path]) -> Dict[str, Path]:
    """
    Downloads all datasets specified in the settings and saves them to the provided folder.

    Args:
        folder (Union[str, Path]): The path to the directory where the datasets will be stored.

    Returns:
        Dict[str, Union[str, Dict[str,str]]]: A dictionary mapping dataset IDs to their saved locations
    """
    # We get a list of dataset ids such as `my-data`, `my-slug`
    dataset_ids = list_dataset_ids()
    output = {}
    for dataset_id in dataset_ids:
        remote_files = list_remote_files(dataset_id)
        output.update(get(remote_files, to_folder(folder)))
    return output
