BDMS Rucio Policy & Deployment Guide
====================================

BDMS Policy Package for Rucio
-----------------------------
Configures permissions, schema, and algorithms for Rucio, including allowed **LFN**, **RSE**, and **user names**, ``extract_scope``, and ``lfn2pfn``.
See `<https://rucio.github.io/documentation/operator/policy_packages/>`_ for more details.
The policy was started from the "generic" Rucio version and adapted to meet the requirements of the **Rucio-DIRAC integration**.

Rucio Docker Images with CTAO Rucio Policy Package
--------------------------------------------------
This repository contains a simple **Dockerfile** adding the **BDMS Rucio policy package** to the upstream **Rucio Docker images**.
The CI system builds and publishes them to **CTAO Harbor**.

You can find the stored Docker images in CTAO Harbor at:
`Harbor Repository <https://harbor.cta-observatory.org/harbor/projects/4/repositories>`_.

Rucio Helm Charts for Harbor Deployment
---------------------------------------
Repository to deploy our **forked version** of the **Rucio Helm Chart** to **Harbor**.

Procedure to Update to a New Rucio Version
------------------------------------------

1. Preparation and Planning
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Review Release Notes**

   - Check the Rucio release notes or any other official documentation for changes.
   - Pay special attention to **breaking changes**, **policy updates**, **configuration changes**, and **database schema migrations**.

2. **Check Policy Changes**

   - Rucio may introduce **new or modified policy packages**.
   - Verify if there are **new fields or configuration elements** in the policy that you must override or align with your settings.
   - Update your **policy configuration files** accordingly.

3. **Back Up Current Setup**

   - Back up your **Rucio database(s)**.
   - Export your configuration files (**Rucio config, Helm values.yaml, secrets, etc.**).
   - If you use a container registry, ensure your **old images** are still available as a fallback.

2. Updating the Helm Charts (Kubernetes Deployments)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Add or Update the Rucio Helm Repository**

   - If you are using the official charts, ensure they are up to date.

2. **Check the Chart Version**

   - Look at the Helm chart’s **changelog** or **README** to confirm you're using a version compatible with the new **Rucio release**.

3. **Update Your Configuration Files**

   - Ensure your **values.yaml** (or equivalent override file) is updated with any new or changed **configuration parameters**.
   - Update the **Rucio image tag** to reflect the new version.
