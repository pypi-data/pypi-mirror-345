import os
import subprocess as sp
from datetime import datetime
from pathlib import Path
from secrets import token_hex

import pytest
from rucio.client.rseclient import RSEClient

from .conftest import STORAGE_HOSTNAME, STORAGE_PROTOCOL

# Constants for RSEs and expected attributes
RSE_CONFIG = {
    "STORAGE-1": {"ONSITE": True, "OFFSITE": None},
    "STORAGE-2": {"ONSITE": None, "OFFSITE": True},
    "STORAGE-3": {"ONSITE": None, "OFFSITE": True},
}


def test_shared_storage(storage_mount_path: Path) -> Path:
    """Ensure shared storage directory exists before any test runs"""
    assert (
        storage_mount_path.exists()
    ), f"Shared storage {storage_mount_path} is not available on the client"


@pytest.fixture(scope="session")
def test_file(storage_mount_path, test_scope) -> tuple[Path, str]:
    """Create a test file in the shared storage and return its path and content"""
    unique_id = f"{datetime.now():%Y%m%d_%H%M%S}_{token_hex(8)}"
    test_file_name = f"/ctao.dpps.test/{test_scope}/testfile_{unique_id}.txt"
    test_file_path = storage_mount_path / test_file_name.lstrip("/")
    test_file_content = f"This is a test file {unique_id}"
    test_file_path.parent.mkdir(parents=True, exist_ok=True)
    test_file_path.write_text(test_file_content)
    assert test_file_path.exists(), f"Test file {test_file_path} was not created successfully at {storage_mount_path}"

    return test_file_name, test_file_content


def test_file_access_from_onsite_storage_using_gfal(test_file: tuple[Path, str]):
    """Verify that the file is accessible from the onsite storage pod using gfal-ls"""
    test_file_lfn, _ = test_file
    test_file_name = os.path.basename(test_file_lfn)

    gfal_url = f"{STORAGE_PROTOCOL}://{STORAGE_HOSTNAME}/rucio{test_file_lfn}"
    cmd = ["gfal-ls", gfal_url]
    try:
        output = sp.run(cmd, capture_output=True, text=True, check=True)
        debug = True  # Adjust as needed
        if debug:
            print(f"GFAL Output: {output.stdout.strip()}")
        stdout = output.stdout.strip()
    except sp.CalledProcessError as e:
        pytest.fail(
            f"gfal-ls failed for {gfal_url}:\nSTDERR: {e.stderr.strip()}\nSTDOUT: {e.stdout.strip()}"
        )

    assert any(
        test_file_name in line for line in stdout.splitlines()
    ), f"File {test_file_name} not accessible; gfal-ls output: {stdout!r}"


@pytest.mark.usefixtures("_auth_proxy")
def test_rse_attributes():
    """Verify onsite and offsite RSE attributes set by setup_rucio.sh during the bootstrap job deployment

    Ensures:
    - STORAGE-1 has onsite=True and no offsite=True
    - STORAGE-2 and STORAGE-3 have offsite=True and no onsite=True

    Raises:
        pytest.fail: If RSE details cannot be retrieved (in case of RSEs not found or Rucio server connectivity issues)
        AssertionError: If attribute values don't match the expected ones
    """

    rse_client = RSEClient()

    for rse_name, expected_attrs in RSE_CONFIG.items():
        try:
            # Verify RSE exists
            rse_details = rse_client.get_rse(rse_name)
            print(f"{rse_name} metadata: {rse_details}")

            # Fetch attributes
            attrs = rse_client.list_rse_attributes(rse_name)
            print(f"{rse_name} attributes: {attrs}")

            # Verify RSE onsite attribute
            onsite_value = attrs.get("ONSITE")
            expected_onsite = expected_attrs["ONSITE"]
            assert onsite_value == expected_onsite, (
                f"{rse_name} onsite attribute mismatch: "
                f"expected {expected_onsite!r}, got {onsite_value!r}. "
                f"Full attributes: {attrs}"
            )

            # Verify RSE offsite attribute
            offsite_value = attrs.get("OFFSITE")
            expected_offsite = expected_attrs["OFFSITE"]
            if expected_offsite is None:
                assert offsite_value is not True, (
                    f"{rse_name} should not have offsite=True, "
                    f"got {offsite_value!r}. Full attributes: {attrs}"
                )
            else:
                assert offsite_value == expected_offsite, (
                    f"{rse_name} offsite attribute mismatch: "
                    f"expected {expected_offsite!r}, got {offsite_value!r}. "
                    f"Full attributes: {attrs}"
                )

            print(f"{rse_name} passed attribute tests")

        except Exception as e:
            pytest.fail(
                f"Failed to retrieve RSE details for {rse_name}: {str(e)}. "
                "Check Rucio server connectivity or RSE existence"
            )
