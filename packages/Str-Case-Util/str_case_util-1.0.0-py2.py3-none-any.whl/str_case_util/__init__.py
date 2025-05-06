from collections import deque
from enum import Enum
from typing import Optional, Self


def capitalize(words: list[str]) -> list[str]:
    """
    Modifies a list of words by capitalizing the first character of each word.
    i.e. ["hello", "WORLD"] -> ["Hello", "World"]

    :param words: The list of words to modify
    :return: A new list of the modified words
    """
    return [w.capitalize() for w in words]


def camel(words: list[str]) -> list[str]:
    """
    Modifies a list of words by capitalizing the first character of all but the 1st word.
    i.e. ["Hello", "world"] -> ["hello", "World"]

    :param words: The list of words to modify
    :return: A new list of the modified words
    """
    return [words[0].lower()] + [w.capitalize() for w in words[1:]]


def sentence(words: list[str]) -> list[str]:
    """
    Modifies a list of words by capitalizing the first character of the 1st word.
    i.e. ["hElLo", "WoRlD"] -> ["Hello", "world"]

    :param words: The list of words to modify
    :return: A new list of the modified words
    """
    return [words[0].capitalize()] + [w.lower() for w in words[1:]]


def lower(words: list[str]) -> list[str]:
    """
    Modifies a list of words by converting each to lowercase.
    i.e. ["HELLO", "WORLD"] -> ["hello", "world"]

    :param words: The list of words to modify
    :return: A new list of the modified words
    """
    return [w.lower() for w in words]


def upper(words: list[str]) -> list[str]:
    """
    Modifies a list of words by converting each to uppercase.
    i.e. ["hello", "world"] -> ["HELLO", "WORLD"]

    :param words: The list of words to modify
    :return: A new list of the modified words
    """
    return [w.upper() for w in words]


def words_of(string: str) -> list[str]:
    """
    Splits a delimited string into a list of words.
    Supported delimiters are " ", "_", "-", and case (i.e. CaseDelimitedWords).
    Sequential uppercase letters are treated as a single word.
        i.e. "SUPERString" results in ["SUPER", "String"] rather than ["S", "U", "P", "E", "R", "String"]
    An empty string input will return an empty list.

    :param string: A string which may contain multiple delimited words
    :return: A list of words found
    """
    if " " in string:
        return string.split(" ")
    elif "_" in string:
        return string.split("_")
    elif "-" in string:
        return string.split("-")
    else:
        return split_by_case(string)


def split_by_case(string: str) -> list[str]:
    """
    Splits a case delimited string into a list of words.
        i.e. "splitByCase" -> ["split", "By", "Case"]
    Sequential uppercase letters are treated as a single word.
        i.e. "SUPERString" results in ["SUPER", "String"] rather than ["S", "U", "P", "E", "R", "String"]
    An empty string input will return an empty list.

    :param string: A string which may contain multiple delimited words
    :return: A list of words found
    """
    words = deque()
    if string:
        word = string[-1:]
        for char in reversed(string[:-1]):
            if (word[0].isupper() or word[0].isdigit()) and (char.islower() or not word.isupper()):
                words.appendleft(word)
                word = ""
            word = char + word
        words.appendleft(word)
    return list(words)


class Case(Enum):
    """
    Represents the variety of capitalization and delimiters that might be seen within programming.
    Cases are not mutually exclusive as some are known by multiple names.
    """
    PASCAL_CASE = capitalize, ""
    CAPITAL_CAMEL_CASE = PASCAL_CASE

    CAMEL_CASE = camel, ""

    FLAT_CASE = lower, ""
    MUMBLE_CASE = FLAT_CASE

    UPPER_FLAT_CASE = upper, ""

    TITLE_CASE = capitalize, " "

    SENTENCE_CASE = sentence, " "

    LOWER_CASE = lower, " "

    UPPER_CASE = upper, " "

    SNAKE_CASE = lower, "_"
    C_CASE = SNAKE_CASE

    SCREAMING_SNAKE_CASE = upper, "_"
    CONSTANT_CASE = SCREAMING_SNAKE_CASE
    MACRO_CASE = SCREAMING_SNAKE_CASE

    TRAIN_CASE = capitalize, "-"

    KEBAB_CASE = lower, "-"
    CATERPILLAR_CASE = KEBAB_CASE
    CSS_CASE = KEBAB_CASE
    LISP_CASE = KEBAB_CASE

    COBOL_CASE = upper, "-"

    def __init__(self, capitalization, delimiter):
        self.capitalization = capitalization
        self.delimiter = delimiter

    def format(self, string: str) -> str:
        """
        Formats a string using the capitalization and delimiter of this Case.
        The input string may be of any format though some formats may make it impossible to determine individual words.

        :param string: The string to format
        :return: A newly formatted string
        """
        return self.delimiter.join(self.capitalization(words_of(string)))

    def is_formatted(self, string: str) -> bool:
        """
        Determines if a string is formatted using the capitalization and delimiter of this Case.

        :param string: The string to check
        :return: True if the string is formatted, False otherwise
        """
        return self.format(string) == string

    @classmethod
    def detect_format(cls, string: str) -> Optional[Self]:
        """
        Detects the format of the capitalization and delimiter of a string in order to match to a Case.

        :param string: The string to check
        :return: The Case applicable to the string or None if a format cannot be determined
        """
        cases = set()
        for case in Case:
            if case.is_formatted(string):
                cases.add(case)
        if len(cases) == 1:
            return cases.pop()
        elif Case.FLAT_CASE in cases:
            return Case.FLAT_CASE
        elif Case.UPPER_FLAT_CASE in cases:
            return Case.UPPER_FLAT_CASE
        else:
            return None
