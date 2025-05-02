from __future__ import annotations

import logging
import os
import shutil
import time
import zipfile
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from .python_project import PythonProject

if TYPE_CHECKING:
    from typing import Tuple

logger = logging.getLogger(__name__)

class Packager:
    AWS_LAMBDA_MAX_UNZIP_SIZE = 262144000

    def __init__(self, venv_path: Path, project_path: Path, output_dir: Path, output_file: Path | None):
        self.project = PythonProject(project_path)
        self.venv_path = venv_path

        self.output_dir = output_file.parent if output_file else output_dir
        self.output_file = output_file if output_file else output_dir / f'{self.project.distribution_name}.zip'

        self._uncompressed_bytes = 0

    @property
    def input_path(self) -> Path:
        python_paths = list((self.venv_path / 'lib').glob('python*'))
        if not python_paths:
            raise Exception("input_path")
        return python_paths[0] / 'site-packages'

    def package(self) -> None:
        logger.info(f"Packaging: '{self.input_path}' to '{self.output_file}' using '{self.project.path}'... ")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        with NamedTemporaryFile(suffix=".zip") as dependencies_zip:
            self.zip_all_dependencies(Path(dependencies_zip.name))

    def zip_all_dependencies(self, target_path: Path) -> None:
        logger.info(f"Zipping to {target_path}...")

        def date_time() -> Tuple[int, int, int, int, int, int]:
            """Returns date_time value used to force overwrite on all ZipInfo objects. Defaults to
            1980-01-01 00:00:00. You can set this with the environment variable SOURCE_DATE_EPOCH as an
            integer value representing seconds since Epoch.
            """
            source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH", None)
            if source_date_epoch is not None:
                return time.gmtime(int(source_date_epoch))[:6]
            return (1980, 1, 1, 0, 0, 0)

        with zipfile.ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as zip_file:

            def zip_dir(path: Path) -> None:
                for item in path.iterdir():
                    if item.is_dir():
                        zip_dir(item)
                    else:
                        zinfo = zipfile.ZipInfo.from_file(
                            item, item.relative_to(self.input_path)
                        )
                        zinfo.date_time = date_time()
                        zinfo.external_attr = 0o644 << 16
                        self._uncompressed_bytes += item.stat().st_size
                        with (
                            open(item, "rb") as src,
                            zip_file.open(zinfo, "w") as dest,
                        ):
                            shutil.copyfileobj(src, dest, 1024 * 8)

            zip_dir(self.input_path)

        compressed_bytes = target_path.stat().st_size

        logger.info(f"Uncompressed size: {self._uncompressed_bytes:,} bytes. Compressed size: {compressed_bytes:,} bytes.")

        if self._uncompressed_bytes > self.AWS_LAMBDA_MAX_UNZIP_SIZE:
            logger.info(f"The uncompressed size of the ZIP file is greater than the AWS Lambda limit of {self.AWS_LAMBDA_MAX_UNZIP_SIZE:,} bytes.")
            if(compressed_bytes < self.AWS_LAMBDA_MAX_UNZIP_SIZE):
                logger.info(f"The compressed size ({compressed_bytes:,}) is less than the AWS limit, so the nested-zip strategy will be used.")
                self.generate_nested_zip(target_path)
            else:
                print("TODO Error.  The unzipped size it too large for AWS Lambda.")
        else:
            logger.info(f"Copying '{target_path}' to '{self.output_file}'")
            shutil.copy(str(target_path), str(self.output_file))

    def generate_nested_zip(self, inner_zip_path: Path) -> None:
        logger.info(f"Generating nested-zip and __init__.py loader using entrypoint package '{self.project.entrypoint_package_name}'...")

        with zipfile.ZipFile(self.output_file, 'w') as outer_zip_file:
            entrypoint_dir = Path(self.project.entrypoint_package_name)
            outer_zip_file.write(
                inner_zip_path,
                arcname=str(entrypoint_dir / ".dependencies.zip"),
                compresslevel=zipfile.ZIP_STORED
            )
            outer_zip_file.writestr(
                str(entrypoint_dir / "__init__.py"),
                Path(__file__).parent.joinpath("nested_zip_loader.py").read_text(),
                compresslevel=zipfile.ZIP_DEFLATED
            )
