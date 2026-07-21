# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0]

### Added

- Improve ocsf models ( `User`, `Vulnerability`) with new fields.
- Add unit test to validate the models ( `User`, `Vulnerability`).
- Add instructions for PR review to validate the models against the OCSF JSON schemas.

## [1.1.0]

### Added

- `connector` module with the asset-connector models (`AssetItem`, `AssetList`, `DefaultAssetConnectorConfiguration`) extracted from `sekoia-automation-sdk`.
- Improved OCSF models (`User`, `Vulnerability`) with new fields.

## [1.0.0]

### Added

- Initial package with the OCSF asset-connector Pydantic models extracted from `sekoia-automation-sdk`.
