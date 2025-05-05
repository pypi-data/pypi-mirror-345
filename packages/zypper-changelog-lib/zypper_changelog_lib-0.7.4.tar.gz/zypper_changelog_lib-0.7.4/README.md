<!--
SPDX-FileCopyrightText: 2025 The Rockstor Project <support@rockstor.com>

SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Changelog tool for Zypper

Both YUM & DNF can provide changelogs for pending package updates, or as-yet uninstalled packages.
Zypper, the package manager favoured by openSUSE, lacks these capabilities currently.

This tool is a stand-alone work-around that resources zypper local cache files,
specifically each repo's `/var/cache/zypp/raw/(REPOSITORY-ALIAS)/repodata/*primary.xml.[gz|zst]`,
to discover the latest version of each package that is available within each repository.

An RPM python interface is then utilized to interrogate the header of that latest-per-repo version.
This facilitates having to only download the header of each rpm from the remote repositories,
for each package queried.

The default is to consider only installable pending package updates.
Analyzing a large repository for all available packages is still somewhat extreme, and rarely required. 

## History

This endeavour represents a heavily modified version of zypper-changelog-plugin by Zoltán Balogh of SUSE.

- [GitHub zypper-changelog-plugin](https://github.com/bzoltan1/zypper-changelog-plugin) 
- [OBS zypper-changelog-plugin](https://build.opensuse.org/package/show/zypp:plugins/zypper-changelog-plugin)

These references differ in packaging details/config but share the LGPL-2.1-only licensed `zypper-changelog` file.
The single Python source file differs by a pending GitHub PR fix; already in the OBS zypper-changelog-plugin-0.6.tar.gz.
This file is renamed to `zypper-changelog-lib.py` with the original preserved within Git to help with [Aims 6](#aims).

## Aims

This fork aims to:

1. Add library capability, enabling its use in other Python projects,
2. Add common, non-optional constrains/optimisations not found in the original work. 
   E.g. retrieving changelogs only for the latest version of each package in each repo.
3. Lightly re-work the CLI options available; with the aim of simplifying its use.
4. Add repo authentication capability, as per for example SLES repos, via password-store initially.
   Required outside that already provided by zypper by virtue of our partial (http 206) requests. 
5. Reduce RAM requirements by further optimisations. The original, and still to a large extent this fork,
   struggle with larger repos on systems with < 4 GB RAM.
6. Ultimately contribute back to the original project if these goals align. 

## Use within a Python projects

The current maintainer of this fork has a time-sensitive specific use for the modified code as presented.
But as per [Aims 6](#aims) above,
it is hoped that over time any and hopefully all improvements can be shared with the above referenced project.  

> pip install zypper-changelog-lib

You virtual environment, as per the included Poetry .venv config, needs to include:

- `rpm-shim` [rpm](https://pypi.org/project/rpm/) to interfaces with the OS `Python311-rpm` package. 
- [requests](https://pypi.org/project/requests/) if OS `python311-requests` is not found.
- [keyring-pass](https://pypi.org/project/keyring-pass/) module is assumed: [see Repository Authentication](@repository_authentication).

```python
import zypper-changelog-lib
```

## OS package dependencies
Names based on openSUSE packages.

- `Python311` - A suspected minimum.
- `Python311-rpm` - to interface with the OS's RPM version.
- `python311-requests` - used for the partial (HTTP 206) rpm header retrievals.
- `password-store` - repo authentication, via  the Python `keyring-pass` module.
- `zstd` - decompression tool used for the zypper cache files.
- `zypper` - Obviously.

If running within a 

## CLI use

The initial focus here is on enabling library functionality,
but the following should work for testing purposes using the included Poetry config.

### Poetry .venv preparation
From the source root:
```shell
poetry install
```

Note that `zypper refresh` ensures its cache files are up-to-date with repository content. 

### Default

List the changelogs for all installable updates

```shell
zypper refresh
poetry run zypper-changelog-lib
```

Not all pending updates have accompanying changelog entries,
in this case only the package name header will be output;
e.g. `Package: libvpl2` in the following example.
Similarly, companion packages can sometimes share a changelog.
The following is an example output containing both of the above.

```shell
Package: iproute2
* Wed Mar 19 2025 mkubecek@suse.cz
- avoid spurious cgroup warning (bsc#1234383):
  - ss-Tone-down-cgroup-path-resolution.patch

Package: iproute2-bash-completion
* Wed Mar 19 2025 mkubecek@suse.cz
- avoid spurious cgroup warning (bsc#1234383):
  - ss-Tone-down-cgroup-path-resolution.patch

Package: libvpl2
```

### Repository Authentication

Required repository credentials are assumed to be held by [password-store](https://www.passwordstore.org/),
by Jason A. Donenfeld of wireguard fame.
But any [keyring](https://pypi.org/project/keyring/) compatible back-end should work, if properly configured.
The [keyring-pass](https://pypi.org/project/keyring-pass/) library provides the keyring interface to `pass`/`password-store`.

Keyring-pass, by default, has a prefix of "python-keyring".
The following uses the CLI `pass` command from the `password-store` OS rpm package.
A single set of credentials for the repo alias "Rockstor-Stable" have been added.

```shell
pass

Password Store
└── python-keyring
    └── zypper-changelog-lib
        └── Rockstor-Stable
            └── 43c30530-50e2-49a2-8a0f-f9b0ceae0402
```

The above credentials could have been added/updated via CLI:
```shell
pass add python-keyring/zypper-changelog-lib/Rockstor-Stable/43c30530-50e2-49a2-8a0f-f9b0ceae0402
# repo-pass-typed-in
```
Where `43c30530-50e2-49a2-8a0f-f9b0ceae0402` is the repository username counterpart.

Credentials can be removed via CLI:
```shell
pass delete python-keyring/zypper-changelog-lib/<repo-alias>/<auth-username>
```

Password retrieval via CLI:
```shell
pass python-keyring/zypper-changelog-lib/Rockstor-Stable/43c30530-50e2-49a2-8a0f-f9b0ceae0402
test-password
```

Password retrieval via Python:
```python
poetry shell
python
>>> import keyring
>>> import keyring_pass
>>> repo_auth = keyring.get_credential("zypper-changelog-lib/Rockstor-Testing", None)
>>> print(repo_auth)
None
>>> repo_auth = keyring.get_credential("zypper-changelog-lib/Rockstor-Stable", None)
>>> print(type(repo_auth))
<class 'keyring.credentials.SimpleCredential'>
>>> print(repo_auth.username)
43c30530-50e2-49a2-8a0f-f9b0ceae0402
>>> print(repo_auth.password)
test-password
```

**Note:** If credentials exist for a repository (by alias) that does not require authentication,
they will be retrieved, but not used: as the server will make no request for them.

### Debug

An example containing both package and repository filtering with all debug logging redirected to a file:

```shell
zypper refresh
poetry run zypper-changelog-lib -p zstd,acl,deltarpm -r openSUSE:update-slowroll -d 2> output-file.txt
```

### Known limitations

Internally the OS provided zstd package is used to uncompress .gz or .zst zypper cache files.
On Leap 15.6 and newer this is fine,
but on Leap 15.5 (EOL) the following is indicated via debug output:

```text
zstd: /var/cache/zypp/raw/...-primary.xml.gz: gzip file cannot be uncompressed (zstd compiled without HAVE_ZLIB) -- ignored
```

'Plaindir' type repositories are ignored as they have no associated/cached metadata.
Similarly, repositories added without the 'refresh' option, or pending a `zypper refresh`,
will also have no cached metadata.
And as such will also be ignored.

### Options and parameters

From:
```shell
poetry run zypper-changelog-lib --help
```

```
usage: zypper-changelog-lib [-h] [-p PACKAGES] [-r REPOS] [-of OUTF] [-d] [-t] [-re] [-AA]

Changelogs for installable pending updates, or available/uninstalled packages (requires options).

Note: '--all-available' alone is extreme: it retrieves rpm headers for
the latest version (per repo) of all available packages - taking no account of
what packages are installed. '--all-available' still heeds the filters
of '--packages' & '--repos' if specified, but the changelogs presented are
full default length: not a difference to any incidentally installed packages.

options:
  -h, --help            show this help message and exit
  -p PACKAGES, --packages PACKAGES
                        Comma separated list (no spaces) of package names to consider.
                        Default is all installed packages.
  -r REPOS, --repos REPOS
                        Comma separated list (no spaces) of repository aliases to consider.
                        Default is all enabled repositories.
  -of OUTF, --output-format OUTF
                        Options: 'json' - formatted single print, 'dict' - for library use.
                        Default is line-by-line prints.
  -d, --debug           Enable debug mode.
  -t, --titles-only     List only the changelog titles.
  -re, --regex          Enable regular expression in package names.
  -AA, --all-available  Changelogs for all available packages (latest versions only): USE WITH CAUTION.
```