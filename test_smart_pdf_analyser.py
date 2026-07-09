from nlp import normalize_word, get_keywords
from project import format_reading_time, get_page_stats , get_document_stats

def test_normalize_word():
    """A simple word should be returned as-is."""
    assert normalize_word("hello") == "hello"

    """Punctuation should be stripped from words."""
    assert normalize_word("hello,") == "hello"
    assert normalize_word("world.") == "world"

    """Words ending in 's' (length > 3) should be stemmed."""
    assert normalize_word("forms") == "form"

    """Words shorter than 4 chars should NOT be stemmed."""
    assert normalize_word("is") == "is"

    """Numbers should be replaced with empty string."""
    assert normalize_word("123") == ""

    """Words with non-alphabetic characters should be filtered."""
    assert normalize_word("hello!") == "hello"
    assert normalize_word("$100") == ""


def test_get_keywords():
    """Result should be a list."""
    result = get_keywords("hello world hello")
    assert isinstance(result, list)

    """Each item should be a (word, count) tuple."""
    result = get_keywords("hello world hello")
    assert all(isinstance(item, tuple) for item in result)
    assert all(len(item) == 2 for item in result)

    """Stop words should not appear in keywords."""
    result = get_keywords("the and is are was were")
    # All input words are stop words, so result should be empty
    assert result == []

    """Numbers should not appear in keywords."""
    result = get_keywords("hello 123 world 456")
    words = [word for word, count in result]
    assert "123" not in words
    assert "456" not in words



def test_format_reading_time():
    """Reading time under 1 minute should be shown in seconds."""
    assert format_reading_time(0.5) == "30 sec"
    assert format_reading_time(0.1) == "6 sec"

    """Reading time of exactly 1 minute."""
    assert format_reading_time(1.0) == "1.0 min"

    """Reading time between 1 and 60 minutes shows minutes."""
    assert format_reading_time(30) == "30.0 min"

    """Reading time over 60 minutes shows hours."""
    assert format_reading_time(75) == "1h 15m"

    """Zero reading time should show 0 sec."""
    assert format_reading_time(0) == "0 sec"

    """Exactly 60 minutes is 1h 0m."""
    assert format_reading_time(60) == "1h 0m"



def test_get_page_stats():
    """Result should be a dictionary."""
    result = get_page_stats("Hello world.")
    assert isinstance(result, dict)

    """Word count should be correct."""
    result = get_page_stats("Hello world this is a test")
    assert result['words'] == 6

    """Sentence count should match sentence-ending punctuation."""
    result = get_page_stats("Hello. World! How are you?")
    assert result['sentences'] == 3

    """Character count includes everything (including spaces)."""
    result = get_page_stats("Hello world")
    assert result['characters'] == 11

    """Empty text should return zeros."""
    result = get_page_stats("")
    assert result['words'] == 0
    assert result['sentences'] == 0
    assert result['characters'] == 0

    """A single word should count as 1 word, 0 sentences."""
    result = get_page_stats("Hello")
    assert result['words'] == 1
    assert result['sentences'] == 0
    assert result['characters'] == 5

def test_get_document_stats():
    """Result should be a dict."""
    result = get_document_stats([{'pg_no': 1, 'text': 'This is ths first page'},{'pg_no': 2, 'text': 'This is the second page'}])
    print(result)
    assert isinstance(result, dict)

    '''Total stat must be a dictionary while perpage stat must be a list(dict)'''
    assert isinstance(result['total'], dict)

    assert isinstance(result['per_page'], list)
    assert [isinstance(x,dict) for x in result['per_page']]
    