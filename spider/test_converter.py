from unittest import TestCase

from spider.converter import Converter


class TestConverter(TestCase):
    def test_retrieve_prereqs(self):
        TestConverter.compare("Prerequisites: (COMS W1004) or (COMS W1007)", [["COMS W1004", "COMS W1007"]])
        TestConverter.compare("Prerequisites: Fluency in at least one programming language", [])
        TestConverter.compare(
            "Prerequisites: (COMS W3134) or (COMS W3137) or (COMS W3136) and fluency in Java);"
            " or the instructor's permission", [["COMS W3134", "COMS W3137", "COMS W3136"]])
        TestConverter.compare("Prerequisites: (COMS W3134 or W3136 or COMS W3137)"
                              " and (COMS W3261) and (CSEE W3827) or equivalent, or the instructor's permission.",
                              [["COMS W3134", "W3136", "COMS W3137"], "COMS W3261", "CSEE W3827"])
        TestConverter.compare("Prerequisites: Working knowledge of at least one programming language,"
                              " and some background in probability and statistics.",
                              [])
        TestConverter.compare("Prerequisites: (MATH UN1202) or the equivalent",
                              ["MATH UN1202"])

    @staticmethod
    def compare(prereq_str, expected):
        result = Converter.retrieve_prereqs(prereq_str)
        assert result == expected, result
