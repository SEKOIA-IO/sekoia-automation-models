# sekoia-automation-models

Standalone pydantic models shared across SEKOIA.IO services and the automation SDK.

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

## Development

```bash
uv sync
uv run ruff check .
uv run mypy
uv run pytest
```
