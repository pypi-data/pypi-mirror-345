# GDPLabs Artifact Registry Python Tools

This repository is a fork of [keyrings.google-artifactregistry-auth](https://pypi.python.org/pypi/keyrings.google-artifactregistry-auth) with modifications to support GDPLabs domains.

## Changes from Original

This fork extends the original package to support additional domains:
- `.obrol.id`
- `.gdplabs.id`

## Overview

This package provides a [keyring](https://pypi.python.org/pypi/keyring) backend implementation for interacting with Python repositories hosted on Artifact Registry, including GDPLabs domains.

## Authentication

The backend automatically searches for credentials from the environment and authenticates to Artifact Registry. It looks for credentials in the following order:

1. [Google Application Default Credentials](https://developers.google.com/accounts/docs/application-default-credentials)
2. From the `gcloud` SDK
3. If neither exists, an error occurs
