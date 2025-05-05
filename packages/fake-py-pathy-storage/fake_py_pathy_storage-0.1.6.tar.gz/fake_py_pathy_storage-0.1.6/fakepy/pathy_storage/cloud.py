from abc import abstractmethod
from typing import Any, Dict, Optional, Union

from fake import BaseStorage
from pathy import Pathy

from .helpers import is_legacy_pathy_version

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2024-2025 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "CloudStorage",
    "LocalFileSystemStorage",
    "PathyFileSystemStorage",
)

DEFAULT_ROOT_PATH = "tmp"
DEFAULT_REL_PATH = "tmp"
IS_LEGACY_PATHY_VERSION = is_legacy_pathy_version()


class CloudStorage(BaseStorage):
    """File storage class using Pathy for path handling.

    Usage example:

    .. code-block:: python

        from fake import FAKER
        from fakepy.pathy_storage import LocalFileSystemStorage

        storage = LocalFileSystemStorage()
        docx_file = FAKER.docx_file(storage=storage)

    Initialization with params:

    .. code-block:: python

        from fake import FAKER
        from fakepy.pathy_storage import LocalFileSystemStorage

        storage = LocalFileSystemStorage()
        docx_file = storage.generate_filename(prefix="zzz_", extension="docx")
        storage.write_bytes(docx_file, FAKER.docx())
    """

    bucket_name: str
    bucket: Pathy
    credentials: Dict[str, str]
    schema: Optional[str] = None

    def __init__(
        self: "CloudStorage",
        bucket_name: str,
        root_path: Optional[str] = DEFAULT_ROOT_PATH,
        rel_path: Optional[str] = DEFAULT_REL_PATH,
        credentials: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        :param bucket_name: Bucket name.
        :param root_path: Path of your files root directory (e.g., Django's
            `settings.MEDIA_ROOT`).
        :param rel_path: Relative path (from root directory).
        :param credentials: Dictionary of credentials.
        :param *args:
        :param **kwargs:
        :raises: NotImplementedError
        """
        if self.schema is None:
            raise Exception("The `schema` property should the set!")
        self.bucket_name = bucket_name
        self.root_path = root_path or ""
        self.rel_path = rel_path or ""
        self.cache_dir = None
        credentials = credentials or {}

        if credentials:
            self.authenticate(**credentials)

        self.bucket = Pathy(f"{self.schema}://{self.bucket_name}")
        # If bucket does not exist, create
        if not self.bucket.exists():
            self.bucket.mkdir(exist_ok=True)

        super().__init__(*args, **kwargs)

    @abstractmethod
    def authenticate(self, *args, **kwargs):
        raise NotImplementedError("Method authenticate is not implemented!")

    def _get_file(self: "CloudStorage", filename: Union[Pathy, str]) -> Pathy:
        """Get file from path.

        By concept, the path is always relative to the root directory, thus
        `rel_path` + initial filename, when used in string representation.

        :param filename: File name.
        :return Pathy: File object.
        """
        # if isinstance(filename, str):
        #     file = self.bucket / self.root_path / filename
        # else:
        #     file = filename
        # return file
        if isinstance(filename, Pathy):
            return filename
        if isinstance(filename, str) and filename.startswith(
            f"{self.schema}://"
        ):
            return Pathy(filename)
        return self.bucket / self.root_path / filename

    def generate_filename(
        self: "CloudStorage",
        extension: str,
        prefix: Optional[str] = None,
        basename: Optional[str] = None,
    ) -> Pathy:
        """Generate filename."""
        if not extension:
            raise Exception("Extension shall be given!")

        if not basename:
            basename = self.generate_basename(prefix)

        return (
            self.bucket
            / self.root_path
            / self.rel_path
            / f"{basename}.{extension}"
        )

    def write_text(
        self: "CloudStorage",
        filename: Union[Pathy, str],
        data: str,
        encoding: Optional[str] = None,
    ) -> int:
        """Write text."""
        file = self._get_file(filename)
        return file.write_text(data, encoding)

    def write_bytes(
        self: "CloudStorage",
        filename: Union[Pathy, str],
        data: bytes,
    ) -> int:
        """Write bytes."""
        file = self._get_file(filename)
        return file.write_bytes(data)

    def exists(self: "CloudStorage", filename: Union[Pathy, str]) -> bool:
        """Check if file exists."""
        file = self._get_file(filename)
        return file.exists()

    def relpath(self: "CloudStorage", filename: Pathy) -> str:
        """Return relative path."""
        file = self._get_file(filename)
        return str(file.relative_to(self.bucket / self.root_path))

    def abspath(self: "CloudStorage", filename: Pathy) -> str:
        """Return absolute path."""
        file = self._get_file(filename)
        return file.as_uri()

    def unlink(self: "CloudStorage", filename: Union[Pathy, str]) -> None:
        """Delete the file."""
        file = self._get_file(filename)
        file.unlink()


class LocalFileSystemStorage(CloudStorage):
    """Local FileSystem Storage.

    Usage example:

    .. code-block:: python

        from fakepy.pathy_storage.cloud import LocalFileSystemStorage

        storage = LocalFileSystemStorage(bucket_name="artur-testing-1")
        file = storage.generate_filename(prefix="zzz_", extension="txt")
        storage.write_text(file, "Lorem ipsum")
        storage.write_bytes(file, b"Lorem ipsum")
    """

    schema: str = "file"

    if not IS_LEGACY_PATHY_VERSION:

        def abspath(self: "LocalFileSystemStorage", filename: Pathy) -> str:
            """Override `abspath` for local storage.

            Instead of calling `as_uri()`, manually construct the absolute URI.
            """
            # Use the storage components to build the absolute URI.
            parts = [self.bucket_name]
            if self.root_path:
                parts.append(self.root_path)
            if self.rel_path:
                parts.append(self.rel_path)
            # Here we use filename.name as the final part.
            parts.append(filename.name)
            return "file://" + "/".join(parts)

    def authenticate(self: "LocalFileSystemStorage", **kwargs) -> None:
        """Authenticate. Does nothing."""


PathyFileSystemStorage = LocalFileSystemStorage
