import logging
import os
import subprocess as sp
from datetime import datetime
from pathlib import Path
from secrets import token_hex

import pytest
from rucio.client.scopeclient import ScopeClient

from bdms.tests.utils import download_test_file

USER_CERT = os.getenv("RUCIO_CFG_CLIENT_CERT", "/opt/rucio/etc/usercert.pem")
USER_KEY = os.getenv("RUCIO_CFG_CLIENT_KEY", "/opt/rucio/etc/userkey.pem")

# Define on-site storage related variables
STORAGE_MOUNT_PATH = Path(os.getenv("STORAGE_MOUNT_PATH", "/storage-1"))
STORAGE_PROTOCOL = "root"  # e.g., root, davs, gsiftp
STORAGE_HOSTNAME = "rucio-storage-1"  # on-site storage container hostname


def pytest_configure():
    # gfal is overly verbose on info (global default), reduce a bit
    logging.getLogger("gfal2").setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def storage_mount_path():
    """Provide the STORAGE_MOUNT_PATH as a fixture"""
    return STORAGE_MOUNT_PATH


@pytest.fixture(scope="session")
def test_user():
    return "root"


@pytest.fixture(scope="session")
def _auth_proxy(tmp_path_factory):
    """Auth proxy needed for accessing RSEs"""
    # Key has to have 0o600 permissions, but due to the way we
    # we create and mount it, it does not. We copy to a tmp file
    # set correct permissions and then create the proxy
    sp.run(
        [
            "voms-proxy-init",
            "-valid",
            "9999:00",
            "-cert",
            USER_CERT,
            "-key",
            USER_KEY,
        ],
        check=True,
    )


@pytest.fixture(scope="session")
def test_vo():
    return "ctao.dpps.test"


@pytest.fixture(scope="session")
def test_scope(test_user):
    """To avoid name conflicts and old state, use a unique scope for the tests"""
    # length of scope is limited to 25 characters
    random_hash = token_hex(2)
    date_str = f"{datetime.now():%Y%m%d_%H%M%S}"
    scope = f"t_{date_str}_{random_hash}"

    sc = ScopeClient()
    sc.add_scope(test_user, scope)
    return scope


@pytest.fixture(scope="session")
def subarray_test_file():
    """Fixture to download a subarray test file"""
    path = "acada-small/DL0/ARRAY/ctao-n-acada/acada-adh/triggers/2025/02/04/SUB000_SWAT000_20250204T213405_SBID0000000002000000066_OBSID0000000002000000200_SUBARRAY_CHUNK000.fits.fz"
    return download_test_file(path)


@pytest.fixture(scope="session")
def tel_trigger_test_file():
    """Fixture to download a telescope trigger test file"""
    path = "acada-small/DL0/ARRAY/ctao-n-acada/acada-adh/triggers/2025/02/04/SUB000_SWAT000_20250204T213405_SBID0000000002000000066_OBSID0000000002000000200_TEL_CHUNK000.fits.fz"
    return download_test_file(path)


@pytest.fixture(scope="session")
def tel_events_test_file():
    """Fixture to download a telescope events test file"""
    path = "acada-small/DL0/LSTN-01/ctao-n-acada/acada-adh/events/2025/02/04/TEL001_SDH0000_20250204T213354_SBID0000000002000000066_OBSID0000000002000000200_CHUNK000.fits.fz"
    return download_test_file(path)
