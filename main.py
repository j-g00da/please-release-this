import sys

from packaging.utils import canonicalize_name
import re
import stdlib_list
from itertools import chain
import requests

from normalize import normalize_pep426_name, ultranormalize_name
from typosnyper import typo_check_name, _TOP_PROJECT_NAMES

# https://github.com/pypi/warehouse/blob/691680fa603cce2375505b3b265fe72c0e5ca451/warehouse/utils/project.py#L30C1-L32C2
PROJECT_NAME_RE = re.compile(
    r"^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])\Z", re.IGNORECASE
)

# https://github.com/pypi/warehouse/blob/691680fa603cce2375505b3b265fe72c0e5ca451/warehouse/packaging/services.py#L60C1-L64C43
def _namespace_stdlib_list(module_list):
    for module_name in module_list:
        parts = module_name.split(".")
        for i, part in enumerate(parts):
            yield ".".join(parts[: i + 1])

# https://github.com/pypi/warehouse/blob/691680fa603cce2375505b3b265fe72c0e5ca451/warehouse/packaging/services.py#L67C1-L73C2
STDLIB_PROHIBITED = {
    canonicalize_name(s.rstrip("-_.").lstrip("-_."))
    for s in chain.from_iterable(
        _namespace_stdlib_list(stdlib_list.stdlib_list(version))
        for version in stdlib_list.short_versions
    )
}


def check_project_name(name: str) -> None:
    """
    This closely matches `ProjectService.check_project_name` in PyPI warehouse.
    https://github.com/pypi/warehouse/blob/691680fa603cce2375505b3b265fe72c0e5ca451/warehouse/packaging/services.py#L449
    """

    print(f"Checking {name} against PROJECT_NAME_RE...")
    if not PROJECT_NAME_RE.match(name):
        raise Exception("PROJECT_NAME_RE check failed.")
    print("Ok.")

    print(f"Checking {canonicalize_name(name)} against STDLIB_PROHIBITED...")
    if canonicalize_name(name) in STDLIB_PROHIBITED:
        raise Exception("STDLIB_PROHIBITED check failed.")
    print("Ok.")

    # Here we should also check for prohibited names... todo


    # similarity check
    print("Checking for similar package names...")
    # get all packages from pypi (yeah)
    response = requests.get(f"https://pypi.org/simple", headers={"Accept": "application/vnd.pypi.simple.v1+json"}).json()
    projects = response["projects"]

    pep426_name = normalize_pep426_name(name)
    ultranormalized_name = ultranormalize_name(name)
    for project in projects:
        pep426_other = normalize_pep426_name(project["name"])
        if pep426_name == pep426_other:
            raise Exception(f"PEP426 name check failed, collision with {project['name']}r (pep426-normalized to {pep426_name}r)")

        ultranormalized_other = ultranormalize_name(project["name"])
        if ultranormalized_name == ultranormalized_other:
            raise Exception(f"ultranormalized name check failed, collision with {project['name']}r (ultranormalized to {ultranormalized_name}r)")
    print("Ok.")

    # typo-squatting check
    # normally this checks for the "top dependents in pypi"
    # we are using here a hardcoded list instead
    print("Checking for typos against top dependents corpus...")
    if typo_check_match := typo_check_name(canonicalize_name(name), _TOP_PROJECT_NAMES):
        raise Exception(f"typo check failed, {typo_check_match[0]}r matches {typo_check_match[1]}r.")
    print("Ok.")

    print(f"Congratulations! Your package name {name} survived.")



if __name__ == "__main__":
    check_project_name(sys.argv[1])
