# libdc3

Library designed to implement all operations needed for DC3 application and at the same time be human-usable through python scripts or notebooks.

## Installation

To install libdc3, simply

```bash
$ pip install libdc3
```

## Environment variables

This library depends heavily on `runregistry` python package, so it is needed to set `SSO_CLIENT_ID` and `SSO_CLIENT_SECRET` in your environment.

The interface with `brilcalc` is done via SSH or standard python subprocess if `brilconda` environment is available under the `/cvmfs` location. If executing in an environment without `brilconda`, you need to configure the `dc3_config` object with your LXPlus credentials (recommended via environment variables).

Last but not least, in order to successfully communicate with `DQMGUI` and `T0` endpoints a valid CERN Grid certificate is needed. Again, the `dc3_config` object should be configured with paths to the grid certificated and key (that should be opened).

## SWAN setup

1. Configure your SWAN environment using `Software stack 105a` and select the option `Use Python packages installed on CERNBox`
2. Create a SWAN project with any name you like and upload all example notebooks to it
3. Open SWAN terminal and create a `.env` file under your project directory and add the following variables: `SSO_CLIENT_ID`, `SSO_CLIENT_SECRET`, `AUTH_CERT`, `AUTH_CERT_KEY`
4. On any notebook, create a new cell and add `pip install libdc3`.
