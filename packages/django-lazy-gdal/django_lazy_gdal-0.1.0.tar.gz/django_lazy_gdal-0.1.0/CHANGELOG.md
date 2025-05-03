# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project attempts to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [${version}]
### Added - for new features
### Changed - for changes in existing functionality
### Deprecated - for soon-to-be removed features
### Removed - for now removed features
### Fixed - for any bug fixes
### Security - in case of vulnerabilities
[${version}]: https://github.com/joshuadavidthomas/django-lazy-gdal/releases/tag/v${version}
-->

## [Unreleased]

## [0.1.0]

### Added

- Initial release of django-lazy-gdal
- Lazy loading of GDAL libraries to defer loading until actually needed and avoid `ImproperlyConfigured` exceptions
- Monkeypatching mechanism to replace Django's default GDAL loading in `django.contrib.gis.gdal.libgdal`
- Support for Python 3.9, 3.10, 3.11, 3.12, 3.13
- Support for Django 4.2, 5.1, 5.2

### New Contributors!

- Josh Thomas <josh@joshthomas.dev> (maintainer)

[unreleased]: https://github.com/joshuadavidthomas/django-lazy-gdal/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/joshuadavidthomas/django-lazy-gdal/releases/tag/v0.1.0
