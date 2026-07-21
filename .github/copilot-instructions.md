# Copilot Instructions — sekoia-automation-models

This repository contains **standalone Pydantic models** implementing the
[OCSF (Open Cybersecurity Schema Framework)](https://schema.ocsf.io/1.8.0) schema.
All models live under `sekoia_automation_models/ocsf/`.

---

## PR Review — OCSF Model Alignment

When reviewing a pull request, validate every model change against the canonical
JSON schemas stored in `.github/schemas/`. The three top-level models are:

| Model | Schema file | OCSF reference                                             |
|---|---|------------------------------------------------------------|
| `VulnerabilityOCSFModel` | `.github/schemas/VulnerabilityOCSFModel.json` | https://schema.ocsf.io/1.8.0/classes/vulnerability_finding |
| `UserOCSFModel` | `.github/schemas/UserOCSFModel.json` | https://schema.ocsf.io/1.8.0/classes/user_inventory        |
| `DeviceOCSFModel` | `.github/schemas/DeviceOCSFModel.json` | https://schema.ocsf.io/1.8.0/classes/device_inventory_info |

### Checklist for every model change

1. **Required fields must stay required.**  
   The following fields are mandatory on all OCSF top-level models and must
   never be made optional:
   `activity_id`, `activity_name`, `category_name`, `category_uid`,
   `class_name`, `class_uid`, `type_name`, `type_uid`, `time`, `metadata`.
   Each model also has a model-specific required field:
   - `VulnerabilityOCSFModel` → `finding_info`, `vulnerabilities`
   - `UserOCSFModel` → `user`
   - `DeviceOCSFModel` → `device`

2. **Field types must match the JSON schema.**  
   Optional fields use `<type> | None = None`. Required fields must not have a
   default value. Enums must use the `IntEnum`/`StrEnum` subclasses defined in
   the same module.

3. **New fields must be optional (`| None = None`) unless they are explicitly
   required by the OCSF spec.**  
   Adding a required field is a breaking change; flag it in the review.

4. **Enum values must match OCSF exactly.**  
   Integer IDs and string labels must match the values in the JSON schema
   `$defs` section. Cross-check any new enum entry against the schema file.

5. **Nested models must reference existing `$defs`.**  
   Do not inline a nested model that already exists as a shared object
   (e.g. `Product`, `Metadata`, `Device`, `Group`, `Organization`).

6. **Every new model field must have a corresponding unit test.**  
   Tests live in `tests/test_<model_name>_model.py`. The test must cover:
   - the field accepting a valid value
   - the field defaulting to `None` when optional
   - a `ValidationError` when a required field is missing

7. **Imports must be explicit.**  
   Each module must import every type it uses. Re-exporting from another
   module's namespace to satisfy a type hint is not acceptable.

8. **No silent field aliasing.**  
   Do not use `Field(alias=...)` unless the OCSF spec mandates a different
   wire name. If an alias is added, document the reason in a comment.

---

## Code Style

- Use `from __future__ import annotations` only when strictly needed for
  forward references.
- Keep model classes in alphabetical order within their file, except for
  dependency order (a class must be defined before it is referenced).
- Do not add `model_config` unless there is a concrete need (e.g. `populate_by_name`).
- Comments are only required when the mapping to OCSF is non-obvious.

---

## Schema Files

The JSON schemas in `.github/schemas/` are auto-generated from the Pydantic
models via `Model.model_json_schema()`. They must be regenerated and committed
whenever a model changes. To regenerate:

```bash
uv run python - << 'EOF'
import json
from sekoia_automation_models.ocsf.vulnerability import VulnerabilityOCSFModel
from sekoia_automation_models.ocsf.user import UserOCSFModel
from sekoia_automation_models.ocsf.device import DeviceOCSFModel

for name, Model in [
    ("VulnerabilityOCSFModel", VulnerabilityOCSFModel),
    ("UserOCSFModel", UserOCSFModel),
    ("DeviceOCSFModel", DeviceOCSFModel),
]:
    with open(f".github/schemas/{name}.json", "w") as f:
        json.dump(Model.model_json_schema(), f, indent=2)
EOF
```
