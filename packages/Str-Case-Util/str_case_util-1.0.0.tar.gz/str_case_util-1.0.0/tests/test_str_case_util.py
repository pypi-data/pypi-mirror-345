from typing import Callable

import pytest

from str_case_util import Case, capitalize, camel, sentence, lower, upper, words_of, split_by_case


@pytest.mark.parametrize("function, expected", [
    (capitalize, ["One", "Two", "Three", "Four", "Five"]),
    (camel, ["one", "Two", "Three", "Four", "Five"]),
    (sentence, ["One", "two", "three", "four", "five"]),
    (lower, ["one", "two", "three", "four", "five"]),
    (upper, ["ONE", "TWO", "THREE", "FOUR", "FIVE"])
])
def test_capitalization(function: Callable, expected:  list[str]):
    words = ["ONE", "Two", "tHrEe", "fOUR", "five"]
    assert function(words) == expected


@pytest.mark.parametrize("text, expected", [
    ("PascalCaseText", ["Pascal", "Case", "Text"]),
    ("camelCaseText", ["camel", "Case", "Text"]),
    ("indeterminatemumblingtext", ["indeterminatemumblingtext"]),
    ("INCOHERENTSHOUTINGTEXT", ["INCOHERENTSHOUTINGTEXT"]),
    ("Book Or Movie Title", ["Book", "Or", "Movie", "Title"]),
    ("A standard sentence of text", ["A", "standard", "sentence", "of", "text"]),
    ("fully lower case text", ["fully", "lower", "case", "text"]),
    ("COMPLETELY UPPER CASE TEXT", ["COMPLETELY", "UPPER", "CASE", "TEXT"]),
    ("snake_case_text", ["snake", "case", "text"]),
    ("SCREAMING_SNAKE_CASE_TEXT", ["SCREAMING", "SNAKE", "CASE", "TEXT"]),
    ("Engine-Dining-Coach-Sleeper-Caboose", ["Engine", "Dining", "Coach", "Sleeper", "Caboose"]),
    ("meat-veggie-meat-veggie-meat", ["meat", "veggie", "meat", "veggie", "meat"]),
    ("COBOL-CASE-TEXT", ["COBOL", "CASE", "TEXT"])
])
def test_words_of(text: str, expected:  list[str]):
    assert words_of(text) == expected


@pytest.mark.parametrize("text, expected", [
    ("OneTwoThree", ["One", "Two", "Three"]),
    ("oneTwoThree", ["one", "Two", "Three"]),
    ("OneTWOThree", ["One", "TWO", "Three"]),
    ("ONETwoTHREE", ["ONE", "Two", "THREE"]),
    ("ONETWOTHREE", ["ONETWOTHREE"]),
    ("onetwothree", ["onetwothree"]),
    ("one2Thr3e", ["one", "2", "Thr", "3e"]),
    ("one-three", ["one-three"]),
    ("", [])
])
def test_split_by_case(text: str, expected:  list[str]):
    assert split_by_case(text) == expected


test_scenarios = [
    ("LoremIpsumDolorSitAmet", [Case.PASCAL_CASE, Case.CAPITAL_CAMEL_CASE]),
    ("loremIpsumDolorSitAmet", [Case.CAMEL_CASE]),
    ("loremipsumdolorsitamet", [Case.FLAT_CASE, Case.MUMBLE_CASE]),
    ("LOREMIPSUMDOLORSITAMET", [Case.UPPER_FLAT_CASE]),
    ("Lorem Ipsum Dolor Sit Amet", [Case.TITLE_CASE]),
    ("Lorem ipsum dolor sit amet", [Case.SENTENCE_CASE]),
    ("lorem ipsum dolor sit amet", [Case.LOWER_CASE]),
    ("LOREM IPSUM DOLOR SIT AMET", [Case.UPPER_CASE]),
    ("lorem_ipsum_dolor_sit_amet", [Case.SNAKE_CASE, Case.C_CASE]),
    ("LOREM_IPSUM_DOLOR_SIT_AMET", [Case.SCREAMING_SNAKE_CASE, Case.CONSTANT_CASE, Case.MACRO_CASE]),
    ("Lorem-Ipsum-Dolor-Sit-Amet", [Case.TRAIN_CASE]),
    ("lorem-ipsum-dolor-sit-amet", [Case.KEBAB_CASE, Case.CATERPILLAR_CASE, Case.CSS_CASE, Case.LISP_CASE]),
    ("LOREM-IPSUM-DOLOR-SIT-AMET", [Case.COBOL_CASE])
]


@pytest.mark.parametrize("expected, cases", test_scenarios)
def test_format(expected: str, cases: list[Case]):
    text = "Lorem ipsum dolor sit amet"
    for case in cases:
        assert case.format(text) == expected


@pytest.mark.parametrize("text, cases", test_scenarios)
def test_is_formatted(text: str, cases: list[Case]):
    for case in cases:
        assert case.is_formatted(text)


@pytest.mark.parametrize("text, cases", test_scenarios)
def test_determine_format(text: str, cases: list[Case]):
    assert Case.detect_format(text) in cases


def test_determine_format_none():
    assert Case.detect_format("MIX formatted-STRING") is None
