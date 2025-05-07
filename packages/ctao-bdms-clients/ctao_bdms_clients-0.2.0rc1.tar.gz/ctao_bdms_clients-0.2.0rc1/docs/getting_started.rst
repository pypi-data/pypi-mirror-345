Getting started for Developers
==============================

Development Setup on your local machine
---------------------------------------

This repository contains the helm charts for deploying the BDMS
and the ``bdms`` python package, containing client side code.

The helm charts define a test pod that will run the tests of the ``bdms`` package
using the installed helm components.

Via the `dpps-aiv-toolkit <https://gitlab.cta-observatory.org/cta-computing/dpps/aiv/dpps-aiv-toolkit/>`_
it is possible to use the Kubernetes based deployment also for development, including running tests
locally against a development installation.

It is using `kind <https://kind.sigs.k8s.io/>`_ to locally deploy a Kubernetes cluster.


#. Clone the repository, make sure to add ``-r / --recursive`` to get the submodules:

   .. code-block:: shell

      $ git clone -r git@gitlab.cta-observatory.org:cta-computing/dpps/bdms/bdms
      $ cd bdms

   If you forgot to add ``-r``, you can run:

   .. code-block:: shell

      $ git submodule update --init --recursive

#. Copy ``env_template`` to ``.env`` and fill in the credentials for accessing data. Ask the maintainers if you don't know them.

#. Create the kubernetes cluster:

   .. code-block:: shell

      $ make dev

   Now you can run tests interactively, e.g. using a debugger:

   .. code-block:: shell

      [root@bdms-pytest bdms]# pytest --pdb
