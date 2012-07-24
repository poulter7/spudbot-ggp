from collections import namedtuple
from KIFSyntax import quoterm
import re

def solo_command(current, strip):
    return len(current) == 0 and len(strip) > 0 and strip.count('(') == strip.count(')')

def text_terms_from_kif(filename):
    terms = []
    with open(filename) as f:
        current = r''
        for line in f.readlines():
            strip = line.strip()
            if strip.startswith(';'):
                pass
            elif len(strip) == 0 and len(current) > 0: # end of multiline term
                terms.append(current)
                current = r''
            elif solo_command(current, strip): # single line term
                terms.append(strip)
            else:
                current += strip
    return terms

def terms_from_kif(filename):
    text_terms = text_terms_from_kif(filename)
    return map(quoterm, text_terms)

import unittest
from numpy.testing import assert_equal
class TestKIFParse(unittest.TestCase):
    def setUp(self):
        self.filename = 'tictactoe.gdl'

    def test_number_of_text_terms(self):
        kif_text_terms = text_terms_from_kif(self.filename)
        assert_equal(len(kif_text_terms), 38)

    def test_number_of_parse_tems(self):
        kif_terms = terms_from_kif(self.filename)
        assert_equal(len(kif_terms), 38)



if __name__ == "__main__":
    unittest.main()
