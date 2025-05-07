import pytest
from rucio.client.downloadclient import DownloadClient
from rucio.client.replicaclient import ReplicaClient
from rucio.client.uploadclient import UploadClient

TEST_RSE = "STORAGE-1"


@pytest.mark.usefixtures("_auth_proxy")
@pytest.mark.verifies_requirement("C-BDMS-0330")
def test_file_localization(test_scope, tmp_path):
    """
    Test that a file ingested in Rucio can be correctly localized using the list-replicas command.
    """
    # Create a dummy file
    file_name = "file_with_localization_test.txt"
    lfn = f"/example.namespace/{test_scope}/{file_name}"
    path = tmp_path / file_name
    path.write_text("Test content for file localization")

    # Upload the file to Rucio
    upload_client = UploadClient()
    upload_spec = {
        "path": path,
        "rse": TEST_RSE,
        "did_scope": test_scope,
        "did_name": lfn,
    }
    # Uploading the file
    assert upload_client.upload([upload_spec]) == 0, "File upload failed"

    # Verify file localization using list-replicas
    replica_client = ReplicaClient()
    replicas = list(replica_client.list_replicas([{"scope": test_scope, "name": lfn}]))
    assert len(replicas) == 1, f"Expected 1 replica, found {len(replicas)}"

    replica = replicas[0]
    assert replica["name"] == lfn, f"Replica name mismatch: {replica['name']} != {lfn}"
    assert TEST_RSE in replica["rses"], f"Replica not found in RSE {TEST_RSE}"

    # Validate PFN and download the file
    pfns = replica["rses"][TEST_RSE]
    assert len(pfns) > 0, "No PFNs returned for the replica"
    pfn = list(pfns)[0]  # Extract the first PFN as a string

    # Log the PFN for debugging
    print(f"Using PFN: {pfn}")

    # Prepare the input for download_pfns
    download_spec = {
        "pfn": pfn,
        "did": f"{test_scope}:{lfn}",
        "base_dir": str(tmp_path),  # Ensure `dir` is correctly set
        "rse": TEST_RSE,  # Add `rse` if required by your Rucio setup
        "no_subdir": True,
    }

    # Download the file using PFN
    download_client = DownloadClient()
    download_client.download_pfns([download_spec])

    # Verify the contents of the downloaded file
    download_path = (
        tmp_path / file_name
    )  # The downloaded file should match the original name
    assert download_path.exists(), f"Downloaded file does not exist at {download_path}"
    downloaded_content = download_path.read_text()
    original_content = path.read_text()
    assert downloaded_content == original_content, (
        f"Downloaded file content does not match the original. "
        f"Expected: {original_content}, Got: {downloaded_content}"
    )
