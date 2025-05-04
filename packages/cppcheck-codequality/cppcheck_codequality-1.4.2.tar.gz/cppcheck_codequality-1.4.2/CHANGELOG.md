# `cppcheck-codequality` Changelog

[[_TOC_]]

## UPCOMING

## 1.4.2 - 2025-03-03

### Fixed

- CI job tag (`docker` -> `gitlab-org-docker`). (MR !20)
- Fix MD5 hash exception in FIPS restricted environments. (MR !21, ty @irowebbn)

## 1.4.1 - 2024-01-27

### Fixed

- Fix changelog links on PyPi et. al.
- Fix supported Python version range in pyproject.toml

## 1.4.0 - 2023-10-26

### Added

- Add support for Python 3.12. (MR !18)

### Changed

- Bump Poetry from 1.2.1 to 1.5.1 (MR !18)
- Refactor unit test to remove dependency on `pytest-console-scripts`. (MR !18)
- Format CHANGELOG as Markdown. AsciiDoc is overkill. (MR !18)

### Removed

- Drop support for Python 3.6. (MR !18)

## 1.3.1 - 2022-10-19

### Added

- Restore support for Python 3.6. (MR !17)
  - Really wanted the updated fingerprint scheme from MR !14 in some older CI runners.

## 1.3.0 - 2022-10-19

### Added

- Test for Python 3.10.x and 3.11.x support.

### Fixed

- Fix Gitlab CI syntax to use new `reports:coverage_report` key. (MR !13)
- Fix issue count return from `convert_file`. (MR !14)

### Changed

- Remove line number from fingerprint input. (MR !14)
- Transition from setup.py + requirements text files to Poetry v1.2.x. (MR !15)

### Removed

- Drop Python 3.6.x support.

## 1.2.0 - 2021-10-19

### Added

- CI tests against py36, py37, py38, py39. (MR !12)
- Added support for pointing to source code directories with `--base-dir` CLI flag. (MR !12)
- Log warning message if `ConfigurationNotChecked` rule (from CppCheck) is seen in the input XML.
- Log number of issues written to output.

### Fixed

- Fix "run as module" usage by splitting the singular `\__init__.py` into `\__init__.py` and `\__main__.py`. (MR !12)

### Removed

- Remove CWE URL from JSON `content` body.
  I don't think it has been very useful over the last year.
  Not exposed in GitLab MRs and just makes the JSON file larger.
- Remove `[cppcheck]` prefix from JSON `description` field. Move to `check_name` field. (MR !12)

## 1.1.2 - 2021-08-18

### Fixed

- Fix crash when CppCheck points to line number 0 in a file. (MR !11)

## 1.1.1 - 2021-02-17

### Fixed

- Fix example in README. (MR !7)

## 1.1.0 - 2020-12-15

### Added

- Add 'severity' field. (MR !6)
- Add "[cppcheck]" prefix to issue message, to quickly identify the
  tool which produced the warning. May put this in 'engine_name' field
  in the future, but GitLab won't show that in MRs. So prefix the issue
  message for now. (MR !6)

### Removed

- Remove CppCheck's severity from the JSON `categories` list. (MR !6)

## 1.0.3 - 2020-7-22

### Fixed

- Fix reading code line from wrong file, when issue has an array of file locations. (MR !5)

## 1.0.2 - 2020-7-22

### Fixed

- Fix off-by-one error in file line read call. (MR !4)

## 1.0.1 - 2020-7-21

Improve reliability and consistency.

### Added

* Add more unit test cases. (MR !2, MR !3)

### Fixed

- Fixes issue where source code with bad (not UTF-8/ASCII) characters would
  cause script failure. (MR !3)
- Fixes issues where column number is missing in XML report. (MR !3)

## 1.0.0 - 2020-7-19

Script working. PyPi packaging and CI pipeline set up.

## 0.1.0-rc0 - 2020-7-7

Initial mostly-working v0.1.0 (still in development).
