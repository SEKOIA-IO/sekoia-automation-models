# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `build_fqdn` returns the FQDN of a device from its hostname and domain in lower case, keeps a hostname that already ends with the domain, and returns `None` for a NetBIOS domain, a hostname qualified with another domain or an invalid name, so connectors and the asset management API build the same FQDN.

## [1.6.0]

### Added

- `normalize_sid` returns the SID of a domain account or an Entra ID object in upper case, and `None` for a placeholder, a GUID, a well-known SID or a built-in account, so connectors and the asset management API keep the same SIDs.

## [1.5.0]

### Added

- `split_hostname` returns the `(hostname, domain)` pair the asset management API accepts: a fully qualified name is split on its first label, an unusable name gives `(None, None)`.

## [1.4.0]

### Added

- Add `batch_push_interval` to `DefaultAssetConnectorConfiguration` to configure the delay between consecutive asset batch pushes; it defaults to `0` (no delay).
- Add `max_assets_per_cycle` to `DefaultAssetConnectorConfiguration` so asset connectors can declare a per-cycle asset cap. `0` (the default) declares an unlimited cap; enforcement requires SDK support.
- `last_used_file_name` on `SoftwareEnrichmentObject`: the name of the application's binary that ran last, reported by the endpoint agent together with its hashes.

## [1.3.0]

### Added

- `purl` (Package URL) on `SoftwarePackage`, as in the OCSF `package` object, and on `SoftwareEnrichmentObject` so the endpoint agent can report it.

## [1.2.0]

### Added

- Improve ocsf models (`User`, `Vulnerability`) with new fields.
- Add unit test to validate the models (`User`, `Vulnerability`).
- Add instructions for PR review to validate the models against the OCSF JSON schemas.

## [1.1.0]

### Added

- `connector` module with the asset-connector models (`AssetItem`, `AssetList`, `DefaultAssetConnectorConfiguration`) extracted from `sekoia-automation-sdk`.

## [1.0.0]

### Added

- Initial package with the OCSF asset-connector Pydantic models extracted from `sekoia-automation-sdk`.
