#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-11-14
#

"""Common workflow variables and functions."""

from __future__ import absolute_import, print_function

import logging
import os
from collections import OrderedDict
from typing import Final, Union

from workflow import Variables

log = logging.getLogger("workflow")


# Default workflow settings
DEFAULT_SETTINGS: Final[dict[str, list[str]]] = {
    "locales": [
        "en",
        "de_DE",
        "es_ES",
        "fr_FR",
    ],
}

DOCS_URL: Final[str] = "https://github.com/deanishe/alfred-fakeum/blob/master/README.md"
HELP_URL: Final[
    str
] = "https://www.alfredforum.com/topic/5319-fakeum-—-generate-fake-test-datasets-in-alfred/"
ISSUE_URL: Final[str] = "https://github.com/deanishe/alfred-fakeum/issues"
UPDATE_SETTINGS: Final[dict[str, str]] = {"github_slug": "deanishe/alfred-fakeum"}

# Workflow icons
ICON_DOCS: Final[str] = "icons/docs.png"
ICON_HELP: Final[str] = "icons/help.png"
ICON_ISSUE: Final[str] = "icons/issue.png"
ICON_ON: Final[str] = "icons/on.png"
ICON_OFF: Final[str] = "icons/off.png"
ICON_LOCALES: Final[str] = "icons/locales.png"
ICON_UPDATE_CHECK: Final[str] = "icons/update-check.png"
ICON_UPDATE_AVAILABLE: Final[str] = "icons/update-available.png"

# All locales supported by faker
ALL_LOCALES: OrderedDict[str, str] = OrderedDict(
    (
        ("en", "English"),
        ("de_DE", "German"),
        ("es", "Spanish"),
        ("fr_FR", "French"),
        ("ar_AA", "Arabic"),
        ("ar_EG", "Arabic (Egypt)"),
        ("ar_JO", "Arabic (Jordan)"),
        ("ar_PS", "Arabic (Palestine)"),
        ("ar_SA", "Arabic (Saudi Arabia)"),
        ("bs_BA", "Bosnian"),
        ("bg_BG", "Bulgarian"),
        ("zh_CN", "Chinese (China)"),
        ("zh_TW", "Chinese (Taiwan)"),
        ("hr_HR", "Croatian"),
        ("cs_CZ", "Czech"),
        ("dk_DK", "Danish"),
        ("nl_NL", "Dutch"),
        ("nl_BE", "Dutch (Belgium)"),
        ("en_AU", "English (Australia)"),
        ("en_CA", "English (Canada)"),
        ("en_GB", "English (Great Britain)"),
        ("en_TH", "English (Thailand)"),
        ("en_US", "English (United States)"),
        ("et_EE", "Estonian"),
        ("fi_FI", "Finnish"),
        ("fr_CH", "French (Switzerland)"),
        ("ka_GE", "Georgian"),
        ("de_AT", "German (Austria)"),
        ("tw_GH", "Ghanaian"),
        ("el_GR", "Greek"),
        ("he_IL", "Hebrew"),
        ("hi_IN", "Hindi"),
        ("hu_HU", "Hungarian"),
        ("id_ID", "Indonesian"),
        ("it_IT", "Italian"),
        ("ja_JP", "Japanese"),
        ("ko_KR", "Korean"),
        ("la", "Latin"),
        ("lv_LV", "Latvian"),
        ("lt_LT", "Lithuanian"),
        ("ne_NP", "Nepali"),
        ("no_NO", "Norwegian"),
        ("fa_IR", "Persian"),
        ("pl_PL", "Polish"),
        ("pt_BR", "Portuguese (Brazil)"),
        ("pt_PT", "Portuguese (Portugal)"),
        ("ru_RU", "Russian"),
        ("sk_SK", "Slovakian"),
        ("sl_SI", "Slovenian"),
        ("es_MX", "Spanish (Mexico)"),
        ("es_ES", "Spanish (Spain)"),
        ("sv_SE", "Swedish"),
        ("th_TH", "Thai"),
        ("tr_TR", "Turkish"),
        ("uk_UA", "Ukranian"),
    )
)


# Workflow's bundle IDs
BUNDLE_ID: Final[str] = os.getenv("alfred_workflow_bundleid")

# Script Filter keyword
KEYWORD: Final[str] = os.getenv("keyword")


def boolvar(name: str, default: bool = False) -> bool:
    """Return `True` or `False` for a workflow variable."""
    v: str = os.getenv(name)
    if v is not None:
        if v.lower() in ("1", "on", "yes"):
            return True

        if v.lower() in ("0", "off", "no"):
            return False
    log.debug(f'no value set for workflow variable "{name}", "using default: {default}"')
    return default


def intvar(name: str, default: int = 0) -> int:
    """Return `int` for a workflow variable."""
    v: Union[str, int] = os.getenv(name)
    if v is not None:
        try:
            v = int(v)
        except ValueError:
            log.error(f'bad value for "{name}": "{v}" is not a number')
            return default
        return v
    log.debug(f'no value set for workflow variable "{name}", "using default: {default}"')
    return default


def notify(title: str, text: str = "") -> None:
    """Show a notification."""
    if not boolvar("SHOW_NOTIFICATIONS"):
        return

    v: Variables = Variables(title=title, text=text)
    print(v)
