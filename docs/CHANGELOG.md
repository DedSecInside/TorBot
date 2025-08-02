# Changelog
--------------------
All notable changes to this project will be documented in this file.

## 4.2.0 - Security, Docker, and Documentation Update

### Added
- Updated all dependencies to latest secure versions
- Added support for httpx 0.28.1+ with proper proxy configuration
- Added lxml>=5.3.0 for improved XML/HTML parsing
- Enhanced error handling for NLP module
- Multi-stage Docker build for optimized container (200MB final size)
- Docker Compose support with Tor integration
- Non-root user execution in Docker container (security enhancement)
- Comprehensive Docker documentation (docs/DOCKER.md)
- Enhanced testing documentation (TESTING.md)
- Docker testing configuration (docker-compose.test.yml)
- Health checks for Docker containers
- .dockerignore for optimized builds

### Fixed
- Fixed compatibility issues with httpx 0.28.1+ API changes
- Fixed UnicodeDecodeError in NLP module by adding graceful degradation
- Fixed FileNotFoundError for missing training data in sklearn
- Updated dependency versions to address security vulnerabilities
- Fixed Docker build process to use pip instead of poetry
- Updated README.md with new Docker instructions

### Security
- Updated certifi>=2024.8.30 for SSL certificate validation
- Updated urllib3>=2.2.2 for security patches
- Updated scikit-learn>=1.5.1 with latest security fixes
- Updated all dependencies to latest stable versions
- Docker container runs as non-root user (UID 1000)
- Reduced attack surface with minimal base image

### Documentation
- Updated README.md with Docker multi-stage build instructions
- Enhanced Tor.md with Docker configuration options
- Added comprehensive Docker documentation (docs/DOCKER.md)
- Updated testing documentation with Docker testing instructions
- Added CONTRIBUTING.md for contribution guidelines
- Updated installation instructions for Python ^3.9

## 2.1.0

### Added
* GoTor API - A Golang implementation of Core TorBot functionality.
* Phone number extractor - Extracts phone numbers from urls.
* Integrated NLP module with TorBot
* Major code refactoring

### Removed
* No longer using the tree module
* Poetry Implementation removed

## 2.0.0

### Added
* Fix data collection and add progress indicator by @KingAkeem in #192
* convert port to integer by @KingAkeem in #193
* Use hiddenwiki.org as default URL for collecting data by @KingAkeem in #194
* Bump jinja2 from 2.11.2 to 2.11.3 in /src/api by @dependabot in #200
* Simplify LinkNode and add new display by @KingAkeem in #202
* Remove live flag by @KingAkeem in #203
* Poetry Implementation by @NeoLight1010 in #206
* Delete .DS_Store by @stefins in #204
* Fix the basic functionality of tree features by @KingAkeem in #214
* Save results as json by @KingAkeem in #215
* Organize data file location by @KingAkeem in #216
* Add CodeTriage link and image by @KingAkeem in #213
* Add website classification by @KingAkeem in #218
* Use GoTor HTTP service by @KingAkeem in #219


## 1.4.0 | Present 

### Added 

* New Web UI
* API
* Error handling

## 1.3.1 | Nov 1, 2018 - Aug 1, 2020

### Changed 

* Changing requests version to 2.20.0

## 1.3.0 | Oct 19, 2018 - Nov 1, 2018

### Changed

* Major code improvements
* Updated README.md
* Updated dependencies
* Refactored TorBot

### Added

* Visualizer Module
* Download option to save Tree into different formats.
* DB module
* Installation shell script to create torBot binary
* Test for getting links that uses a Mock Object to reproduce tests without touching actual servers.
* BFS algorithm for crawling
* Documentation for functions

### Removed

* -l Live argument Removed (Enabled by default)


## 1.2.0 | Nov 16, 2017 - Oct 19, 2018

### Changed

* Major code improvements
* Pep 8 Standard
* Tests
* Library changes

### Added

* Documentation
* Save to JSON
* Testcase for Save to JSON

## 1.0.1 - July 6, 2017 - Nov 16, 2017

### Added

* Updater
* Version checker
* Refactored code to meet PEP8 requirements
* Refactored code to meet Google Style Docstrings for documentation
* Fixed error occuring while using -i flag

## 1.0.0 - Jun 28, 2017 - July 5, 2017

### Added
* Argument parser support
* Made live url checker optional
* Multiple domain extension support
* Quiet mode

### Changed

* Default Live url checker

## 0.0.3 - Jun 18, 2017 - Jun 27, 2017

### Added

* Resources and Samples
* Color to modules
* Live website checking
* CODE_OF_CONDUCT
* Travis CI integration

## 0.0.2 - Jun 13, 2017 - Jun 17, 2017

### Added

* Tor.md
* LICENSE
* Page reader
* Weblink fetcher
* Email fetcher
* Test case for get weblink
* Testcase for get email


## 0.0.1 - May 17, 2017 - Jun 3, 2017

### Added

* README file
* Test directory
