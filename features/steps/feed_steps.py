"""
Step definitions for Feature 009: Weather Forecast Atom Feed
"""
from behave import when, then
import xml.etree.ElementTree as ET


@when('I request the Atom feed for city "{city_name}"')
def step_request_atom_feed(context, city_name):
    """Request the Atom feed for a specific city."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = context.city_uuids[city_name]

    context.response = context.client.get(
        f'/feeds/{city_uuid}/feed.atom',
    )

    # Store raw content for XML parsing
    context.response_content = context.response.content.decode('utf-8')


@when('I request the Atom feed for non-existent city UUID "{city_uuid}"')
def step_request_atom_feed_nonexistent(context, city_uuid):
    """Request the Atom feed for a non-existent city UUID."""
    context.response = context.client.get(
        f'/feeds/{city_uuid}/feed.atom',
    )

    context.response_content = context.response.content.decode('utf-8')


@then('the response content type is "{content_type}"')
def step_response_content_type(context, content_type):
    """Check that the response has the expected content type."""
    actual_content_type = context.response.get('Content-Type', '')
    assert content_type in actual_content_type, \
        f"Expected content type '{content_type}', got '{actual_content_type}'"


@then('the Atom feed contains valid XML structure')
def step_atom_feed_valid_xml(context):
    """Check that the response is valid Atom XML."""
    try:
        root = ET.fromstring(context.response_content)
        context.atom_root = root
        # Verify it's a feed element
        assert root.tag.endswith('feed') or root.tag == 'feed', \
            f"Expected root element 'feed', got '{root.tag}'"
    except ET.ParseError as e:
        raise AssertionError(f"Invalid XML: {e}")


@then('the Atom feed contains forecast entries')
def step_atom_feed_contains_entries(context):
    """Check that the Atom feed contains entry elements."""
    root = getattr(context, 'atom_root', None)
    if root is None:
        root = ET.fromstring(context.response_content)
        context.atom_root = root

    # Find all entry elements (with or without namespace)
    entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
    if not entries:
        entries = root.findall('.//entry')

    context.atom_entries = entries
    assert len(entries) > 0, "Atom feed should contain at least one entry"


@then('each entry contains a title with weather summary')
def step_entry_contains_title(context):
    """Check that each entry has a title with weather summary."""
    entries = getattr(context, 'atom_entries', None)
    if entries is None:
        root = getattr(context, 'atom_root', None)
        if root is None:
            root = ET.fromstring(context.response_content)
        entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
        if not entries:
            entries = root.findall('.//entry')

    for entry in entries:
        title = entry.find('{http://www.w3.org/2005/Atom}title')
        if title is None:
            title = entry.find('title')
        assert title is not None, "Entry should have a title element"
        assert title.text is not None and len(title.text) > 0, \
            "Entry title should not be empty"


@then('each entry contains temperature information')
def step_entry_contains_temperature(context):
    """Check that each entry contains temperature information."""
    entries = getattr(context, 'atom_entries', None)
    if entries is None:
        root = getattr(context, 'atom_root', None)
        if root is None:
            root = ET.fromstring(context.response_content)
        entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
        if not entries:
            entries = root.findall('.//entry')

    for entry in entries:
        # Temperature could be in title, content, or summary
        title = entry.find('{http://www.w3.org/2005/Atom}title')
        if title is None:
            title = entry.find('title')
        content = entry.find('{http://www.w3.org/2005/Atom}content')
        if content is None:
            content = entry.find('content')
        summary = entry.find('{http://www.w3.org/2005/Atom}summary')
        if summary is None:
            summary = entry.find('summary')

        # Check if temperature appears in any of these
        has_temp = False
        for elem in [title, content, summary]:
            if elem is not None and elem.text:
                if 'C' in elem.text or 'temperature' in elem.text.lower():
                    has_temp = True
                    break

        assert has_temp, "Entry should contain temperature information"


@then('the Atom feed contains a feed title')
def step_atom_feed_has_title(context):
    """Check that the Atom feed has a title element."""
    root = getattr(context, 'atom_root', None)
    if root is None:
        root = ET.fromstring(context.response_content)
        context.atom_root = root

    title = root.find('{http://www.w3.org/2005/Atom}title')
    if title is None:
        title = root.find('title')

    assert title is not None, "Atom feed should have a title element"
    assert title.text is not None and len(title.text) > 0, \
        "Atom feed title should not be empty"


@then('the Atom feed contains an updated timestamp')
def step_atom_feed_has_updated(context):
    """Check that the Atom feed has an updated timestamp."""
    root = getattr(context, 'atom_root', None)
    if root is None:
        root = ET.fromstring(context.response_content)
        context.atom_root = root

    updated = root.find('{http://www.w3.org/2005/Atom}updated')
    if updated is None:
        updated = root.find('updated')

    assert updated is not None, "Atom feed should have an updated element"
    assert updated.text is not None and len(updated.text) > 0, \
        "Atom feed updated timestamp should not be empty"


@then('the Atom feed contains a feed id')
def step_atom_feed_has_id(context):
    """Check that the Atom feed has an id element."""
    root = getattr(context, 'atom_root', None)
    if root is None:
        root = ET.fromstring(context.response_content)
        context.atom_root = root

    feed_id = root.find('{http://www.w3.org/2005/Atom}id')
    if feed_id is None:
        feed_id = root.find('id')

    assert feed_id is not None, "Atom feed should have an id element"
    assert feed_id.text is not None and len(feed_id.text) > 0, \
        "Atom feed id should not be empty"


@then('each Atom feed entry has a unique id')
def step_atom_entries_have_unique_ids(context):
    """Check that each Atom feed entry has a unique id."""
    root = getattr(context, 'atom_root', None)
    if root is None:
        root = ET.fromstring(context.response_content)
        context.atom_root = root

    entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
    if not entries:
        entries = root.findall('.//entry')

    ids = set()
    for entry in entries:
        entry_id = entry.find('{http://www.w3.org/2005/Atom}id')
        if entry_id is None:
            entry_id = entry.find('id')

        assert entry_id is not None, "Each entry should have an id element"
        assert entry_id.text is not None and len(entry_id.text) > 0, \
            "Entry id should not be empty"

        assert entry_id.text not in ids, \
            f"Entry id '{entry_id.text}' is not unique"
        ids.add(entry_id.text)
