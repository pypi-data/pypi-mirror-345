Storage Elements
================

XrootD storage elements (with AAA and TPC) for the Test setup
-------------------------------------------------------------

The XrootD RSEs are deployed using a storages sub-chart belonging to the main BDMS helm chart. These XrootD storages support
grid authentication (GSI) and Third-party copy (TPC) required for data transfers and replication managed by Rucio.
The helm chart installation of XrootD results in them running as deployment type on the kubernetes cluster. The storages configuration
including mounting of host and CA certificates are defined in their chart's yaml file ``bdms/chart/templates/test_storages.yaml``.

The xrootD configuration file ``xrdrucio.cfg`` is modified to add the directive ``xrd.maxfd 1024`` that enables setting the maximum number of
file descriptors that XrootD server can process. Thus, XrootD server will allocate up to 1024 concurrent file descriptors. The file descriptors are resources
used by the operating system. In the context of XrootD server, they are required to handle incoming client connections, opening file streams,
and on-going data transfers. The modified xrdrucio.cfg file is added as kubernetes ``configMap`` in the chart's yaml file and its content
is shown in the code-block below.

::

    ======== /etc/xrootd/xrdrucio.cfg ========
    all.export /rucio
    xrootd.seclib /usr/lib64/libXrdSec.so
    sec.protocol /usr/lib64 gsi -dlgpxy:1 -exppxy:=creds
    xrootd.chksum adler32 /usr/local/bin/xrdadler32.sh
    ofs.tpc autorm fcreds gsi =X509_USER_PROXY pgm /usr/bin/xrdcp --server
    xrd.port 1094
    xrd.maxfd 1024
    ==========================================

There is also another configMap ``xrd-entrypoint`` mounted in the chart's yaml file definition, it contains the ``docker-entrypoint.sh`` script
that is an entrypoint to the storages deployment container. At first, the script sets the file descriptor limit to 1024 matching the
xrdrucio.cfg file so that lower limits are not enforced by the system causing runtime errors to inform about too many open files. It fixes
the ownership to xrootd user and also restricts permissions on the private key so that only XrootD process is able to read it.

The storages are rolled out as deployments and pod on the Kubernetes cluster and their service is run on port 1094 with default clusterIP type
restricting access within the cluster. The xrootD image used in the deployment container is fetched from CTAO Harbor and it is the standard
one provided by Rucio. There is a proxy cache deployed at the harbor to speed-up the serving of image from the local cache instead of pulling it
from the upstream source (like rucio/xrootd at Docker Hub).

Storing data at XrootD with persistence: Data storage on XrootD RSEs is made persistent with a persistent volume claim (PVC) feature in Kubernetes and a mountpath with the prefix to be
added in the configuration.

Accessing XrootD storage elements from BDMS clients: For this, a X509 proxy set-up on the client is required and such a proxy can be
generated from user certificates as shown in the code block below.

.. code-block:: shell

   $ (KEY=$(mktemp); cat /opt/rucio/etc/userkey.pem > "$KEY"; voms-proxy-init -valid 9999:00 -cert /opt/rucio/etc/usercert.pem -key "$KEY"; rm -f "$KEY")
