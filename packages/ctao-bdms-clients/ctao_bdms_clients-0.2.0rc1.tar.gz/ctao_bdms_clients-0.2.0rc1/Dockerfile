 # rucio version used as base for the final image
ARG RUCIO_TAG=release-35.7.0

FROM harbor.cta-observatory.org/proxy_cache/python:3.9 AS builder

COPY pyproject.toml MANIFEST.in /tmp/bdms/
COPY .git /tmp/bdms/.git/
COPY src /tmp/bdms/src/

RUN python -m pip install build \
  && python -m build /tmp/bdms --wheel -o /tmp/dist

# second stage, copy and install wheel
# We are using the official python 3.11 image
# as base image in the slim variant to reduce image size.
FROM harbor.cta-observatory.org/proxy_cache/rucio/rucio-clients:${RUCIO_TAG}

ARG RUCIO_TAG

# server and daemons use root, clients use "user", switch to root, install, then back
USER root
COPY --from=builder /tmp/dist/ /tmp/dist/
RUN  dnf install -y --setopt=install_weak_deps=False git \
  && python3 -m pip install --no-cache-dir /tmp/dist/ctao_bdms* \
  && dnf autoremove \
  && dnf clean all

USER user

ENV RUCIO_POLICY_PACKAGE=bdms_rucio_policy
