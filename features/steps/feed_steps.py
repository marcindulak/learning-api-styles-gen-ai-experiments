"""Steps for the Atom forecast feed assertions.

The feed XML is parsed from context.response (set by the shared GET
request steps) with ElementTree; entry-level steps parse lazily so each
scenario can start its assertions at any step.
"""
import xml.etree.ElementTree as ElementTree
from datetime import datetime

import parse
from behave import register_type, then

ATOM_NAMESPACE = "http://www.w3.org/2005/Atom"


@parse.with_pattern(r'[^"]*')
def parse_quoted(text):
    return text


# Registered locally: importing another step module would re-register
# its steps (see webhook_steps.py).
register_type(Q=parse_quoted)


def feed_root(context):
    return ElementTree.fromstring(context.response.content)


def feed_entries(context):
    entries = feed_root(context).findall(f"{{{ATOM_NAMESPACE}}}entry")
    assert entries, "the feed contains no entry elements"
    return entries


@then(
    'the response body is a well-formed XML document with root element '
    '"{tag:Q}" in the Atom namespace "{namespace:Q}"'
)
def step_feed_is_well_formed_atom(context, tag, namespace):
    try:
        root = feed_root(context)
    except ElementTree.ParseError as error:
        raise AssertionError(f"response body is not well-formed XML: {error}")
    expected = f"{{{namespace}}}{tag}"
    assert root.tag == expected, (
        f'expected root element "{expected}", got "{root.tag}"'
    )


@then('the feed contains a "{tag:Q}" element mentioning "{text:Q}"')
def step_feed_element_mentions(context, tag, text):
    elements = feed_root(context).findall(f"{{{ATOM_NAMESPACE}}}{tag}")
    assert elements, f'the feed contains no "{tag}" element'
    contents = [element.text or "" for element in elements]
    assert any(text in content for content in contents), (
        f'no feed "{tag}" element mentions "{text}": {contents}'
    )


@then('the feed contains {count:d} "{tag:Q}" elements')
def step_feed_element_count(context, count, tag):
    elements = feed_root(context).findall(f"{{{ATOM_NAMESPACE}}}{tag}")
    actual = len(elements)
    assert actual == count, f'expected {count} "{tag}" elements, got {actual}'


@then('every feed entry contains a "{tag:Q}" element')
def step_every_entry_has_element(context, tag):
    for index, entry in enumerate(feed_entries(context)):
        element = entry.find(f"{{{ATOM_NAMESPACE}}}{tag}")
        assert element is not None, f'entry {index} has no "{tag}" element'


@then(
    'every feed entry contains an "{tag:Q}" element '
    "with a valid RFC 3339 timestamp"
)
def step_every_entry_has_rfc3339_element(context, tag):
    for index, entry in enumerate(feed_entries(context)):
        element = entry.find(f"{{{ATOM_NAMESPACE}}}{tag}")
        assert element is not None, f'entry {index} has no "{tag}" element'
        value = element.text or ""
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise AssertionError(
                f'entry {index} "{tag}" is not an RFC 3339 timestamp: "{value}"'
            )
        assert parsed.tzinfo is not None, (
            f'entry {index} "{tag}" lacks the RFC 3339 UTC offset: "{value}"'
        )


@then('every feed entry contains a "{tag:Q}" element mentioning "{text:Q}"')
def step_every_entry_element_mentions(context, tag, text):
    for index, entry in enumerate(feed_entries(context)):
        element = entry.find(f"{{{ATOM_NAMESPACE}}}{tag}")
        assert element is not None, f'entry {index} has no "{tag}" element'
        content = element.text or ""
        assert text in content, (
            f'entry {index} "{tag}" does not mention "{text}": "{content}"'
        )
