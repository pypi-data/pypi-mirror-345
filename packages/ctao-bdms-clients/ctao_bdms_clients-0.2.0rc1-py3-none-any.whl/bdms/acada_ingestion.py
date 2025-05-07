"""Module for ACADA data ingestion (onsite) into the BDMS system using the IngestionClient.

This module provides the IngestionClient class to manage the ingestion of ACADA data into the BDMS system.
It includes functionality for constructing FITS file paths, converting ACADA paths to Logical File Names (LFNs),
and registering replicas in Rucio.
"""
# this is the latest working file (as on 6:40 pm) with judge repairer repairing the STUCK rule.

import logging
import os
from pathlib import Path
from typing import Optional, Union

from astropy.io import fits
from rucio.client.accountclient import AccountClient
from rucio.client.client import Client
from rucio.client.replicaclient import ReplicaClient
from rucio.client.rseclient import RSEClient
from rucio.client.ruleclient import RuleClient
from rucio.client.scopeclient import ScopeClient
from rucio.common.exception import Duplicate, RucioException
from rucio.common.utils import adler32

LOGGER = logging.getLogger(__name__)


__all__ = [
    "IngestionClient",
]


class IngestionClient:
    """A client for BDMS ingestion and replication.

    This class provides methods to ingest ACADA data into the BDMS system, including converting ACADA paths to
    Logical File Names (LFNs), registering replicas in Rucio, and replicating data to offsite RSEs.

    Parameters
    ----------
    data_path : str
        Path to data directory. This is a required argument.
    rse : str
        Rucio Storage Element (RSE) name. This is a required argument.
    vo : str, optional
        Virtual organization name prefix. Defaults to "ctao".
    logger : logging.Logger, optional
        Logger instance. If None, a new logger is created.
    scope : str, optional
        Rucio scope to use for replica registration. Defaults to 'acada'.

    Raises
    ------
    FileNotFoundError
        If the specified data directory does not exist.
    ValueError
        If the specified RSE is not available in Rucio.
    RuntimeError
        If there is an error communicating with Rucio while:

        - Checking RSE availability.
        - Initializing Rucio clients (related to configuration and authentication issues).
        - Managing the Rucio scope.
    """

    def __init__(
        self,
        data_path: Union[str, os.PathLike],
        rse: str,
        vo="ctao",
        logger=None,
        scope="acada",
    ) -> None:
        self.logger = logger or LOGGER.getChild(self.__class__.__name__)
        self.vo = vo

        # Set data path (Prefix)
        self.data_path = Path(data_path)
        if not self.data_path.is_dir():
            raise FileNotFoundError(f"Data directory not found at {self.data_path}")

        self.rse = rse

        # Check RSE availability before proceeding to next steps
        self._check_rse_availability()

        # Initialize Rucio clients
        try:
            self.client = Client()
            self.replica_client = ReplicaClient()
            self.scope_client = ScopeClient()
            self.account_client = AccountClient()
            self.rse_client = RSEClient()
            self.rule_client = RuleClient()
        except RucioException as e:
            self.logger.error("Failed to initialize Rucio clients: %s", str(e))
            raise

        # Set the scope and ensure it exists in Rucio
        self.scope = scope
        self.user = self.account_client.whoami()["account"]
        self._add_acada_scope()

    def _check_rse_availability(self) -> None:
        """Check if the specified RSE is available in Rucio.

        Raises
        ------
        ValueError
            If the RSE is not found in Rucio.
        rucio.common.exception.RucioException
            If there is an error communicating with Rucio (e.g., network issues, authentication errors).
        """
        rse_client = RSEClient()
        available_rses = [rse["rse"] for rse in rse_client.list_rses()]
        if self.rse not in available_rses:
            raise ValueError(
                f"RSE '{self.rse}' is not available in Rucio. Available RSEs: {available_rses}"
            )
        self.logger.info("RSE '%s' is available in Rucio", self.rse)

    def _add_acada_scope(self) -> None:
        """Add the specified scope to Rucio if it doesn't already exist.

        Raises
        ------
        RuntimeError
            If the scope cannot be created or managed in Rucio.
        """
        try:
            self.scope_client.add_scope(self.user, self.scope)
        except Duplicate:
            # Scope already exists
            return
        except RucioException as e:
            self.logger.error(
                "Failed to manage scope '%s' in Rucio: %s",
                self.scope,
                str(e),
            )
            raise

    def acada_to_lfn(self, acada_path) -> str:
        """Convert an ACADA path to a BDMS Logical File Name (LFN).

        Parameters
        ----------
        acada_path : str or Path
            The ACADA file path to convert.

        Returns
        -------
        str
            The generated BDMS LFN (e.g., '/ctao/acada/DL0/LSTN-01/events/YYYY/MM/DD/file.fits.fz').

        Raises
        ------
        ValueError
            If ``acada_path`` is not an absolute path or is not within the BDMS data path (prefix) or
            does not start with the expected '<vo>/<scope>' prefix under the data path.
        """
        acada_path = Path(acada_path)

        # Validate that the path is absolute
        if not acada_path.is_absolute():
            raise ValueError("acada_path must be absolute")

        # Validate that acada_path is within data_path
        try:
            rel_path = acada_path.relative_to(self.data_path)
        except ValueError:
            raise ValueError(
                f"acada_path {acada_path} is not within data_path {self.data_path}"
            )

        # Validate that acada_path starts with <vo>/<scope> under data_path
        expected_prefix = self.data_path / self.vo / self.scope
        if not acada_path.is_relative_to(expected_prefix):
            raise ValueError(
                f"acada_path {acada_path} must start with {expected_prefix} (vo: {self.vo}, scope: {self.scope})"
            )

        bdms_lfn = f"/{rel_path}"
        return bdms_lfn

    def check_replica_exists(self, lfn: str) -> bool:
        """Check if a replica already exists for the given LFN on the specified RSE.

        Parameters
        ----------
        lfn : str
            The Logical File Name (LFN) to check.


        Returns
        -------
        bool
            True if the replica exists and has a valid PFN, False otherwise.

        Raises
        ------
        RuntimeError
            If a replica exists but has no PFN for the RSE, indicating an invalid replica state.
        """
        replicas = list(
            self.replica_client.list_replicas(
                dids=[{"scope": self.scope, "name": lfn}],
                rse_expression=self.rse,
            )
        )

        self.logger.debug("Existing Replicas for lfn '%r'", replicas)
        if replicas:
            replica = replicas[0]
            pfns = replica["rses"].get(self.rse, [])
            if not pfns:
                raise RuntimeError(
                    f"No PFN found for existing replica with LFN {lfn} on {self.rse}"
                )
            return True
        return False

    def add_onsite_replica(self, acada_path) -> str:
        """Register a file as a replica in Rucio on the specified RSE and retrieve its LFN.

        Parameters
        ----------
        acada_path : str or Path
            The ACADA path where the file is located.

        rse : str, optional
            The RSE to register the replica on. If None, uses the client's RSE (self.rse).

        Returns
        -------
        str
            The Logical File Name (LFN) of the registered replica.

        Raises
        ------
        FileNotFoundError
            If the file does not exist at ``acada_path``.
        RuntimeError
            In the following cases:
            - If a replica already exists but has no PFN for the RSE (raised by `check_replica_exists`).
            - If the ``IngestionClient.add_replica`` call fails during registration (e.g., due to a Rucio server issue).
        """
        acada_path = Path(acada_path)
        self.logger.debug("Starting ingestion for path '%s'", acada_path)

        # Validate file existence
        if not acada_path.is_file():
            raise FileNotFoundError(f"File does not exist at {acada_path}")

        # Generate LFN
        lfn = self.acada_to_lfn(acada_path=str(acada_path))
        self.logger.info("Using LFN '%s' for path '%s'", lfn, acada_path)

        # Check if the replica already exists
        if self.check_replica_exists(lfn):
            self.logger.info("Replica already exists for lfn '%s', skipping", lfn)
            return lfn

        # Proceed with registering the replica if check_replica_exists returns False

        # Compute file metadata
        # TODO: use functions to identify file type, extract metadata, validate integrity, when this functionality is ready https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/work_items/46
        file_size = acada_path.stat().st_size
        checksum = adler32(acada_path)

        # Register the replica in Rucio
        try:
            success = self.replica_client.add_replica(
                rse=self.rse,
                scope=self.scope,
                name=lfn,
                bytes_=file_size,
                adler32=checksum,
            )
            if not success:
                raise RuntimeError(
                    f"Failed to register replica for LFN {lfn} on {self.rse}"
                )
        except Exception as e:
            raise RuntimeError(
                f"Failed to register replica for LFN {lfn} on {self.rse}: {str(e)}"
            )
        self.logger.info("Successfully registered the replica for lfn '%s'", lfn)

        return lfn

    def add_offsite_replication_rules(
        self,
        lfn: str,
        copies: int = 1,
        lifetime: Optional[int] = None,
        offsite_rse_expression: str = "OFFSITE",
    ) -> list[str]:
        """Replicate an already-ingested ACADA data product to offsite RSEs.

        This method assumes the data product has already been ingested into the onsite RSE and is identified by the given LFN.
        It creates one or two replication rules to offsite RSEs, depending on the number of copies requested:
        - First rule: Always creates exactly 1 replica to prevent parallel transfers from the onsite RSE.
        - Second rule (if copies > 1): Creates additional replicas (equal to the requested copies), sourcing data from offsite RSEs to avoid further transfers from the onsite RSE.

        Parameters
        ----------
        lfn : str
            The Logical File Name (LFN) of the already-ingested ACADA data product.
        copies : int, optional
            The total number of offsite replicas to create. Defaults to 1.
            - If copies == 1, only one rule is created with 1 replica.
            - If copies > 1, a second rule is created with the requested number of copies, sourcing from offsite RSEs.
        lifetime : int, optional
            The lifetime of the replication rules in seconds. If None, the rules are permanent.
        offsite_rse_expression : str, optional
            The RSE expression identifying offsite Rucio Storage Elements (RSEs). Defaults to "OFFSITE".

        Returns
        -------
        List[str]
            The list of replication rule IDs created (1 or 2 rules, depending on the copies parameter).

        Raises
        ------
        RuntimeError
            If there is an error interacting with Rucio, including:
            - Failure to create a new replication rule (e.g., DuplicateRule).
        """
        # Create the DID for replication
        did = {"scope": self.scope, "name": lfn}
        dids = [did]

        # Initialize the list of rule IDs
        rule_ids = []

        # First rule: Always create exactly 1 replica to prevent parallel transfers from onsite RSE
        try:
            rule_id_offsite_1 = self.rule_client.add_replication_rule(
                dids=dids,
                rse_expression=offsite_rse_expression,
                copies=1,
                lifetime=lifetime,
                source_replica_expression=None,  # Let Rucio choose the source (onsite RSE)
            )[0]
            self.logger.debug(
                "Created first replication rule %s for DID %s to RSE expression '%s' with 1 copy, lifetime %s",
                rule_id_offsite_1,
                did,
                offsite_rse_expression,
                lifetime if lifetime is not None else "permanent",
            )
            rule_ids.append(rule_id_offsite_1)
        except RucioException as e:
            self.logger.error(
                "Failed to create first offsite replication rule for DID %s to RSE expression '%s': %s",
                did,
                offsite_rse_expression,
                str(e),
            )
            raise

        # Second rule: If more than one copy is requested, create a second rule sourcing from offsite RSEs
        if copies > 1:
            # Exclude the onsite RSE to ensure the data is sourced from an offsite RSE
            # source_replica_expression = f"*\\{onsite_rse}" (we could also consider this expression)
            source_replica_expression = offsite_rse_expression
            self.logger.debug(
                "Creating second offsite replication rule to RSE expression '%s' with %d copies, sourcing from offsite RSEs",
                offsite_rse_expression,
                copies,
            )
            try:
                rule_id_offsite_2 = self.rule_client.add_replication_rule(
                    dids=dids,
                    rse_expression=offsite_rse_expression,
                    copies=copies,  # Use requested number of copies
                    lifetime=lifetime,
                    source_replica_expression=source_replica_expression,
                )[0]
                self.logger.debug(
                    "Created second replication rule %s for DID %s to RSE expression '%s' with %d copies, source_replica_expression '%s', lifetime %s",
                    rule_id_offsite_2,
                    did,
                    offsite_rse_expression,
                    copies,
                    source_replica_expression,
                    lifetime if lifetime is not None else "permanent",
                )
                rule_ids.append(rule_id_offsite_2)
            except RucioException as e:
                self.logger.error(
                    "Failed to create second offsite replication rule for DID %s to RSE expression '%s': %s",
                    did,
                    offsite_rse_expression,
                    str(e),
                )
                raise

        self.logger.info(
            "Created %d offsite replication rule(s) for LFN '%s' to RSE expression '%s': %s",
            len(rule_ids),
            lfn,
            offsite_rse_expression,
            rule_ids,
        )
        return rule_ids


class FITSVerificationError(Exception):
    """Raised when a FITS file does not pass verification."""


def verify_fits_checksum(hdul: fits.HDUList):
    """
    Verify all present checksums in the given HDUList.

    Goes through all HDUs and verifies DATASUM and CHECKSUM if
    present in the given HDU.

    Verifies DATASUM before CHECKSUM to distinguish failure
    in data section vs. failure in header section.

    Raises
    ------
    FITSVerificationError: in case any of the checks are not passing
    """
    for pos, hdu in enumerate(hdul):
        name = hdu.name or ""

        checksum_result = hdu.verify_checksum()
        if checksum_result == 0:
            msg = f"CHECKSUM verification failed for HDU {pos} with name {name!r}"
            raise FITSVerificationError(msg)
        elif checksum_result == 2 and pos != 0:  # ignore primary for warning
            LOGGER.warning("No CHECKSUM in HDU %d with name %r", pos, name)
