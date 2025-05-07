Data Ingestion from ACADA
==========================

This page describes the functionality for ingesting new data products from ACADA (Use Case UC-110-1.1.1) into the BDMS system using Rucio.

Configuration of ONSITE RSE and Shared Storage
----------------------------------------------

To ingest data from ACADA, BDMS configures one RSE as the ONSITE RSE. This is achieved by setting RSE attributes during the bootstrapping
phase of the BDMS Rucio deployment. The configuration script in the BDMS Helm chart (``bdms/chart/scripts/bootstrap_rucio/setup_rucio.sh``)
includes the following logic to set these attributes to RSEs:

.. code-block:: shell

  if [ "$N" -eq 1 ]; then
    echo "Setting STORAGE-${N} as ONSITE"
    rucio-admin rse set-attribute --rse "STORAGE-${N}" --key ONSITE --value true
  else
    echo "Setting STORAGE-${N} as OFFSITE"
    rucio-admin rse set-attribute --rse "STORAGE-${N}" --key OFFSITE --value true
  fi

The ``IngestionClient`` needs direct access to the storage area of the ONSITE RSE and this is the expected location of files to be ingested.


Data Ingestion
--------------

The ingestion of data products from ACADA is handled by the `bdms.acada_ingestion` module. This module provides the functionality to ingest new data products into the BDMS system,
ensuring they are registered in Rucio and stored on the ONSITE RSE. As part of the ingestion process, BDMS extracts relevant metadata from the data products, validates their integrity,
and registers them in the Rucio file catalog. The extracted metadata is then added to the data products, enhancing their discoverability and management within the system.

For more details on the ingestion process, refer to the API documentation for the module:

- `bdms.acada_ingestion`
