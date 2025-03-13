from pathlib import Path
import unittest

from Singleton import Singleton
from BNFError import BNFError
from Grammar import Grammar, Rule
from Item import Item
from Generator import Generator, State, Core
import pytest
from unittest.mock import mock_open, patch
import tempfile

# Grammar
#   parsing rules
#   start symbol

# Item
#  find_follow gives right look ahead
#  terminal , optional, repetitive, remove tag
#  closure 

# State
#   intial state is right
#   manages to connect states
#   avoids duplicates

class TestGrammar(unittest.TestCase):
    
    def test_remove_tags(self):
        # only tags
        with pytest.raises(RuntimeError):
            Grammar.remove_tags("*****")
        with pytest.raises(RuntimeError):
            Grammar.remove_tags("++*++")

        # values <= 2
        assert Grammar.remove_tags(" ") == " "
        assert Grammar.remove_tags("") == ""
        assert Grammar.remove_tags("*") == "*"
        assert Grammar.remove_tags("+=") == "+="
        assert Grammar.remove_tags("+=*") == "="
        
        assert Grammar.remove_tags("<>") == "<>"
        assert Grammar.remove_tags("<*>") == "<*>"
        assert Grammar.remove_tags("<foo>") == "<foo>"
        assert Grammar.remove_tags("<foo>*") == "<foo>"

        assert Grammar.remove_tags("{<external-declaration>}*") == "<external-declaration>"
        assert Grammar.remove_tags("{<expression>}?") == "<expression>"

        assert Grammar.remove_tags("{<foo>*}") == "<foo>"
        assert Grammar.remove_tags("{ <foo>* }") == " <foo>* "

    #TODO
    def test_start_symbol(self):
        mock_data = """ A ::= a a \
                           | b
                        
                        b ::= c
        """
        pass
    def test_find_first(self):
        pass
    def test_parse_grammar(self):
        pass

def cmp_item(item: Item, lhs: str, rhs: list[str], lookahead: set = set(), pos: int = 0) -> bool:
    return (
        item.lhs == lhs and
        item.rhs == rhs and
        item.lookahead == lookahead and
        item.pos == pos
    )

def parse_item(item: str) -> Item:

    lhs = item.split()[0]

    lookahead_start = str.find(',')
    if lookahead_start == -1:
        lookahead = set()
    else:
        lookahead = set(item[lookahead_start + 1 :].split())

    rhs_start = str.find("::=")

    rhs = item[rhs_start + 3 : lookahead_start].split()
    pos = rhs.index(".")
    if pos == -1:
        pos = 0

    item = item.replace('.', '')
    rhs = item[rhs_start + 3 : lookahead_start].split()

    return Item(Rule(lhs, rhs), lookahead, pos)
    
def config_Grammar(grammar: str, map = {}):
    with tempfile.NamedTemporaryFile(mode='w+', delete=True) as temp_file:
        temp_file.write(str)
        temp_file.seek(0)

class TestItem(unittest.TestCase):
    
    # paste the entire grammar as string and parse it with grammar 
    # paste items in 

    def test_closure(self):

        mock_file = mock_open(read_data=""
        "S ::= X X"
        "X ::= a X"
        "| b")
        grammer = Grammar(mock_file)

        res = parse_item("x ::= X X").closure()
        assert cmp_item(res[0], parse_item("X ::= . a X , a b"))
        assert cmp_item(res[0], parse_item("X ::= . b , a b"))

        Grammar._rules = {}
        Grammar._rules["<declaration-specifier>"] = [
            ["<storage-class-specifier>"],
            ["<type-specifier>"],
            ["<type-qualifier>"]
        ]
        Grammar._rules["<declarator>"] = [
            ["{<pointer>}?", "<direct-declarator>"]
        ]
        item = Item(Rule("<parameter-declaration>", ["{<declaration-specifier>}*", "<declarator>"]))
        for i in item.closure():
            print(i)

 
        # assert cmp_item(res[0], "{<declaration-specifier>}*", )


        # res = item.closure()
        # assert res[0].lhs == "X"
        # assert res[0].rhs == ["a", "X"]
        # assert res[0].pos == 0
        # assert res[0].lookahead == {'a', 'b'}
        # assert res[1].lhs == "X"
        # assert res[1].rhs == ["b"]
        # assert res[1].pos == 0
        # assert res[1].lookahead == {'a', 'b'}

class TestCore(unittest.TestCase):
    def test_add(self):
        pass
    def test__init__(self):
        pass

class TestState(unittest.TestCase):
    def test__init__(self):
        pass
    def test_is_reduction_ambiguous(self):
        pass
    def test_add_reduction(self):
        pass
    def test_merge_state(self):
        pass
    def test_connect_states(self):
        pass

c = TestItem()
c.test_closure()