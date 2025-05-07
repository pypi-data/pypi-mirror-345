import pytest
from rucio.client import Client
from rucio.client.client import ReplicaClient, RuleClient
from rucio.client.didclient import DIDClient
from rucio.client.uploadclient import UploadClient

from bdms.tests.utils import wait_for_replication_status


def test_server_version():
    """Test the expected version of rucio is running"""
    client = Client()
    result = client.ping()
    assert result["version"].startswith("35")


def test_authentication():
    """Test we authenticated successfully"""
    client = Client()
    result = client.whoami()

    assert result["account"] == "root"


def test_rses():
    """Test the expected RSEs are configured"""
    client = Client()
    result = list(client.list_rses())

    rses = [r["rse"] for r in result]
    assert "STORAGE-1" in rses
    assert "STORAGE-2" in rses
    assert "STORAGE-3" in rses


def test_add_dataset(test_vo, test_scope):
    """Test adding a simple dataset works"""
    dataset_name = f"/{test_vo}/{test_scope}/dataset_aiv_basic"

    did_client = DIDClient()
    success = did_client.add_dataset(
        scope=test_scope, name=dataset_name, rse="STORAGE-1", lifetime=2
    )
    assert success

    names = list(did_client.list_dids(scope=test_scope, filters={}))
    assert dataset_name in names


@pytest.mark.usefixtures("_auth_proxy")
def test_upload_file(test_vo, test_scope, tmp_path):
    """Test uploading a simple file works"""
    name = "file_aiv_basic"
    path = tmp_path / "file_aiv_basic"
    path.write_text("Hello, World!")
    did_name = f"/{test_vo}/{test_scope}/{name}"

    upload_client = UploadClient()

    upload_spec = {
        "path": path,
        "rse": "STORAGE-2",
        "did_scope": test_scope,
        "did_name": did_name,
    }
    # 0 means success
    assert upload_client.upload([upload_spec]) == 0


"""
@pytest.mark.parametrize(
    "timeout,poll_interval",
    [
        pytest.param(
            60,
            5,
            marks=pytest.mark.xfail(
                reason="sometimes there is an extra 300s timeout somewhere in FTS"
            ),
            id="timeout-60",
        ),
        (600, 5),
    ],
)
"""


@pytest.mark.usefixtures("_auth_proxy")
def test_replication(test_vo, test_scope, tmp_path):
    dataset = "transfer_test"
    path = tmp_path / f"{dataset}.dat"
    path.write_text("I am a test for replication rules.")

    dataset_did = f"/{test_vo}/{test_scope}/{dataset}"
    file_did = f"/{test_vo}/{test_scope}/{dataset}/{path.name}"

    main_rse = "STORAGE-1"
    replica_rse = "STORAGE-2"

    client = Client()
    upload_client = UploadClient()
    did_client = DIDClient()
    rule_client = RuleClient()
    replica_client = ReplicaClient()

    upload_spec = {
        "path": path,
        "rse": main_rse,
        "did_scope": test_scope,
        "did_name": file_did,
    }
    # return value of 0 means success
    assert upload_client.upload([upload_spec]) == 0
    assert did_client.add_dataset(scope=test_scope, name=dataset_did)
    dids = [{"scope": test_scope, "name": file_did}]
    assert client.attach_dids(scope=test_scope, name=dataset_did, dids=dids)

    dids = [{"scope": test_scope, "name": dataset_did}]
    rule = rule_client.add_replication_rule(
        dids=dids, copies=1, rse_expression=replica_rse
    )[0]

    wait_for_replication_status(
        rule_client,
        rule_id=rule,
        expected_status="OK",
        timeout=600,
        poll_interval=5,
    )
    replicas = next(replica_client.list_replicas(dids))
    assert replicas["states"] == {"STORAGE-1": "AVAILABLE", "STORAGE-2": "AVAILABLE"}
