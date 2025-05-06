#!/usr/bin/python3
# SPDX-FileCopyrightText: 2018 SUSE LLC
# SPDX-FileCopyrightText: 2025 The Rockstor Project <support@rockstor.com>
#
# SPDX-License-Identifier: LGPL-2.1-only
#
# -*- coding: utf-8 -*-
# Copyright © 2018 SUSE LLC
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; version 2.1.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Zoltán Balogh <zbalogh@suse.com>
# Author: 2025 rework Philip Guyton <support@rockstor.com>
# Summary: Simple tool to list changelogs of packages in the available
# repositories.

import argparse
import datetime
import difflib
import json
import logging
import os
import re
import tempfile
import time
import typing
from os.path import isdir
from subprocess import run, CalledProcessError, TimeoutExpired
import xml.etree.ElementTree as et
import platform
from time import sleep

import requests
import rpm
from keyring import get_credential
from keyring.credentials import SimpleCredential
from requests import RequestException, HTTPError, Timeout

import keyring
from keyring.errors import KeyringError

ARCH: str = platform.machine()
# Package index for package in root.findall
NAME_INDEX = 0
ARCH_INDEX = 1
# VERSION_INDEX = 3
LOCATION_INDEX = 10
FORMAT_INDEX = 11
# `Zypper versioncmp first second` return codes.
VERSIONS_EQUAL = 0
FIRST_NEWER = 11
SECOND_NEWER = 12

logger = logging.getLogger(__name__)


def _get_updates_per_repo(repo_list: typing.List[str] = [], max_wait: int = 14) -> typing.Dict[str, list]:
    """
    Fetch info on installable updates (all repos if no repo_list) via zypper call.
    Resolves as per 'zypper up' excluding packages with dependency problems.
    Adding `--all` includes packages with dependency problems.
    For "No updates found." {"": []} is returned.
    When updates available: {'libudev1', 'udev'}, {'repo-oss'}
    When updates available: {'repo-oss': ['libudev1', 'udev']}
    """
    per_repo_updates = {}
    repo_args = []
    if repo_list:  # construct list ["--repo"  repo_list[0] "--repo" repo_list[1]]
        for repo in repo_list:
            repo_args.append("--repo")
            repo_args.append(repo)
    try:
        # rc = 1 when out = "package * is not installed"
        zypp_run = run(
            ["zypper", "-x", "--non-interactive", "list-updates"] + repo_args,
            capture_output=True,
            encoding="utf-8",  # stdout and stderr as string
            universal_newlines=True,
            timeout=max_wait,
            check=True,
        )
    except CalledProcessError as e:
        logger.error(f"Error fetching updates from all, or indicated repos: {e}")
        return per_repo_updates
    except TimeoutExpired as e:
        logger.error(f"Consider using a repository filter, i.e. --repos: {e}")
        return per_repo_updates
    stdout_value = zypp_run.stdout
    updates_tree = et.ElementTree(et.fromstring(stdout_value))
    updates_root = updates_tree.getroot()
    for update in updates_root.iter('update'):
        repo_alias = update.find('source').get('alias')
        if repo_alias in per_repo_updates:
            per_repo_updates[repo_alias].append(update.get('name'))
        else:
            per_repo_updates[repo_alias] = [update.get('name')]
    return per_repo_updates


def _local_changelog(package: str, titles_only: bool = False, max_wait: int = 1) -> str:
    """
    Retrieve the changelog for a locally installed package via rpm call.
    If the package is not installed, rpm stderr=1, we return ""
    """
    try:
        rpm_run = run(
            ["rpm", "-q", "--changelog", package],
            capture_output=True,
            encoding="utf-8",  # stdout and stderr as string
            universal_newlines=True,
            timeout=max_wait,
            check=True,  # rc = 1 when out = "package * is not installed"
        )
    except CalledProcessError as e:
        logger.error(f"{e.stdout}Error fetching local changelog: ({e})")
        return ""
    if not titles_only:
        return rpm_run.stdout
    else:
        titles: str = ""
        for line in rpm_run.stdout.split('\n'):
            if line.startswith("*"):  # rpm changelog format for release title line.
                titles += line + "\n"
        return titles


def _fetch_rpm_header(url: str, end: str, retries: int = 2, backoff_factor: int = 2,
                      auth: SimpleCredential = None) -> bytes | None:
    """
    Fetch the RPM header from a remote repository.
    Uses `Range:` in request header: requires support on receiving server:
    `curl --head url` should contain: "Accept-Ranges: bytes"
    """
    logger.debug(f"++ CALLED fetch_rpm_header(url={url}, end={end}, auth={auth is not None})")
    for attempt in range(retries):  # [0 1] for retries = 2
        try:
            # https://requests.readthedocs.io/en/stable/user/advanced/#timeouts
            # timeout = (connect-timeout, read-timeout)
            # connect timeout: seconds to wait to establish initial connection.
            # read timeout: seconds to wait between bytes sent: mostly first byte wait.
            if not auth:
                response = requests.get(
                    url, headers={'Range': f'bytes=0-{end}'}, timeout=(3.5, 10)
                )
            else:
                response = requests.get(
                    url, headers={'Range': f'bytes=0-{end}'}, auth=(auth.username, auth.password), timeout=(3.5, 10)
                )
            # Expected `response.status_code` is 206 Partial Content
            response.raise_for_status()
            return response.content
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error connecting to repository: {e}")
            return None
        except Timeout as e:
            logger.error(f"Error fetching RPM header (attempt {attempt + 1}): {e}")
            # i.e. (1 * (2^0)) = 1s then (1 * (2^1)) = 2s (backoff_factor = 1)
            # i.e. (2 * (2^0)) = 2s then (2 * (2^1)) = 4s (backoff_factor = 2
            sleep(backoff_factor * (2 ** attempt))
            continue
        except HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            if response.status_code == 401:  # Unauthorized
                logger.error("Repo Authorization failure, ensure credentials are in keyring for this user.")
            return None
        # Catch all:
        except RequestException as e:
            logger.error(f"Unknown error connecting to repository: {e}")
            return None
    return None


def _get_zypper_repo_cache_filenames(repository_list=[]) -> typing.Dict[str, str]:
    """
    Get the *primary.xml.zst or *primary.xml.gz full path filename for each repo passed.
    Or for all cached repos if repository_list is empty.
    :return: Dictionary indexed by repo "alias" with *primary.xml.?(zst|gz) fullpath filenames.
    """
    dict_of_xml_files: typing.Dict[str, str] = {}
    # N.B. Directory names are equal to Repo Alias, not Name.
    cached_repos = os.listdir("/var/cache/zypp/raw/")
    if not repository_list:
        repository_list = cached_repos
    repodata_paths: typing.Dict[str, str] = {repo: f"/var/cache/zypp/raw/{repo}/repodata/" for repo in repository_list}
    for repo_alias, path in repodata_paths.items():
        if not isdir(path):
            continue  # 'plaindir' repos have no repodata, or uncached repo in repository_list.
        for file in os.listdir(path):
            if file.endswith("primary.xml.zst") or file.endswith("primary.xml.gz"):
                dict_of_xml_files[repo_alias] = f"{path}{file}"
    return dict_of_xml_files


def get_zypper_repo_dict(max_wait: int = 1) -> typing.Dict[str, str]:
    """
    Simple wrapper for "zypper -x lr" to extract alias-to-url info
    for enabled repos only.
    :return: Dictionary indexed by repo "alias" with "url" values.
    """
    alias_to_url: typing.Dict[str, str] = {}
    try:
        zypp_run = run(
            ["zypper", "-x", "lr"],
            capture_output=True,
            encoding="utf-8",  # stdout and stderr as string
            universal_newlines=True,
            timeout=max_wait,
            check=True,
        )
    except CalledProcessError as e:
        logger.error(f"{e.stdout}Error fetching repository list: ({e})")
        return {"": ""}
    stdout_value = zypp_run.stdout
    repo_tree = et.ElementTree(et.fromstring(stdout_value))
    repo_root = repo_tree.getroot()
    for repo in repo_root.iter('repo'):
        if repo.get('enabled') == "1":
            alias_to_url[repo.get('alias')] = repo.find('url').text
    return alias_to_url


def _decode_if_bytes(value) -> str:
    """Decode a value if it is in bytes."""
    # TODO: Remvoe in favour of in-lining to avoid call overheads,
    #  too trivial to abstract, and may no-longer be required.
    return value.decode("utf-8") if isinstance(value, bytes) else value


def _get_packages_zypp_cache_tree(xml_tree: et.ElementTree, pkg_list, regex_enabled: bool = False) -> dict:
    """
    Find the latest package info in cache_tree for packages in pkg_list.
    Or all latest package info if pkg_list empty.
    Note: cache contains all versions of each package within the associated repo.
    We need only the info from the latest version by publication date.
    Latest pkg versions are assumed to have all earlier version's changelog entries.
    :return: Dictionary indexed by package name, with dict value containing extracted info.
    """
    # Get root element from ElementTree
    root = xml_tree.getroot()  # e.g. <Element '{http://linux.duke.edu/metadata/common}metadata' at 0x7ff2759061b0>
    # print(et.dump(root))
    # <ns0:metadata xmlns:ns0="http://linux.duke.edu/metadata/common"
    # xmlns:ns1="http://linux.duke.edu/metadata/rpm"
    # packages="73">
    # root.tag = {http://linux.duke.edu/metadata/common}metadata
    xml_ns = root.tag.split('}')[0].strip('{')  # "http://linux.duke.edu/metadata/common"
    packages_info: dict = {}
    package_older: bool
    # N.B. Take care with the following loop's contents: many iterations on large repos.
    for package in root.findall('doc:package', namespaces={'doc': xml_ns}):
        package_older = False
        info_dict: dict = {}
        # ARCH CHECKS
        if package[ARCH_INDEX].text not in (ARCH, 'noarch'):
            continue
        # NAME CHECKS
        pkg_name = package[NAME_INDEX].text
        if pkg_list:
            if regex_enabled:
                if not any(
                        re.compile(p).match(pkg_name) for p in pkg_list
                ):
                    logger.debug(f"-- No regex match ({pkg_name})")
                    continue
            else:
                if pkg_name not in pkg_list:
                    logger.debug(f"-- Skipping package ({pkg_name})")
                    continue  # package has no update
        # Need `rpm:entry[1]` as sometimes there are two:
        # <rpm:entry name="rockstor" flags="EQ" epoch="0" ver="5.0.15" rel="0"/>
        # <rpm:entry name="rockstor(x86-64)" flags="EQ" epoch="0" ver="5.0.15" rel="0"/>
        # VERSION CHECKS
        for ver_info in package[FORMAT_INDEX].findall("./rpm:provides/rpm:entry[1]",
                                                      namespaces={'rpm': 'http://linux.duke.edu/metadata/rpm'}):
            # ver & rel can be None type
            ver: str | None = ver_info.get('ver')
            rel: str | None = ver_info.get('rel')
            info_dict["ver"]: str | None = ver
            info_dict["rel"]: str | None = rel
            if ver is None:  # assume no release also.
                info_dict["ver_rel"]: str = "None"
            else:  # we have a version.
                if rel is None:
                    info_dict["ver_rel"]: str = f"{ver}"
                else:  # we have a version and a release
                    info_dict["ver_rel"]: str = f"{ver}-{rel}"
            logger.debug(f"++ Found ({pkg_name}) ver-rel = {info_dict['ver_rel']}")
            if pkg_name in packages_info.keys():  # Ignore current version if saved is newer
                try:
                    zypp_vcmp_run = run(
                        ["zypper", "versioncmp", packages_info[pkg_name]['ver_rel'], info_dict["ver_rel"]],
                        capture_output=True,  # Faster (change to False for debug)
                        timeout=1,
                    )
                    rc = zypp_vcmp_run.returncode
                    if rc == VERSIONS_EQUAL or rc == FIRST_NEWER:
                        package_older = True
                except CalledProcessError as e:
                    logger.error(f"{e.stdout} Error comparing versions: ({e})")
                    continue
        if package_older:
            continue
        # GET RPM HEADER-RANGE
        for field in package[FORMAT_INDEX].findall(  # One 'rpm:header-range' field per package
                # <rpm:header-range start="4504" end="1511140"/>
                'rpm:header-range',
                namespaces={'rpm': 'http://linux.duke.edu/metadata/rpm'}
        ):
            # We get rpm.error if we don't get the file from zero bytes to header-end.
            # info_dict["header-start"]: str = field.get('start')  # around 4504 bytes in
            info_dict["header-end"]: str = field.get('end')  # KB to MB
            info_dict["href"]: str = package[LOCATION_INDEX].get("href")
        packages_info[pkg_name] = info_dict
    logger.debug(f"packages_info = {packages_info}")
    return packages_info


def get_zypper_changelog(repo_list=[], pkg_list=[], only_updates: bool = True,
                         titles_only: bool = False, regex_enabled: bool = False,
                         output_format: str | None = None) -> str | dict | None:
    """
    Library invocation: The importing agent should call this procedure.

    :param repo_list: default to considering all repos.
    :param pkg_list: default to all packages in repository_list repos.
    :param only_updates: changelog for packages (installed) with pending updates.
    :param titles_only: only show changelog titles.
    :param regex_enabled: enable package_list regex function.
    :param output_format: "json" - single print: json format, "dict" returns dict, None (default) line-by-line print.
    :return: Determined by output_format; default is None.
    """

    all_repos: bool = True
    if repo_list:
        all_repos = False

    # Used only if output_format is not None and known.
    # Indexed by pkg_name, value is list of changelog lines.
    changelog_dict: typing.Dict[str: list[str]] = {}

    per_repo_updates = {}
    if only_updates:
        logger.debug("Changelogs for installable pending updates")
        per_repo_updates = _get_updates_per_repo(repo_list)
        logger.debug(f"per_repo_updates = {per_repo_updates}")
        if not per_repo_updates:
            if not output_format:
                print("No updates found")
            return None

    # Initialize the RPM transaction set
    # https://jfearn.fedorapeople.org/en-US/RPM/4/html/RPM_Guide/ch16s04s02.html
    # Don't check; signature, RPM database header, digest.
    # Leave file handle position at beginning of payload.
    ts = rpm.TransactionSet("", (
            rpm._RPMVSF_NOSIGNATURES or rpm.RPMVSF_NOHDRCHK or
            rpm._RPMVSF_NODIGESTS or rpm.RPMVSF_NEEDPAYLOAD
    ))
    cache_files_dict = _get_zypper_repo_cache_filenames(repo_list)
    enabled_repos_dict = get_zypper_repo_dict()
    if not all_repos:
        enabled_repos_dict = {item: value for item, value in enabled_repos_dict.items() if item in repo_list}
    start_time: float = time.perf_counter()
    # Loop through all repo cache (alias, file) tuples.
    # Consider refactor re moving outer loop to enabled_repos_dict.
    for cached_repo_alias, zypp_cache_file in cache_files_dict.items():
        logger.debug(f"Considering cached repo ({cached_repo_alias}), file {zypp_cache_file}")
        url: str = ""
        # Check corresponding repo is enabled, skip otherwise.
        if cached_repo_alias in enabled_repos_dict.keys():
            url = enabled_repos_dict[cached_repo_alias]
            logger.debug(f"++ Cached Repo has enabled repo URL: {url}")
        else:
            logger.debug(f"-- Cached Repo has no matching enabled repo")
            continue
        # Skip cached_repo if updates_only and no package intersection with pkg_list.
        pkg_list_per_repo = pkg_list
        repo_regex_applied = not regex_enabled
        if only_updates:
            # We know package updates per repo.
            # If no updates from this repo, skip.
            if cached_repo_alias not in per_repo_updates.keys():
                logger.debug("-- No installable updates associated with this repo.")
                continue
            # We know user requested pkg_list:
            repo_pkg_updates = per_repo_updates[cached_repo_alias]
            if not regex_enabled:
                if pkg_list:  # User passed a packages filter
                    pkg_intersection = list(set(repo_pkg_updates) & set(pkg_list))
                else:
                    pkg_intersection = repo_pkg_updates  # All updates for this repo
            else:  # regex_enabled
                # Find intersection assuming regex entries in pkg_list
                intersection: set[str] = set()
                for pkg_update in repo_pkg_updates:
                    for regex in pkg_list:
                        if re.match(regex, pkg_update) is not None:
                            intersection.add(pkg_update)
                pkg_intersection = list(intersection)
                repo_regex_applied = True
            if not pkg_intersection:
                logger.debug("-- No intersection with installable updates, packages filter, and this repo.")
                continue
            else:
                pkg_list_per_repo = pkg_intersection
                logger.debug(
                    f"++ Intersection for installable updates, package filter, and this repo: {pkg_list_per_repo}")
        # zstd decompress zypper cache file. Approx 20/200 MB compressed/uncompressed.
        # OOM seen on 2 GB RAM with 32/455 MB compressed/uncompressed openSUSE:update-slowroll cache file.
        # 2.5 GB RAM min required for similarly sized raw cache files.
        #   `zypper clean --raw-metadata` & `zypper refresh`
        # `--memory=` default max 128 MiB for decompression.
        # `--quite` suppress progress and input filename/size info.
        # `--force` overwrite file if it exists.
        # `-o` output filename.
        with tempfile.NamedTemporaryFile() as zypp_cache_tempfile:
            try:
                unzstd_run = run(
                    ["unzstd", zypp_cache_file, "--quiet", "--force", "-o", zypp_cache_tempfile.name],
                    capture_output=False,
                    timeout=3,
                    check=True,
                )
            except CalledProcessError as e:
                logger.error(f"Error decompressing XML file: {e}")
                continue
            except TimeoutExpired as e:
                logger.error(f"Timeout in decompressing zypper cache file: {e}")
                continue
            # XML tree from above `zstdcat zypp_cache_file` output
            try:
                tree = et.ElementTree(file=zypp_cache_tempfile.name)
            except et.ParseError as e:
                logger.error(f"Error parsing XML file: {e}")
                continue
        logger.debug(f"Zypper cache file XML-parsed for repo: ({cached_repo_alias})")
        # Note: not repo_regex_applied avoids re-applying regex, when enabled.
        # For only_updates this has already been done on installable updates.
        cached_pkg_info = _get_packages_zypp_cache_tree(tree, pkg_list_per_repo,
                                                        not repo_regex_applied and regex_enabled)
        # Look for repo associated credentials, if none found assume none needed.
        repo_auth: SimpleCredential | None = None
        logger.debug("Query keyring for repository credentials.")
        try:
            repo_auth = get_credential(service_name=f"zypper-changelog-lib/{cached_repo_alias}", username=None)
            # If not in password store, stdout (debug log) contains:
            # Error: python-keyring/zypper-changelog-lib/Rockstor-Stable is not in the password store.
            # None type returned (not an exception).
        # Greater fidelity in reporting would be nice, i.e. NoKeyringError
        except keyring.errors.KeyringError as e:
            logger.debug(f"KeyringError - for repo user/pass from service `zypper-changelog-lib`. Skipping repo.: {e}")
            continue
        if not repo_auth:
            logger.info("Assuming repo requires no authentication")
        else:
            logger.debug("Credentials for repo authentication retrieved.")
        for pkg_name, pkg_info in cached_pkg_info.items():
            # Package name 'header' before the associated changelog output.
            pkg_ver_rel: str = pkg_info['ver_rel']
            match output_format:
                case None:
                    print(f"Package: {pkg_name} {pkg_ver_rel}")
                case "dict" | "json":
                    # TODO: here we fail to account for same pkg_name in multiple repos.
                    #   Wipes existing changelog for same pkg_name from a prior repo.
                    # Place pkg_ver_rel as first entry in changelog.
                    changelog_dict[pkg_name] = [pkg_ver_rel]
            # RPM header retrieval.
            rpm_header_url = f"{url}/{pkg_info['href']}"
            rpm_header_content = _fetch_rpm_header(rpm_header_url, pkg_info["header-end"], auth=repo_auth)
            if rpm_header_content is None:
                logger.debug("No content received")
                continue  # Skip changelog output for this package.
            logger.debug("rpm_header_content retrieved")
            # Write rpm_header_content to named temp file.
            # Read temp file using read_rpm_header().
            # Buffering 4096 or 8192 bytes long (binary mode)
            with tempfile.NamedTemporaryFile() as temp_rpm_header:
                temp_rpm_header.write(rpm_header_content)
                temp_rpm_header.flush()
                temp_rpm_header.seek(0)
                try:
                    # http://ftp.rpm.org/api/4.4.2.2/classRpmhdr.html
                    rpmheader = ts.hdrFromFdno(temp_rpm_header.name)
                except rpm.error as e:
                    logger.error(f"Error reading RPM header: {e}")
                    continue
                if rpmheader is None:
                    continue
            changelog_name = rpmheader[rpm.RPMTAG_CHANGELOGNAME]
            changelog_time = rpmheader[rpm.RPMTAG_CHANGELOGTIME]
            changelog_text = rpmheader[rpm.RPMTAG_CHANGELOGTEXT]
            # Retrieval from header of version-release if None from cachefile parsing.
            if pkg_ver_rel == "None":  # We failed to get this info from zypper cache, try via rpm header:
                logger.debug("'None' ver-rel substitution from rpm header.")
                rpm_version = rpmheader["version"]
                rpm_release = rpmheader["release"]
                header_ver_rel = f"{rpm_version}-{rpm_release}"
                match output_format:
                    case None:
                        print(f"Package: {pkg_name} {header_ver_rel} (from rpm header).")
                    case "dict" | "json":
                        # TODO: here we fail to account for same pkg_name in multiple repos.
                        #   Wipes existing changelog for same pkg_name from a prior repo.
                        # Place header_ver_rel as first entry in changelog.
                        changelog_dict[pkg_name] = [header_ver_rel]
            changelog = ''
            for cname, ctime, ctext in zip(
                    changelog_name, changelog_time, changelog_text
            ):
                cname = _decode_if_bytes(cname)
                ctext = _decode_if_bytes(ctext)
                dt = datetime.datetime.fromtimestamp(ctime).strftime(
                    "%a %b %d %Y"
                )
                if titles_only:
                    changelog += f"* {dt} {cname}\n"
                else:
                    changelog += f"* {dt} {cname}\n{ctext}\n\n"

            if only_updates:
                local = _local_changelog(pkg_name, titles_only)
                diff = difflib.ndiff(local.split('\n'), changelog.split('\n'))
                for line in diff:
                    if line.startswith('+ '):
                        match output_format:
                            case None:
                                print(line.replace('+ ', ''))
                            case "dict" | "json":
                                changelog_dict[pkg_name].append(line.replace('+ ', ''))
            else:
                match output_format:
                    case None:
                        print(changelog)
                    case "dict" | "json":
                        changelog_dict[pkg_name].extend(changelog.split('\n'))

            logger.debug(f"Finished processing {pkg_name}")
    end_time: float = time.perf_counter()
    logger.debug(f"-- TIMED get_zypper_changelog(): {end_time - start_time} sec")
    match output_format:
        case "dict":
            return changelog_dict
        case "json":
            print(json.dumps(changelog_dict, indent=2))
        case _:
            return None


def main():
    """
    Command line invocation: non-boolean arguments are None by default.
    All boolean types are False by default.
    All defaults (no arguments) requests changelogs for all pending updates.
    All options (except '--all-available' & '--debug') filter the above function.
    """
    warning_text = ("Note: '--all-available' alone is extreme: it retrieves rpm headers for\n"
                    "the latest version (per repo) of all available packages - taking no account of\n"
                    "what packages are installed. '--all-available' still heeds the filters\n"
                    "of '--packages' & '--repos' if specified, but the changelogs presented are\n"
                    "full default length: not a difference to any incidentally installed packages.")
    parser = argparse.ArgumentParser(
        prog='zypper-changelog-lib',
        description='Changelogs for installable pending updates,'
                    ' or available/uninstalled packages (requires options).\n\n' + warning_text,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-p", "--packages", dest="packages",
        help="Comma separated list (no spaces) of package names to consider.\nDefault is all installed packages."
    )
    parser.add_argument(
        "-r", "--repos", dest="repos",
        help="Comma separated list (no spaces) of repository aliases to consider.\nDefault is all enabled repositories."
    )
    parser.add_argument(
        "-of", "--output-format", dest="outf",
        help="Options: 'json' - formatted single print, 'dict' - for library use.\nDefault is line-by-line prints."
    )
    parser.add_argument(
        '-d', '--debug', dest='debug', default=False, action='store_true',
        help='Enable debug mode.'
    )
    parser.add_argument(
        '-t', '--titles-only', dest='titles_only', default=False, action='store_true',
        help='List only the changelog titles.'
    )
    parser.add_argument(
        '-re', '--regex', dest='regex', default=False, action='store_true',
        help='Enable regular expression in package names.'
    )
    parser.add_argument(
        "-AA", "--all-available", dest="all", default=False, action='store_true',
        help="Changelogs for all available packages (latest versions only): USE WITH CAUTION."
    )

    args = parser.parse_args()

    loglevel = logging.INFO
    if args.debug:
        loglevel = logging.DEBUG
    # No `stream=` defaults to sys.stderr which works for us.
    logging.basicConfig(level=loglevel)

    pkg_list = []
    if args.packages:
        pkg_list = args.packages.split(",")
    repo_list = []
    if args.repos:
        repo_list = args.repos.split(",")

    get_zypper_changelog(repo_list=repo_list, pkg_list=pkg_list, only_updates=not args.all,
                         titles_only=args.titles_only, regex_enabled=args.regex, output_format=args.outf)


if __name__ == "__main__":
    main()
