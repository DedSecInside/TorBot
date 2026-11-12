# Changelog
--------------------
All notable changes to this project will be documented in this file.

## 4.3.1 - 2026-11-12

### Added
- Added `--save result` for analysis-ready crawl-result v1 files with bounded visible text and content hashes.
- Added `torbot analyze` for deterministic evidence bundles and optional local or remote OpenAI-compatible analysis.
- Added stable evidence IDs, claim citation validation, an evidence graph, JSON schemas, and a safe surface-web fixture.

### Changed
- Requires Python 3.10 or newer, with CI coverage for Python 3.10, 3.11, and 3.12.
- Updated pinned AnyIO, Soup Sieve, urllib3, certifi, and setuptools dependencies.
- Documented installation with OTinstaller.
- Excluded environment files from package builds.

### Security
- Fixed path traversal in tree, JSON, and HTML export filenames by sanitizing untrusted page titles. Thanks to Artur Chlebicki (@Artur12555) for reporting GHSA-5888-59xj-84pf.
- Added regression tests for relative and absolute paths, Windows separators, encoded separators, reserved names, and long titles.
- Remote evidence transmission now requires `--allow-remote`, redacts contact data by default, and never stores API keys.
- Crawled content is treated as untrusted data, model calls receive no tools, and uncited model output cannot become a supported finding.

## 4.3.0 - 2026-07-28

### Changed
- Made NLP classification train lazily from the packaged CSV and cache the classifier for the process, avoiding model retraining for every crawled page.
- Changed the NLP score returned by `classify()` from a misleading random-split accuracy value to prediction confidence for the selected category.

### Fixed
- Removed runtime `training_data/` generation from page classification so installed packages do not try to write generated files into `site-packages`.
- Removed process-wide directory changes from the NLP helpers.

### Tests
- Added direct NLP coverage for HTML text extraction, CSV loading, classifier scoring, and path-safe training-data export.

## 4.2.0 - 2026-07-28

Install from PyPI after publishing with:

```sh
pip install torbot==4.2.0
```

### Added
- Added optional `torbot app` and `torbot --app` CLI commands for launching the TorBotApp desktop UI when installed separately.
- Added TorBotApp discovery through `--app-dir`, `TORBOT_APP_DIR`, or a sibling `TorBotApp` checkout.
- Documented the optional desktop app architecture while keeping Node and Electron out of the Python package dependencies.
- Added a safer publish helper that checks current-version artifacts and prompts for a PyPI token only when uploading.

### Fixed
- Moved the CLI implementation into the installed package so the `torbot` console command works from a wheel install.
- Removed the deprecated `sklearn` package dependency in favor of the existing `scikit-learn` dependency so fresh installs do not fail.

## 4.1.1

### Fixed
- Adjusted the CLI so `--version` and `--update` can run without requiring a URL.
- Improved crawler link parsing so relative links are resolved against the current page while unsupported hrefs are skipped cleanly.

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
