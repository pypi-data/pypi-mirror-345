import zlib

import pytest
from rucio.client import Client
from rucio.client.downloadclient import DownloadClient
from rucio.client.uploadclient import UploadClient


@pytest.fixture(scope="session")
def generic_data_product(_auth_proxy, test_vo, test_scope, tmp_path_factory):
    """A generic test data product ingested into the BDMS.

    Used to fulfill precondition of an existing data product for query and retrieve
    tests and part the implementation part of UC-110-1.1.3.

    Returns
    -------
    lfn: str
        the lfn of the test file
    content: str
        content of the file
    checksum: str
        adler32 checksum as hex string
    """
    name = "test_lfn"
    lfn = f"/{test_vo}/{test_scope}/{name}"
    path = tmp_path_factory.mktemp("upload") / name
    content = "A wizard is never late"
    path.write_text(content)
    checksum = f"{zlib.adler32(content.encode('utf-8')):x}"

    upload_spec = {
        "path": path,
        "rse": "STORAGE-2",
        "did_scope": test_scope,
        "did_name": lfn,
    }

    # upload, this is part of UC 110-1.1.3
    upload_client = UploadClient()
    # 0 means success
    assert upload_client.upload([upload_spec]) == 0
    return lfn, content, checksum


@pytest.mark.verifies_usecase("DPPS-UC-110-1.1.3")
@pytest.mark.verifies_usecase("DPPS-UC-110-1.2.1")
def test_query_by_lfn(test_scope, generic_data_product):
    """
    Test for getting the metadata of a product by LFN.

    Ingestion of the generic data product is executed in the fixture.

    Performing UC-110-1.2.1 is part of the postconditions of UC-110-1.1.3,
    so we use the same test to verify both usecases.
    """
    test_lfn, _, expected_checksum = generic_data_product

    # 1. We select the "test_lfn"
    # 2. - 5. metadata query and execution
    client = Client()
    meta = client.get_metadata(test_scope, test_lfn)
    # 6. verify expectations
    assert meta["adler32"] == expected_checksum


@pytest.mark.verifies_usecase("DPPS-UC-110-1.1.3")
@pytest.mark.verifies_usecase("DPPS-UC-110-1.3.1")
@pytest.mark.usefixtures("_auth_proxy")
def test_retrieve_by_lfn(test_scope, generic_data_product, tmp_path):
    """
    Test for retrieving product by LFN.

    Ingestion of the generic data product is executed in the fixture.

    Performing UC-110-1.3.1 is part of the postconditions of UC-110-1.1.3,
    so we use the same test to verify both usecases.
    """
    test_lfn, expected_content, _ = generic_data_product

    # 1. is done by using the "auth_proxy" fixture
    # 2. - 3. download query and execution
    query = [{"did": f"{test_scope}:{test_lfn}", "base_dir": tmp_path}]
    download_client = DownloadClient()
    download_client.download_dids(query)

    # 4. inspect data product
    expected_path = tmp_path / test_scope / test_lfn.lstrip("/")
    assert expected_path.is_file(), "File not downloaded to expected location"
    assert expected_path.read_text() == expected_content
