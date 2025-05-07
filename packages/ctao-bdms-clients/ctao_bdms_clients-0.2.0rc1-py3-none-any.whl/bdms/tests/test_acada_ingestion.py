"""Tests for onsite ingestion and replication into the BDMS system using the IngestionClient.

This module contains tests for the IngestionClient class, focusing on the conversion of ACADA paths to Logical File Names (LFNs), the registration of replicas in Rucio,
and the replication of data between Rucio storage elements (RSEs).
"""

import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from secrets import token_hex

import pytest
from astropy.io import fits
from astropy.table import Table
from rucio.client import Client
from rucio.client.downloadclient import DownloadClient
from rucio.client.replicaclient import ReplicaClient
from rucio.client.ruleclient import RuleClient
from rucio.common.exception import RucioException
from rucio.common.utils import adler32

from bdms.acada_ingestion import IngestionClient
from bdms.tests.utils import wait_for_replication_status

LOGGER = logging.getLogger(__name__)

XROOTD_UID = 994
XROOTD_GID = 994
ONSITE_RSE = "STORAGE-1"
OFFSITE_RSE_1 = "STORAGE-2"
OFFSITE_RSE_2 = "STORAGE-3"


def test_shared_storage(storage_mount_path: Path):
    """Test that the shared storage path is available."""

    assert (
        storage_mount_path.exists()
    ), f"Shared storage {storage_mount_path} is not available on the client"


def recursive_chown(path: Path, uid: int, gid: int):
    """Equivalent of unix chmod -R <uid>:<gid> <path>."""
    for root, dirs, files in os.walk(path):
        root = Path(root)
        for d in dirs:
            os.chown(root / d, uid, gid)
        for f in files:
            os.chown(root / f, uid, gid)


def trigger_judge_repairer() -> None:
    """Trigger the rucio-judge-repairer daemon to run once and fix any STUCK rules."""

    try:
        cmd = [
            "./kubectl",
            "exec",
            "deployment/bdms-judge-evaluator",
            "--",
            "/usr/local/bin/rucio-judge-repairer",
            "--run-once",
        ]
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        LOGGER.info("Triggered rucio-judge-repairer daemon: %s", result.stdout)
    except FileNotFoundError as e:
        LOGGER.error("kubectl command not found: %s", str(e))
        raise RuntimeError(
            "kubectl command not found. Ensure kubectl is in the PATH or working directory."
        ) from e
    except subprocess.CalledProcessError as e:
        LOGGER.error("Failed to trigger rucio-judge-repairer daemon: %s", e.stderr)
        raise


@pytest.fixture
def test_file(
    storage_mount_path: Path, test_scope: str, test_vo: str
) -> tuple[Path, str]:
    """Create a dummy .fits.fz file in the shared storage for testing."""

    unique_id = f"{datetime.now():%Y%m%d_%H%M%S}_{token_hex(8)}"
    filename = f"testfile_{unique_id}.fits.fz"

    test_file_path = storage_mount_path / test_vo / test_scope / filename
    test_file_path.parent.mkdir(parents=True, exist_ok=True)

    # need to change file permissions of created directories so that
    # the xrootd still can read and write there
    recursive_chown(storage_mount_path / test_vo, XROOTD_UID, XROOTD_GID)

    # Write a small test content (simulating a .fits.fz file with minimal content for testing)
    test_file_content = f"FITS-like content for {unique_id}"
    test_file_path.write_text(test_file_content)
    os.chown(test_file_path, XROOTD_UID, XROOTD_GID)

    return test_file_path, test_file_content


def test_acada_to_lfn(storage_mount_path: Path, test_vo: str):
    """Test the acada_to_lfn method of IngestionClient with valid and invalid inputs."""

    ingestion_client = IngestionClient(storage_mount_path, ONSITE_RSE, vo=test_vo)

    # Test Case 1: valid acada_path
    acada_path = (
        f"{ingestion_client.data_path}/{ingestion_client.vo}/{ingestion_client.scope}/DL0/LSTN-01/events/2023/10/13/"
        "Subarray_SWAT_sbid008_obid00081_0.fits.fz"
    )

    expected_lfn = (
        f"/{ingestion_client.vo}/{ingestion_client.scope}/DL0/LSTN-01/events/2023/10/13/"
        "Subarray_SWAT_sbid008_obid00081_0.fits.fz"
    )
    lfn = ingestion_client.acada_to_lfn(acada_path=acada_path)

    assert lfn == expected_lfn, f"Expected {expected_lfn}, got {lfn}"

    # Test Case 2: Non-absolute acada_path (empty string)
    with pytest.raises(ValueError, match="acada_path must be absolute"):
        ingestion_client.acada_to_lfn(acada_path="")

    # Test Case 3: Non-absolute acada_path (relative path)
    with pytest.raises(ValueError, match="acada_path must be absolute"):
        ingestion_client.acada_to_lfn(acada_path="./test.fits")

    # Test Case 4: acada_path not within data_path
    invalid_acada_path = "/invalid/path/file.fits.fz"
    with pytest.raises(ValueError, match="is not within data_path"):
        ingestion_client.acada_to_lfn(acada_path=invalid_acada_path)

    # Test Case 5: acada_path does not start with <vo>/<scope>
    wrong_prefix_path = (
        f"{ingestion_client.data_path}/wrong_vo/wrong_scope/DL0/LSTN-01/file.fits.fz"
    )
    with pytest.raises(ValueError, match="must start with"):
        ingestion_client.acada_to_lfn(acada_path=wrong_prefix_path)

    # Test Case 6: acada_path starts with <vo> but wrong <scope>
    wrong_scope_path = f"{ingestion_client.data_path}/{ingestion_client.vo}/wrong_scope/DL0/LSTN-01/file.fits.fz"
    with pytest.raises(ValueError, match="must start with"):
        ingestion_client.acada_to_lfn(acada_path=wrong_scope_path)


@pytest.mark.usefixtures("_auth_proxy")
def test_check_replica_exists(
    storage_mount_path: Path, test_scope: str, test_file: tuple[Path, str], test_vo: str
):
    """Test the check_replica_exists method of IngestionClient."""

    ingestion_client = IngestionClient(
        storage_mount_path, ONSITE_RSE, scope=test_scope, vo=test_vo
    )

    acada_path, _ = test_file

    # Generate the LFN
    lfn = ingestion_client.acada_to_lfn(acada_path)

    # Test Case 1: No replica exists yet
    msg = f"Expected no replica for LFN {lfn} before registration"
    assert not ingestion_client.check_replica_exists(lfn), msg

    # Register the replica in Rucio
    ingestion_client.add_onsite_replica(acada_path)

    # Test Case 2: Replica exists with a valid PFN
    msg = f"Expected replica to exist for LFN {lfn} after registration"
    assert ingestion_client.check_replica_exists(lfn), msg

    # Test Case 3: Non-existent LFN
    nonexistent_lfn = lfn + ".nonexistent"
    msg = f"Expected no replica for nonexistent LFN {nonexistent_lfn}"
    assert not ingestion_client.check_replica_exists(nonexistent_lfn), msg


@pytest.mark.usefixtures("_auth_proxy")
@pytest.mark.verifies_usecase("UC-110-1.1.1")
def test_add_onsite_replica_with_dummy_file(
    test_file: tuple[Path, str],
    test_scope: str,
    tmp_path: Path,
    storage_mount_path,
    test_vo: str,
    caplog,
):
    """Test the add_onsite_replica method of IngestionClient using a dummy file."""

    ingestion_client = IngestionClient(
        storage_mount_path, ONSITE_RSE, scope=test_scope, vo=test_vo
    )

    acada_path, test_file_content = test_file
    # Use add_onsite_replica to register the replica
    lfn = ingestion_client.add_onsite_replica(acada_path=acada_path)

    # Verify the LFN matches the expected LFN
    expected_lfn = ingestion_client.acada_to_lfn(acada_path)
    assert lfn == expected_lfn, f"Expected LFN {expected_lfn}, got {lfn}"

    # Download the file using the LFN
    download_spec = {
        "did": f"{ingestion_client.scope}:{lfn}",
        "base_dir": str(tmp_path),
        "no_subdir": True,
    }
    download_client = DownloadClient()
    download_client.download_dids([download_spec])

    # Verify the downloaded file
    download_path = tmp_path / lfn.lstrip("/")
    assert download_path.is_file(), f"Download failed at {download_path}"

    downloaded_content = download_path.read_text()
    assert downloaded_content == test_file_content, (
        f"Downloaded file content does not match the original. "
        f"Expected: {test_file_content}, Got: {downloaded_content}"
    )

    # Check for don't ingest again if its already registered
    caplog.clear()
    lfn = ingestion_client.add_onsite_replica(acada_path=acada_path)
    assert f"Replica already exists for lfn '{lfn}', skipping" in [
        r.message for r in caplog.records
    ]


def test_rses():
    """Test that the expected RSEs are configured."""
    client = Client()
    result = list(client.list_rses())

    rses = [r["rse"] for r in result]
    assert ONSITE_RSE in rses, f"Expected RSE {ONSITE_RSE} not found in {rses}"
    assert OFFSITE_RSE_1 in rses, f"Expected RSE {OFFSITE_RSE_1} not found in {rses}"
    assert OFFSITE_RSE_2 in rses, f"Expected RSE {OFFSITE_RSE_2} not found in {rses}"


@pytest.fixture
def pre_existing_lfn(
    test_file: tuple[Path, str],
    test_scope: str,
    test_vo: str,
) -> str:
    """Fixture to provide an LFN for a replica pre-registered in Rucio without using IngestionClient."""

    # Construct the LFN manually based on the test file and scope
    acada_path, _ = test_file
    relative_path = str(acada_path).split(f"{test_vo}/{test_scope}/", 1)[-1]
    lfn = f"/{test_vo}/{test_scope}/{relative_path}"
    checksum = adler32(acada_path)

    # Construct the DID
    did = {"scope": test_scope, "name": lfn}

    # Register the replica directly using ReplicaClient
    replica_client = ReplicaClient()
    replica = {
        "scope": test_scope,
        "name": lfn,
        "bytes": acada_path.stat().st_size,  # File size
        "adler32": checksum,
    }
    try:
        replica_client.add_replicas(rse=ONSITE_RSE, files=[replica])
    except RucioException as e:
        LOGGER.error(
            "Failed to pre-register replica for LFN %s on %s: %s",
            lfn,
            ONSITE_RSE,
            str(e),
        )
        raise

    # Verify the replica is registered
    replicas = list(replica_client.list_replicas(dids=[did]))
    assert (
        replicas
    ), f"Failed to verify pre-registration of replica for LFN {lfn} on {ONSITE_RSE}"

    return lfn


@pytest.mark.usefixtures("_auth_proxy")
@pytest.mark.verifies_usecase("UC-110-1.6")
def test_add_offsite_replication_rules(
    pre_existing_lfn: str,
    test_scope: str,
    test_vo: str,
    storage_mount_path: Path,
    tmp_path: Path,
    test_file: tuple[Path, str],
    caplog,
):
    """Test the add_offsite_replication_rules method of IngestionClient."""
    ingestion_client = IngestionClient(
        storage_mount_path, ONSITE_RSE, scope=test_scope, vo=test_vo
    )
    caplog.set_level(logging.DEBUG)

    # Replicate the ACADA file to two offsite RSEs
    lfn = pre_existing_lfn
    did = {"scope": test_scope, "name": lfn}

    _, test_file_content = test_file  # Get the test file content

    offsite_rse_expression = "OFFSITE"
    copies = 2
    rule_ids = ingestion_client.add_offsite_replication_rules(
        lfn=lfn,
        offsite_rse_expression=offsite_rse_expression,
        copies=copies,
        lifetime=None,
    )

    rule_id_offsite_1 = rule_ids[0]
    rule_id_offsite_2 = rule_ids[1]
    rule_client = RuleClient()

    # Wait for the first offsite rule to complete (OFFSITE_RSE_1)
    wait_for_replication_status(rule_client, rule_id_offsite_1, expected_status="OK")

    # Verify the replica exists on either OFFSITE_RSE_1 or OFFSITE_RSE_2 after the first rule
    replica_client = ReplicaClient()
    replicas = next(replica_client.list_replicas(dids=[did]))
    states = replicas.get("states", {})
    assert (
        states.get(OFFSITE_RSE_1) == "AVAILABLE"
        or states.get(OFFSITE_RSE_2) == "AVAILABLE"
    ), f"Expected replica on either {OFFSITE_RSE_1} or {OFFSITE_RSE_2} to be AVAILABLE after first rule: {states}"

    # Manually trigger the judge-repairer to ensure the second rule doesn't get stuck
    trigger_judge_repairer()

    # Wait for the second offsite rule to complete (OFFSITE_RSE_2)
    wait_for_replication_status(rule_client, rule_id_offsite_2, expected_status="OK")

    # Verify the replica exists on all RSEs
    replica_client = ReplicaClient()
    replicas = next(replica_client.list_replicas(dids=[did]))
    states = replicas.get("states", {})
    LOGGER.info(
        "Replica states for DID %s in test_replicate_acada_data_to_offsite: %s",
        did,
        states,
    )
    assert (
        states.get(ONSITE_RSE) == "AVAILABLE"
    ), f"Expected replica on {ONSITE_RSE} to be AVAILABLE: {states}"
    assert (
        states.get(OFFSITE_RSE_1) == "AVAILABLE"
    ), f"Expected replica on {OFFSITE_RSE_1} to be AVAILABLE: {states}"
    assert (
        states.get(OFFSITE_RSE_2) == "AVAILABLE"
    ), f"Expected replica on {OFFSITE_RSE_2} to be AVAILABLE: {states}"

    # Download the file from OFFSITE_RSE_2 to verify its content
    download_spec = {
        "did": f"{test_scope}:{lfn}",
        "base_dir": str(tmp_path),
        "no_subdir": True,
        "rse": OFFSITE_RSE_2,
    }
    download_client = DownloadClient()
    download_client.download_dids([download_spec])

    # Verify the downloaded file content
    download_path = tmp_path / lfn.lstrip("/")
    assert download_path.is_file(), f"Download failed at {download_path}"
    downloaded_content = download_path.read_text()
    assert downloaded_content == test_file_content, (
        f"Downloaded file content does not match the original. "
        f"Expected: {test_file_content}, Got: {downloaded_content}"
    )


@pytest.mark.usefixtures("_auth_proxy")
@pytest.mark.verifies_usecase("UC-110-1.6")
def test_add_offsite_replication_rules_single_copy(
    pre_existing_lfn: str,
    test_scope: str,
    test_vo: str,
    storage_mount_path: Path,
    tmp_path: Path,
    test_file: tuple[Path, str],
    caplog,
):
    """Test the add_offsite_replication_rules method of IngestionClient with a single copy (copies=1)."""
    ingestion_client = IngestionClient(
        storage_mount_path, ONSITE_RSE, scope=test_scope, vo=test_vo
    )
    caplog.set_level(logging.DEBUG)

    # Replicate the ACADA file to one offsite RSE
    lfn = pre_existing_lfn
    did = {"scope": test_scope, "name": lfn}

    _, test_file_content = test_file

    offsite_rse_expression = "OFFSITE"
    copies = 1
    rule_ids = ingestion_client.add_offsite_replication_rules(
        lfn=lfn,
        offsite_rse_expression=offsite_rse_expression,
        copies=copies,
        lifetime=None,
    )

    # Verify that only one rule was created
    assert (
        len(rule_ids) == 1
    ), f"Expected exactly 1 rule ID, got {len(rule_ids)}: {rule_ids}"
    rule_id_offsite_1 = rule_ids[0]
    rule_client = RuleClient()

    # Wait for the offsite rule to complete
    wait_for_replication_status(rule_client, rule_id_offsite_1, expected_status="OK")

    # Verify the replica exists on exactly one of the offsite RSEs (either OFFSITE_RSE_1 or OFFSITE_RSE_2)
    replica_client = ReplicaClient()
    replicas = next(replica_client.list_replicas(dids=[did]))
    states = replicas.get("states", {})
    LOGGER.info(
        "Replica states for DID %s in test_add_offsite_replication_rules_single_copy: %s",
        did,
        states,
    )
    # Check that the replica exists on exactly one offsite RSE
    offsite_replica_count = sum(
        1 for rse in [OFFSITE_RSE_1, OFFSITE_RSE_2] if states.get(rse) == "AVAILABLE"
    )
    assert (
        offsite_replica_count == 1
    ), f"Expected exactly 1 offsite replica (on either {OFFSITE_RSE_1} or {OFFSITE_RSE_2}), got {offsite_replica_count}: {states}"

    # Determine which offsite RSE the replica was created on
    target_offsite_rse = (
        OFFSITE_RSE_1 if states.get(OFFSITE_RSE_1) == "AVAILABLE" else OFFSITE_RSE_2
    )

    # Download the file from the target offsite RSE to verify its content
    download_spec = {
        "did": f"{test_scope}:{lfn}",
        "base_dir": str(tmp_path),
        "no_subdir": True,
        "rse": target_offsite_rse,
    }
    download_client = DownloadClient()
    download_client.download_dids([download_spec])

    # Verify the downloaded file content
    download_path = tmp_path / lfn.lstrip("/")
    assert download_path.is_file(), f"Download failed at {download_path}"
    downloaded_content = download_path.read_text()
    assert downloaded_content == test_file_content, (
        f"Downloaded file content does not match the original. "
        f"Expected: {test_file_content}, Got: {downloaded_content}"
    )


def test_verify_fits_file(tel_events_test_file):
    from bdms.acada_ingestion import verify_fits_checksum

    with fits.open(tel_events_test_file) as hdul:
        verify_fits_checksum(hdul)


@pytest.fixture
def broken_checksum(tmp_path):
    # create a fits file with a broken checksum
    path = tmp_path / "invalid.fits"

    table = Table({"foo": [1, 2, 3], "bar": [4.0, 5.0, 6.0]})
    hdul = fits.HDUList([fits.PrimaryHDU(), fits.BinTableHDU(table)])
    hdul.writeto(path, checksum=True)

    # break it
    with path.open("rb+") as f:
        # FITS files are stored in blocks of 2880 bytes
        # first chunk should be the primary header
        # second chunk the header of the bintable
        # third chunk the payload of the bintable
        # we write garbage somewhere into the payload of the table
        f.seek(2 * 2880 + 10)
        f.write(b"\x12\x34\xff")
    return path


def test_verify_fits_file_invalid_checksum(broken_checksum):
    from bdms.acada_ingestion import FITSVerificationError, verify_fits_checksum

    with fits.open(broken_checksum) as hdul:
        with pytest.raises(FITSVerificationError, match="CHECKSUM verification failed"):
            verify_fits_checksum(hdul)
