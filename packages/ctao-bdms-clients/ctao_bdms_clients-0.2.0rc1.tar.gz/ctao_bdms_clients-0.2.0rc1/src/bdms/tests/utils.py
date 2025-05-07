"""Utility functions for BDMS tests."""

import logging
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from minio import Minio
from rucio.client.ruleclient import RuleClient
from rucio.common.exception import RucioException

# Default timeout and polling interval (in seconds) for waiting for replication
DEFAULT_TIMEOUT = 1000
DEFAULT_POLL_INTERVAL = 30
LOGGER = logging.getLogger(__name__)


def wait_for_replication_status(
    rule_client: RuleClient,
    rule_id: str,
    expected_status: str = "OK",
    timeout: int = DEFAULT_TIMEOUT,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    logger: logging.Logger = None,
) -> None:
    if logger is None:
        logger = LOGGER

    start_time = time.perf_counter()
    current_status = None
    result = None
    max_retries = 3

    while (time.perf_counter() - start_time) < timeout:
        retries = 0
        while retries < max_retries:
            try:
                result = rule_client.get_replication_rule(rule_id)
                current_status = result["state"]
                break
            except RucioException as e:
                retries += 1
                if retries == max_retries:
                    raise RuntimeError(
                        f"Failed to check replication rule status for rule {rule_id} after {max_retries} retries: {str(e)}"
                    ) from e
                logger.warning(
                    "Failed to check rule %s status (attempt %s/%s): %s. Retrying...",
                    rule_id,
                    retries,
                    max_retries,
                    str(e),
                )
                time.sleep(1)

        if current_status == expected_status:
            logger.info(
                "Replication rule %s reached status '%s'", rule_id, expected_status
            )
            return

        logger.debug(
            "Rule %s is in state %s, waiting for %s (elapsed: %.2f seconds)",
            rule_id,
            current_status,
            expected_status,
            time.perf_counter() - start_time,
        )
        time.sleep(poll_interval)

    msg = (
        f"Replication rule {rule_id} did not reach status '{expected_status}' within {timeout} seconds. "
        f"Current status is '{current_status}'.\nFull output: {result}"
    )
    raise TimeoutError(msg)


TEST_DATA_DIR = Path(os.getenv("BDMS_TEST_DATA_DIR", "test_data")).absolute()


def download_test_file(path):
    """Get a FITS file from the MinIO server"""

    load_dotenv()

    access_key = os.environ["MINIO_ACCESS_KEY"]
    secret_key = os.environ["MINIO_SECRET_KEY"]

    output_path = TEST_DATA_DIR / path

    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not output_path.exists():
        client = Minio(
            "minio-cta.zeuthen.desy.de",
            access_key,
            secret_key,
            secure=True,
        )

        LOGGER.info("Downloading %s", path)
        client.fget_object(
            "dpps-data-private",
            path,
            output_path,
        )

    else:
        LOGGER.info("File %s already exists, skipping download", output_path)

    return output_path
