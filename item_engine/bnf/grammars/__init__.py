import os
import re
from typing import Tuple, List
from shutil import copytree

VERSION_REGEX = re.compile(r"^(?P<name>\w+)_(?P<major>\d+)_(?P<minor>\d+)_(?P<patch>\d+)$")

GRAMMAR_PACKAGE = __path__[0] if isinstance(__path__, list) else __path__


def get_all_versions(lang: str) -> List[Tuple[int, int, int]]:
    """Return the list of version available for a given lang"""
    versions = []

    for filename in os.listdir(GRAMMAR_PACKAGE):
        match = VERSION_REGEX.match(filename)
        if match:
            if match['name'] == lang:
                version = (int(match['major']), int(match['minor']), int(match['patch']))
                versions.append(version)

    return versions


def get_latest_version(lang: str) -> Tuple[int, int, int]:
    """Return the latest version available for a given lang"""
    versions = get_all_versions(lang)

    if versions:
        return max(versions)


def get_version_name(lang: str, major: int, minor: int, patch: int):
    """Return the package name associated with the lang ``name`` and version (``major``, ``minor``, ``patch``)"""
    return f"{lang}_{major}_{minor}_{patch}"


def new_patch_path(lang) -> str:
    """Return the name associated with the next patch for the specified lang ``name``"""
    major, minor, patch = get_latest_version(lang)
    return get_version_name(lang, major, minor, patch + 1)


def load_version(dst: str, lang: str, major: int, minor: int, patch: int):
    """This will copy the required version of the lang at ``dst``"""
    copytree(
        src=os.path.join(GRAMMAR_PACKAGE, get_version_name(lang, major, minor, patch)),
        dst=dst
    )


def load_latest_version(lang: str, dst: str):
    """This will copy the latest version of the lang at ``dst``"""
    latest_version = get_latest_version(lang)
    load_version(dst, lang, *latest_version)
    return latest_version
