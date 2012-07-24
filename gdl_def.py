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



GdlRule = namedtuple('Rule', 'head body')
GdlSentence = namedtuple('Sentence', 'head body')

def get_roles(kif_terms):
    roles = set()
    for t in kif_terms:
        try:
            if t[0]== 'role':
                roles.add(GdlRule(t[0], t[1]))
        except IndexError:
            pass
    return roles



def get_init_state(kif_terms):
    state = set()
    for t in kif_terms:
        try:
            if t[0]== 'init':
                state.add(build_from_gdl(t[1]))
        except IndexError:
            pass
    return state

Constant = namedtuple('Constant', 'atom')
Variable = namedtuple('Variable', 'variable')
Function = namedtuple('Function', 'head')
Proposition = namedtuple('Proposition', 'const')
Relation = namedtuple('Relation', 'name body')
import collections, types

def create_literal(symbol):
    print symbol
    if isinstance(symbol, collections.Iterable):
        pass


def create_sentence(symbol):
    if len(symbol) == 1:
        return create_proposition(symbol[0])
    else:
        return create_relation(symbol)

def create_relation(symbols):
    name = symbols[0]
    return Relation(name, map(create_term, symbols[1:]))

def create_proposition(symbol):
    return Proposition(create_constant(symbol))

def create_variable(symbol):
    return Variable(symbol)

def create_constant(symbol):
    return Constant(symbol)

def create_term(symbol):
    if isinstance(symbol, types.StringTypes):
        if symbol.startswith('?'):
            return create_variable(symbol)
        else:
            return create_constant(symbol)
    else:
        return create_function(symbol[:2])

def create_rule(list):
    return Rule(create_sentence(list[1]), map(create_literal,list[1:]))

class TestGDLLoad(unittest.TestCase):
    def setUp(self):
        filename = 'tictactoe.gdl'
        self.kif_terms = terms_from_kif(filename)

    def test_role_load(self):
        roles = get_roles(self.kif_terms)
        assert len(roles) == 2

    def Test_init_state(self):
        state = get_init_state(self.kif_terms)
        assert len(state) == 10

    def test_create_constant(self):
        const = create_constant( quoterm(r'a'))
        assert const.atom == 'a'

    def test_create_variable(self):
        var = create_variable( quoterm(r'?a'))
        assert var.variable == '?a'

    def test_create_term(self):
        term = create_term( quoterm(r'?a'))
        assert term.variable == '?a'
        term = create_term( quoterm(r'a'))
        assert term.atom == 'a'

    def test_create_relation(self):
        relation = create_relation( quoterm(r'(control black)'))
        assert relation.name == 'control'

    def test_create_proposition(self):
        proposition = create_proposition( quoterm( r'control'))
        assert proposition.const.atom == 'control'

    def test_create_sentence(self):
        sentence = create_sentence( quoterm( r'(control black)'))
        assert sentence.name == 'control'
        assert sentence.body[0].atom == 'black'



if __name__ == "__main__":
    unittest.main()
