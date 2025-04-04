import typing

from ckan.plugins import toolkit

from .. import constants
from . import _CkanBootstrapOrganization, _CkanExtBootstrapPage

_staff_org_title = toolkit.config.get(
    "ckan.wro.portal_staff_organization_title", "WRO staff"
)
_staff_org_name = _staff_org_title.replace(" ", "-").lower()[:100]


WRO_ORGANIZATIONS: typing.Final[typing.List[_CkanBootstrapOrganization]] = [
    _CkanBootstrapOrganization(
        name=constants.SANSA_ORG_NAME,
        title="SANSA",
        description=(
            "no description yet"
        ),
    ),
    _CkanBootstrapOrganization(
        name=_staff_org_name,
        title=_staff_org_title,
        description=(
            f"The {_staff_org_title} organization is responsible for the maintenance of "
            f"the static contents for the EMC portal"
        ),
    ),
]

PORTAL_PAGES: typing.Final[typing.List[_CkanExtBootstrapPage]] = [
    _CkanExtBootstrapPage(
        name="help",
        content=(
            "This is the WRO help section. It contains resources to help you use the "
            "WRO effectively\n\n"
            "- [Frequently Asked Questions](frequently-asked-questions)"
        ),
        private=False,
        order="3",
    ),
    _CkanExtBootstrapPage(
        name="about",
        content=("Welcome to the WRO Portal"),
        private=False,
        order="4",
    ),
    _CkanExtBootstrapPage(
        name="frequently-asked-questions",
        content=(
            "This is the default FAQ section\n\n"
            "1. What is this?\n\n"
            "    Its a metadata catalogue\n\n"
            "2. Can I link between pages?\n\n"
            "    It seems so: here is a link to the [help](help) page"
        ),
        private=False,
    ),
]
