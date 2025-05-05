from gwcloud_python.utils.file_upload import check_file
import pytest
from tempfile import NamedTemporaryFile, TemporaryDirectory
from pathlib import Path


def test_get_endpoint_from_uploaded():
    with TemporaryDirectory() as tmp_dir:
        with NamedTemporaryFile(dir=tmp_dir) as test_file:
            file_name = check_file(test_file.name)
            assert file_name == Path(test_file.name)

        with pytest.raises(Exception):
            check_file(tmp_dir / 'nonexistant')
