FTS
===

Role of FTS in Rucio
--------------------

FTS is one of the transfertools of Rucio. The ``Conveyor`` submitter daemon sends transfer requests to FTS, grouping based on source and destination
RSEs. FTS then schedules and executes the transfers. The ``Conveyor`` poller daemon continuous monitors the FTS job status, retrieiving updates from FTS. Once
transfers are completed, Rucio's database is updated to reflect successful transfers or logged failures. In the successful case, the destination RSE is marked as
having a valid replica. On the other hand, unsuccessful transfers are either retried based on policy or marked as failed.

Helm-chart based installation for FTS
-------------------------------------
The FTS chart is added as a dependency (thus a sub-chart) in the BDMS chart (``bdms/chart``) by including it in the Chart.yaml file.
It is generated separately under FTS repo at the DPPS AIV: https://gitlab.cta-observatory.org/cta-computing/dpps/aiv/fts and then pushed to
the CTAO Harbor repository.  The following code block shows how FTS is added as a dependency in the the yaml file. The FTS chart installation leads
to deployment of three containers: FTS server, FTS database, and ActiveMQ messaging.

.. code:: bash

  - name: fts
  condition: fts.enabled
  version: 0.1.0
  repository: oci://harbor.cta-observatory.org/dpps

In the global values.yaml file of the BDMS chart under ``fts`` section, values are populated for the FTS server (image: ``harbor.cta-observatory.org/proxy_cache/rucio/fts``, tag, pullPolicy),
FTS database password (including root) and Activemq messaging configuration with FTS server credentials. The FTSdb image details (``harbor.cta-observatory.org/proxy_cache/mariadb:10``) are
provided directly in the chart's deployment yaml file while ActiveMQ messaging (``harbor.cta-observatory.org/proxy_cache/apache/activemq-classic``)and FTS server image detail are provided in the chart's
values.yaml file. The FTS chart's deployment YAML file also provides all the required values for containers (including image, ports, volume mounts for certificates/config): FTS server, FTSdb, and ActiveMQ
as part of its Test set-up.

The service details for FTS server (mapped to port ``8446`` (fts-web) and ``8449`` (fts-monitoring), FTSdb (mapped to port ``3306``), and ActiveMQ (mapped to port ``61613``)
with default ClusterIP type.

The detailed FTS helm chart is provided at this link: https://gitlab.cta-observatory.org/cta-computing/dpps/aiv/fts/-/blob/main/chart/README.md?ref_type=heads
