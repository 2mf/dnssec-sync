# dnssec-sync

Python port of [`SpicyWeb-de/isp-dnstool`](https://github.com/SpicyWeb-de/isp-dnstool) using the [`inwx/python-client`](https://github.com/inwx/python-client).

This CLI syncs DNSSEC information from ISPConfig to INWX.

## Features

- export DNSSEC key data from ISPConfig to `dnsseckeydata.json`
- print DNSSEC summaries and reports
- list signed zones known in ISPConfig and INWX
- print keys for a specific zone
- publish unpublished keys to INWX
- clean orphaned keys from INWX
- clean corrupted keys from INWX

## Requirements

- Python 3.10+
- access to the ISPConfig Remote API
- an INWX account with API access
- optional INWX TOTP secret

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.dist .env
```

Edit `.env` and set your ISPConfig and INWX credentials.

## Usage

```bash
python -m dnssec_sync --help
```

Export keys from ISPConfig:

```bash
python -m dnssec_sync isp --export
```

Print summary from ISP export + INWX live data:

```bash
python -m dnssec_sync inwx --summary
```

Publish missing keys:

```bash
python -m dnssec_sync inwx --publish
```

Clean one domain:

```bash
python -m dnssec_sync inwx --clean example.com.
```

## Environment

The tool reads configuration from a local `.env` file.
See `.env.dist` for the full list of supported variables.

## Notes

- ISPConfig export writes only the KSK (`DNSKEY 257`) plus matching DS record, matching the original PHP tool.
- INWX calls are performed through `inwx-domrobot`.
- By default, `Live` uses `ApiClient.API_LIVE_URL`; `Ote` uses `ApiClient.API_OTE_URL`.
