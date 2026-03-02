"""Step definitions for Atom feed feature."""

from behave import then
from bs4 import BeautifulSoup


@then('the response Content-Type is "{content_type}"')
def step_response_content_type(context, content_type):
    """Verify the response Content-Type header."""
    assert content_type in context.response_content_type, \
        f"Expected Content-Type '{content_type}', got '{context.response_content_type}'"


@then('the feed contains {count:d} entries')
def step_feed_contains_entries(context, count):
    """Verify the Atom feed contains the expected number of entries."""
    soup = BeautifulSoup(context.response_body, 'xml')
    entries = soup.find_all('entry')
    assert len(entries) == count, \
        f"Expected {count} entries, found {len(entries)}"


@then('each entry has a title, updated date, and content')
def step_entry_has_required_fields(context):
    """Verify each entry has required fields."""
    soup = BeautifulSoup(context.response_body, 'xml')
    entries = soup.find_all('entry')

    for entry in entries:
        assert entry.find('title'), "Entry missing title"
        assert entry.find('updated'), "Entry missing updated date"
        assert entry.find('summary') or entry.find('content'), "Entry missing content"


@then('the first entry contains forecast date in the title')
def step_first_entry_contains_date(context):
    """Verify the first entry title contains a forecast date."""
    soup = BeautifulSoup(context.response_body, 'xml')
    entries = soup.find_all('entry')

    assert len(entries) > 0, "No entries found"
    first_entry = entries[0]
    title = first_entry.find('title').text

    # Check if title contains a date pattern (YYYY-MM-DD)
    import re
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    assert re.search(date_pattern, title), \
        f"Title '{title}' does not contain a date in YYYY-MM-DD format"


@then('the first entry content includes temperature')
def step_first_entry_contains_temperature(context):
    """Verify the first entry content includes temperature information."""
    soup = BeautifulSoup(context.response_body, 'xml')
    entries = soup.find_all('entry')

    assert len(entries) > 0, "No entries found"
    first_entry = entries[0]
    content = first_entry.find('summary')
    if not content:
        content = first_entry.find('content')

    assert content, "No content found in entry"
    content_text = content.text.lower()
    assert 'temperature' in content_text or '°c' in content_text or '°f' in content_text, \
        f"Content does not include temperature: {content_text}"


@then('the first entry content includes conditions')
def step_first_entry_contains_conditions(context):
    """Verify the first entry content includes weather conditions."""
    soup = BeautifulSoup(context.response_body, 'xml')
    entries = soup.find_all('entry')

    assert len(entries) > 0, "No entries found"
    first_entry = entries[0]
    content = first_entry.find('summary')
    if not content:
        content = first_entry.find('content')

    assert content, "No content found in entry"
    content_text = content.text.lower()
    assert 'conditions' in content_text, \
        f"Content does not include conditions: {content_text}"


@then('the feed has a title containing "{text}"')
def step_feed_has_title(context, text):
    """Verify the feed has a title containing the specified text."""
    soup = BeautifulSoup(context.response_body, 'xml')
    feed_title = soup.find('title')

    assert feed_title, "Feed has no title element"
    assert text in feed_title.text, \
        f"Feed title '{feed_title.text}' does not contain '{text}'"


@then('the feed has a link to itself')
def step_feed_has_link(context):
    """Verify the feed has a link element."""
    soup = BeautifulSoup(context.response_body, 'xml')
    feed_link = soup.find('link')

    assert feed_link, "Feed has no link element"
    # Check if link has href attribute or is self-closing with href
    assert feed_link.get('href') or feed_link.get('rel'), \
        "Feed link is missing href or rel attribute"


@then('the feed has an updated timestamp')
def step_feed_has_updated(context):
    """Verify the feed has an updated timestamp."""
    soup = BeautifulSoup(context.response_body, 'xml')
    feed_updated = soup.find('updated')

    assert feed_updated, "Feed has no updated element"
    assert feed_updated.text, "Feed updated element is empty"
