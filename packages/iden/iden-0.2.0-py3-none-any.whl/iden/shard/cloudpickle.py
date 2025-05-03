r"""Contain cloudpickle-based shard implementations."""

from __future__ import annotations

__all__ = ["CloudpickleShard", "create_cloudpickle_shard"]

import logging
from typing import TYPE_CHECKING, Any

from coola.utils.path import sanitize_path
from objectory import OBJECT_TARGET

from iden.constants import KWARGS, LOADER
from iden.io import CloudpickleLoader, CloudpickleSaver, JsonSaver
from iden.shard.file import FileShard

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class CloudpickleShard(FileShard[Any]):
    r"""Implement a cloudpickle shard.

    The data are stored in a cloudpickle file.

    Args:
        uri: The shard's URI.
        path: The path to the cloudpickle file.

    Raises:
        RuntimeError: if ``cloudpickle`` is not installed.

    Example usage:

    ```pycon

    >>> import tempfile

    >>> from pathlib import Path
    >>> from iden.shard import CloudpickleShard
    >>> from iden.io import save_pickle
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     file = Path(tmpdir).joinpath("data.pkl")
    ...     save_pickle([1, 2, 3], file)
    ...     shard = CloudpickleShard(uri="file:///data/1234456789", path=file)
    ...     shard.get_data()
    ...
    [1, 2, 3]

    ```
    """

    def __init__(self, uri: str, path: Path | str) -> None:
        super().__init__(uri, path, loader=CloudpickleLoader())

    @classmethod
    def generate_uri_config(cls, path: Path) -> dict:
        r"""Generate the minimal config that is used to load the shard
        from its URI.

        The config must be compatible with the JSON format.

        Args:
            path: The path to the pickle file.

        Returns:
            The minimal config to load the shard from its URI.

        Example usage:

        ```pycon
        >>> import tempfile
        >>> from pathlib import Path
        >>> from iden.shard import CloudpickleShard
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     file = Path(tmpdir).joinpath("data.pkl")
        ...     CloudpickleShard.generate_uri_config(file)
        ...
        {'kwargs': {'path': '.../data.pkl'},
         'loader': {'_target_': 'iden.shard.loader.CloudpickleShardLoader'}}

        ```
        """
        return {
            KWARGS: {"path": sanitize_path(path).as_posix()},
            LOADER: {OBJECT_TARGET: "iden.shard.loader.CloudpickleShardLoader"},
        }


def create_cloudpickle_shard(data: Any, uri: str, path: Path | None = None) -> CloudpickleShard:
    r"""Create a ``CloudpickleShard`` from data.

    Note:
        It is a utility function to create a ``CloudpickleShard`` from its
            data and URI. It is possible to create a ``CloudpickleShard``
            in other ways.

    Args:
        data: The data to save in the cloudpickle file.
        uri: The shard's URI.
        path: The path to the cloudpickle file. If ``None``, a path is
            automatically based on the URI.

    Returns:
        The ``CloudpickleShard`` object.

    Raises:
        RuntimeError: if ``cloudpickle`` is not installed.

    Example usage:

    ```pycon

    >>> import tempfile
    >>> from pathlib import Path
    >>> from iden.shard import create_pickle_shard
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     shard = create_pickle_shard([1, 2, 3], uri=Path(tmpdir).joinpath("my_uri").as_uri())
    ...     shard.get_data()
    ...
    [1, 2, 3]

    ```
    """
    if path is None:
        path = sanitize_path(uri + ".pkl")
    logger.info(f"Saving URI file {uri}")
    JsonSaver().save(CloudpickleShard.generate_uri_config(path), sanitize_path(uri))
    logger.info(f"Saving data in file {path}")
    CloudpickleSaver().save(data, path)
    return CloudpickleShard(uri, path)
