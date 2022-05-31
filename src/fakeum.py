#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-12-29
#

"""Alfred workflow to generate test data."""

from __future__ import absolute_import, print_function

import datetime
import os
import random
import sys
from collections import OrderedDict
from logging import Logger
from typing import Final, Optional, Union

import faker

from common import DEFAULT_SETTINGS, ISSUE_URL, UPDATE_SETTINGS, intvar
from workflow import ICON_WARNING, MATCH_ALL, MATCH_ALLCHARS, Workflow3
from workflow.util import run_trigger

# Query delimiter that separates faker name from quantity
DELIMITER: Final[str] = "✕"

# Number of sentences per paragraph of Lipsum text
LIPSUMS: Final[int] = intvar("LIPSUM_SENTENCES", 3)
SNIPPET_MODE: Final[Optional[str]] = os.getenv("SNIPPET_MODE") is not None

# ALFRED_AS = 'tell application "Alfred 2" to search "fake "'

FAKERS: OrderedDict[str, str] = OrderedDict(
    [
        # People
        ("Name", "name"),
        ("First Name", "first_name"),
        ("Last Name", "last_name"),
        ("Email", "email"),
        ("Email (corporate)", "company_email"),
        ("Email (free)", "free_email"),
        ("Email (safe)", "safe_email"),
        ("Email domain (free)", "free_email_domain"),
        ("Social Security No.", "ssn"),
        ("Phone No.", "phone_number"),
        ("MSISDN", "msisdn"),
        # Addresses
        ("Address", "address"),
        ("Street", "street_address"),
        ("Street Name", "street_name"),
        ("City", "city"),
        ("Postcode", "postcode"),
        ("State", "state"),
        ("State abbr.", "state_abbr"),
        ("Country", "country"),
        # Internet
        ("TLD", "tld"),
        ("Domain Name", "domain_name"),
        ("Domain Word", "domain_word"),
        ("IP Address (IPv4)", "ipv4"),
        ("IP Address (IPv6)", "ipv6"),
        ("URI", "uri"),
        ("URI path", "uri_path"),
        ("URL", "url"),
        ("User-Agent", "user_agent"),
        # Corporate bullshit
        ("Corporate BS", "bs"),
        ("Corporate catchphrase", "catch_phrase"),
        ("Company", "company"),
        ("Company suffix", "company_suffix"),
        # Lorem
        ("Paragraph", "paragraph"),
        ("Sentence", "sentence"),
        ("Word", "word"),
        # Dates and times
        ("Date", "date"),
        ("Datetime", "date_time"),
        ("ISO 8601 Datetime", "iso8601"),
        ("Time", "time"),
        ("Timezone", "timezone"),
        ("UNIX Timestamp", "unix_time"),
        # Banking
        ("Credit Card Provider", "credit_card_provider"),
        ("Credit Card No.", "credit_card_number"),
        ("Credit Card Expiry Date", "credit_card_expire"),
        ("Credit Card Full", "credit_card_full"),
        ("Credit Card Security No.", "credit_card_security_code"),
        ("IBAN", "iban"),
        ("BBAN", "bban"),
        ("Bank Country Code", "bank_country"),
        ("Currency", "currency_name"),
        ("Currency Code", "currency_code"),
        ("Cryptocurrency", "cryptocurrency_name"),
        ("Cryptocurrency Code", "cryptocurrency_code"),
        # Barcodes
        ("EAN", "ean"),
        ("EAN 8", "ean8"),
        ("EAN 13", "ean13"),
        ("ISBN 10", "isbn10"),
        ("ISBN 13", "isbn13"),
        # Colours
        ("Colour Name", "color_name"),
        ("Colour Name (Safe)", "safe_color_name"),
        ("Hex Colour", "hex_color"),
        ("Hex Colour (Safe)", "safe_hex_color"),
        ("RGB Colour", "rgb_color"),
        ("RGB CSS Colour", "rgb_css_color"),
        # Miscellaneous
        ("Profession", "job"),
        ("Licence Plate", "license_plate"),
        ("MD5 Hash", "md5"),
        ("SHA1 Hash", "sha1"),
        ("SHA256 Hash", "sha256"),
        ("Locale", "locale"),
        ("Language Code", "language_code"),
        ("UUID4", "uuid4"),
        ("Password (not secure!!)", "password"),
    ]
)

log: Optional[Logger] = None
fakers: list[faker.Generator] = []


def all_fakers() -> list[faker.Generator]:
    """Return all fakers."""
    global fakers
    if not fakers:
        for loc in wf.settings.get("locales", DEFAULT_SETTINGS["locales"]):
            fakers.append(faker.Factory.create(loc))

    return fakers


def get_faker(name: str = None) -> faker.Generator:
    """Return random faker instance."""
    import faker

    fakers: list[faker.Generator] = all_fakers()

    if name is None:
        return random.choice(fakers)

    random.shuffle(fakers)
    methname = FAKERS[name]
    for faker in fakers:
        if hasattr(faker, methname):
            return faker


def get_fake_datum(name: str) -> Optional[str]:
    """Return one fake datum for name."""
    faker = get_faker(name)
    if not faker:
        return None

    methname = FAKERS[name]
    if name == "Paragraph":  # Pass no. of sentences to generator
        datum = getattr(faker, methname)(LIPSUMS, False)
    else:
        datum = getattr(faker, methname)()

    if isinstance(datum, int):
        datum = str(datum)

    elif isinstance(datum, datetime.datetime):
        datum = datum.strftime("%Y-%m-%d %H:%M:%S")

    elif not isinstance(datum, str) or not isinstance(datum, bytes):
        log.debug(f"{name} : ({datum.__class__}) {datum}")

    return datum


def supported_type(name: str) -> bool:
    """Return ``True`` if at least one Faker supports this type."""
    methname = FAKERS[name]
    for faker in all_fakers():
        if hasattr(faker, methname):
            return True

    log.debug(f'data type "{name}" is not supported by active locales')
    return False


def get_fake_data(names: Optional[list[str]] = None, count: int = 1) -> list[list[str]]:
    """Return list of fake data."""
    fake_data: list = []

    if not names:
        names = sorted(FAKERS.keys())

    names = [n for n in names if supported_type(n)]

    for name in names:
        data: Union[list, str] = []
        for _ in range(count):
            data.append(get_fake_datum(name))

        if name in ("Paragraph", "Address"):
            data = "\n\n".join(data)
        else:
            data = "\n".join(data)

        fake_data.append((name, data))

    return fake_data


def main(wf: Workflow3) -> None:
    """Run workflow."""
    if wf.update_available:
        wf.add_item(
            "A newer version is available",
            "↩ to install update",
            autocomplete="workflow:update",
            icon="update-available.png",
        )

    query: Optional[str] = None

    if len(wf.args):
        query = wf.args[0]

    log.debug(f"query={query}")

    count: Union[int, str] = 0

    if DELIMITER in query:
        if query.endswith(DELIMITER):
            # Back up to empty query
            run_trigger("fake")
            return

        query, count = [s.strip() for s in query.split(DELIMITER)]

        if count:
            if isinstance(count, str) and not count.isdigit():
                wf.add_item(f"Not a number : {count} Please enter a number", icon=ICON_WARNING)
                wf.send_feedback()
                return

            count = int(count)
        else:
            count = 1

        fake_data = get_fake_data(names=[query], count=count)

    else:
        # Save last query so we can jump back to it if user backs up
        # wf.cache_data('last_query', query, session=True)

        fake_data: list[list[str]] = get_fake_data()

        if query:

            fake_data = wf.filter(
                query, fake_data, lambda t: t[0], match_on=MATCH_ALL ^ MATCH_ALLCHARS, min_score=20
            )

    log.debug(f"count={count}")

    if not fake_data:
        wf.add_item("No matching fakers", "Try a different query", icon=ICON_WARNING)

    for name, data in fake_data:

        subtitle = data
        if count:
            example = data.split("\n")[0].strip()
            subtitle = f'{count} ✕ e.g. "{example}"'

        it = wf.add_item(
            name,
            subtitle,
            arg=data,
            autocomplete=f"{name} {DELIMITER} ",
            valid=True,
            largetext=data,
            copytext=data,
        )

        it.setvar("title", "Copied to Clipboard")
        it.setvar("text", data)

        if SNIPPET_MODE:
            it.setvar("paste", "1")
        else:
            mod = it.add_modifier("cmd", "Paste to frontmost application")
            mod.setvar("paste", "1")
            mod.setvar("SHOW_NOTIFICATIONS", "0")

    wf.send_feedback()


if __name__ == "__main__":
    wf: Workflow3 = Workflow3(
        default_settings=DEFAULT_SETTINGS,
        update_settings=UPDATE_SETTINGS,
        help_url=ISSUE_URL,
        libraries=["./libs"],
    )
    log: Logger = wf.logger
    sys.exit(wf.run(main))
