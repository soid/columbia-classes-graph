from unittest import TestCase

from converter import Converter
from helpers import sort_semesters, get_semester_by_filename


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
        TestConverter.compare("Prerequisites: (COMS W1004) or (COMS W1005) or (COMS W1007) or (ENGI E1006)",
                              [["COMS W1004", "COMS W1005", "COMS W1007", "ENGI E1006"]])

    def test_data_dir(self):
        assert len(Converter.get_data_files()) > 0
        get_semester_by_filename("data-2019-1.json") == "Spring 2019"

    def test_sort_semesters(self):
        semesters = ["Summer 2020", "Fall 2019", "Spring 2020", "Spring 2019", ]
        semesters = sort_semesters(semesters)
        assert semesters == ['Spring 2019', 'Fall 2019', 'Spring 2020', 'Summer 2020']

    @staticmethod
    def compare(prereq_str, expected):
        result = Converter.retrieve_prereqs(prereq_str)
        assert result == expected, result
