Data Transfers in BDMS
======================

This page describes the functionality for transferring and replicating data products in the BDMS system (Use Case UC-110-1.6) using Rucio.

Replication from ONSITE to OFFSITE RSEs
---------------------------------------

BDMS supports replication of data products from an ONSITE RSE to OFFSITE RSEs. Replication rules use the RSE expression ``OFFSITE`` to target OFFSITE RSEs,
with the number of replicas determined by the requested number of copies.

- For ``copies=1``, a single replica is created on an OFFSITE RSE, ensuring that only one transfer occurs from the ONSITE RSE to avoid overloading the shared bottleneck link (onsite to offsite). More info on how RSE expression is evaluated is available at this page: https://rucio.github.io/documentation/started/concepts/rse_expressions, and replication rule examples is available here: https://rucio.github.io/documentation/started/concepts/replication_rules_examples.

- For ``copies > 1``, an initial replica is created on an OFFSITE RSE, and additional replicas are created (equal to the requested copies). These additional replicas are sourced from the OFFSITE RSE using the ``source_replica_expression`` parameter set to ``OFFSITE``, preventing further transfers from the ONSITE RSE.
  This will result initially in the second replication rule to be ``STUCK``. This is normal, and that the ``judge-repairer`` daemon needs to be run to finish the transfers.

This approach ensures that the shared bottleneck link between onsite and offsite locations is used only once, optimizing transfer efficiency.

For more details on the replication implementation, refer to the API documentation for the function ``add_offsite_replication_rules`` in the module below.

- :py:mod:`bdms.acada_ingestion`

Additionally, Rucio documentation (https://rucio.github.io/documentation/operator_transfers/transfers-overview) provides finer details on the transfers with its emphasis on the interaction between
storage elements, daemons, and FTS.
