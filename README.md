# sekoia-automation-models

Standalone Pydantic models shared across Sekoia services and the `sekoia-automation-sdk`.

The package currently exposes the OCSF asset-connector models under
`sekoia_automation_models.ocsf`. Its only runtime dependency is `pydantic`, so
services can consume the models without pulling the full automation SDK.

## Install

```bash
pip install sekoia-automation-models
```

## Usage

```python
from sekoia_automation_models.ocsf.software import SoftwareEnrichmentObject
```

## Asset identifiers

`sekoia_automation_models.identifiers` writes a raw value as the identifiers of a machine or an
account, the same way for every source. Each function returns a list, strongest first, and an
empty list when the value identifies nothing (a placeholder such as `unknown`, a loopback name,
an IP address, a machine or shared account, a well-known SID).

```python
from sekoia_automation_models.identifiers import account_identifiers, host_identifiers, sid_identifiers

host_identifiers("SRV-01.corp.local")
# [Identifier("fqdn", "srv-01.corp.local"), Identifier("hostname", "srv-01"),
#  Identifier("hostname", "srv-01.corp.local", legacy=True)]

host_identifiers("srv-01", "corp.example")
# [Identifier("fqdn", "srv-01.corp.example"), Identifier("hostname", "srv-01")]

account_identifiers("CORP\\JDoe")
# [Identifier("username", "jdoe"), Identifier("username", "corp\\jdoe", legacy=True)]

account_identifiers("support@corp.example")
# [Identifier("email", "support@corp.example", generic=True)]

sid_identifiers("S-1-5-21-1500703765-3354019915-535386580-1662")
# [Identifier("sid", "s-1-5-21-1500703765-3354019915-535386580-1662")]
```

An identifier marked `legacy` is the form the value had before these rules: look it up after the
others, to find assets stored under it. One marked `generic` is real but shared by many objects.
`CATALOG` describes each type: its asset type, whether it is strong evidence, whether an event may
create an asset from it, and the OCSF and ECS fields it is read from.

`split_hostname`, `build_fqdn` and `normalize_sid` are unchanged.

## Development

```bash
uv sync
uv run ruff check .
uv run mypy
uv run pytest
```
