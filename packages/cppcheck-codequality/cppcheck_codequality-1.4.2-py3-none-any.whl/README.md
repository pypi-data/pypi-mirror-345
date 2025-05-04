# cppcheck-codequality

[![badge-pypi](https://img.shields.io/pypi/v/cppcheck-codequality.svg?logo=pypi)](https://pypi.python.org/pypi/cppcheck-codequality/)
&nbsp;
[![badge-pypi-downloads](https://img.shields.io/pypi/dm/cppcheck-codequality)](https://pypistats.org/packages/cppcheck-codequality)


[![badge-pipeline](https://gitlab.com/ahogen/cppcheck-codequality/badges/main/pipeline.svg)](https://gitlab.com/ahogen/cppcheck-codequality/-/pipelines?scope=branches)
&nbsp;
[![badge-coverage](https://gitlab.com/ahogen/cppcheck-codequality/badges/main/coverage.svg)](https://gitlab.com/ahogen/cppcheck-codequality/-/pipelines?scope=branches)
&nbsp;
[![badge-pylint](https://gitlab.com/ahogen/cppcheck-codequality/-/jobs/artifacts/main/raw/badge.svg?job=pylint)](https://gitlab.com/ahogen/cppcheck-codequality/-/pipelines?scope=branches)
&nbsp;
[![badge-formatting](https://gitlab.com/ahogen/cppcheck-codequality/-/jobs/artifacts/main/raw/badge.svg?job=format_black)](https://gitlab.com/ahogen/cppcheck-codequality/-/pipelines?scope=branches)
&nbsp;
[![badge-issues-cnt](https://img.shields.io/badge/dynamic/json?label=issues&query=statistics.counts.opened&url=https%3A%2F%2Fgitlab.com%2Fapi%2Fv4%2Fprojects%2F19114200%2Fissues_statistics%3Fscope%3Dall)](https://gitlab.com/ahogen/cppcheck-codequality/-/issues)


## About

I wanted reports from CppCheck to appear in GitLab Merge Requests as [Code
Quality reports](https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html#implementing-a-custom-tool),
which is a JSON file defined by the Code Climate team/service.

That's all this does: convert CppCheck XML to Code Climate JSON.

### Usage

It is primarily used as a console script. As such, ensure you have Python 3's "scripts" directory in your `PATH` variable.
For example, on Linux, that might be `$HOME/.local/bin`.

To test, try the `--help` or `--version` flags:
```bash
cppcheck-codequality --help
```

CppCheck already has a script to convert its XML report to HTML for easy
human reading. See "Chapter 11 HTML Report" in the [CppCheck Manual](http://cppcheck.sourceforge.net/manual.pdf)

This script follows that example and provides similar command-line options.
A typical workflow might look like this:

```bash
# Generate CppCheck report as XML
cppcheck --xml --enable=warning,style,performance ./my_src_dir/ 2> cppcheck_out.xml
# Convert to a Code Climate JSON report
cppcheck-codequality --input-file cppcheck_out.xml --output-file cppcheck.json
```

If you wanted, you could invoke the script directly as a module, like this:

```bash
# Run as a module instead (note the underscore in the module name here)
python -m cppcheck_codequality --input-file=cppcheck_out.xml --output-file=cppcheck.json
```

Now, in your GitLab CI script, [upload this file](https://docs.gitlab.com/ee/ci/pipelines/job_artifacts.html#artifactsreportscodequality)
as a Code Quality report.

```yaml
my-code-quality:
  script:
    - [...]
  artifacts:
    reports:
      codequality: cppcheck.json
```

### Contributing

* Sign the contributor agreement (coming soon)
* Format with [black](https://pypi.org/project/black/)
* Check with [pylint](https://pypi.org/project/pylint/)

### Credits & Trademarks

CppCheck is an open-source project with a GPL v3.0 license.
* http://cppcheck.sourceforge.net
* https://github.com/danmar/cppcheck

"Code Climate" may be a registered trademark of Code Climate, Inc. which provides
super-cool free and paid services to the developer community.
* https://codeclimate.com
* https://github.com/codeclimate

"GitLab" is a trademark of GitLab B.V.
* https://gitlab.com
* https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html

All other trademarks belong to their respective owners.
