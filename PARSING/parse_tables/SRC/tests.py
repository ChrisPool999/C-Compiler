from pathlib import Path
import unittest

from Singleton import Singleton
from BNFError import BNFError
from Grammar import Grammar, Rule
from Item import Item
from Generator import Generator, State, Core
from unittest.mock import mock_open, patch

# State
#   intial state is right
#   manages to connect states
#   avoids duplicates

class TestGrammar(unittest.TestCase):

    @classmethod
    # helper for testing
    def make_new_grammar(cls, bnf: str) -> None:
        Grammar.START_SYMBOL = ""
        Grammar._rules = {}
        grammar = Grammar()

        grammar._parse_from_string(bnf.splitlines())
        return grammar

    def test_parsing_basic(self) -> None:
        grammar = self.make_new_grammar("""S ::= X X
            X ::= a X
            | b""")

        assert grammar.START_SYMBOL == "S"
        assert grammar._rules == {
            "S" : [['X', 'X']],
            "X" : [['a', 'X'], ['b']]
        }

    def test_parsing_spaces(self) -> None:
        grammar = self.make_new_grammar("""X ::= A b

            A ::= a X

            | b""")

        assert grammar.START_SYMBOL == "X"
        assert grammar._rules == {
            "X" : [['A', 'b']],
            "A" : [['a', 'X'], ['b']]
        }

    def test_parsing_tags(self) -> None:
        grammar = self.make_new_grammar("""G ::= B* {b}

            B ::= c+ G?

            | {f}*""")

        assert grammar.START_SYMBOL == "G"
        assert grammar._rules == {
            "G" : [['B*', '{b}']],
            "B" : [['c+', 'G?'], ['{f}*']]
        }

    def test_find_first_basic(self) -> None: 
        grammar = self.make_new_grammar("""X ::= A b c
        | d
        | e f""")

        assert grammar.find_first("X") == {"A", "d", "e"}

    def test_find_first_tags(self) -> None: 
        grammar = self.make_new_grammar("""X ::= {A}* {b}? c
        | d
        | {e}+ f""")

        assert grammar.find_first("X") == {'c', 'd', 'A', 'b', 'e'}

    def test_remove_tags(self) -> None: 
        grammar = self.make_new_grammar("""X ::= {A}* {b}? c
        | d
        | {e}+ f""")

        # find first will remove tags, to find the proper LHS name
        assert grammar.find_first("{X}*") == {'c', 'd', 'A', 'b', 'e'}   
        assert grammar.find_first("{X}*") == {'c', 'd', 'A', 'b', 'e'}   
        assert grammar.find_first("{X}+") == {'c', 'd', 'A', 'b', 'e'}   
        assert grammar.find_first("{X}+") == {'c', 'd', 'A', 'b', 'e'}   

# helper for testing item
def parse_item(item: str) -> Item:
    lhs = item.split()[0]

    rhs_start = item.find("::=")
    if rhs_start == -1:
        raise ValueError("Item missing '::='")
    rhs_start += 3

    lookahead_start = item.find(',')
    if lookahead_start == -1:
        rhs = item[rhs_start :].split()
        lookahead = set()
    else:
        rhs = item[rhs_start : lookahead_start].split()
        lookahead = set(item[lookahead_start + 1 :].split())

    pos = 0
    for i in range(len(rhs)):
        if rhs[i] == ".":
            pos = i

    if "." in rhs:
        rhs.remove(".")

    return Item(Rule(lhs, rhs), lookahead, pos)
    
# helper for testing item
def cmp_item(item: Item, item2: Item) -> bool:
    return (
        item.lhs == item2.lhs and
        item.rhs == item2.rhs and
        item.lookahead == item2.lookahead and
        item.pos == item2.pos
    )

# helper for testing item
def cmp_item_list(items: list[Item], values: list[str]) -> bool:
    if len(items) != len(values):
        raise ValueError("cmp_item_list is comparing item lists of two different sizes")

    for i in range(len(items)):
        if not cmp_item(items[i], parse_item(values[i])):
            return False

    return True   

class TestItem(unittest.TestCase):
    
    def test_closure_basic(self):
        grammar = TestGrammar.make_new_grammar("""X ::= a X 
                                               | b""")
        item = parse_item("x ::= . X X, $")
        closure_items = item.closure()

        assert cmp_item_list(closure_items, [
            "X ::= . a X , a b", 
            "X ::= . b , a b"])

    def test_closure_result_loop(self):
        grammar = TestGrammar.make_new_grammar("""A ::= B
                                               B ::= c""")
        item = parse_item("X ::= . A B, $")
        closure_items = item.closure()

        assert cmp_item_list(closure_items, [
            "A ::= B , c", 
            "B ::= c , c"])

    def test_closure_option_tag(self):
        grammar = TestGrammar.make_new_grammar("""B ::= b
                                               C ::= c""")
        item = parse_item("A ::= . {B}? C, $")
        closure_items = item.closure()

        assert cmp_item_list(closure_items, [
            "{B}? ::=   . , c ", 
            "{B}? ::=   . b , c",
            "C ::= c, $"])

    def test_closure_repetitive_tag(self):
        grammar = TestGrammar.make_new_grammar("""B ::= b
                                               C ::= c""")
        item = parse_item("A ::= . {B}* C, $")
        closure_items = item.closure()

        assert cmp_item_list(closure_items, [
            "{B}* ::=   . {B}* {B}* , b c",
            "{B}* ::=   . , b c",
            "{B}* ::=   . b , b c",
            "C ::=   . c , $"])

    def test_closure_plus_tag(self):
        grammar = TestGrammar.make_new_grammar("""B ::= b
                                               C ::= c""")
        item = parse_item("A ::= . {B}+ C, $")
        closure_items = item.closure()

        assert cmp_item_list(closure_items, [
            "{B}+ ::=   . {B}+ {B}* , c b",
            "{B}+ ::=   . b , c b"])

    def test_closure_final_symbol(self):
        grammar = TestGrammar.make_new_grammar("""B ::= b
                                               C ::= c""")
        item = parse_item("A ::= . {B}? C, $")
        closure_items = item.closure()

        assert cmp_item_list(closure_items, [
            "{B}? ::=   . , c ", 
            "{B}? ::=   . b , c",
            "C ::= c, $"])
        
        grammar = TestGrammar.make_new_grammar("""C ::= c""")
        item = parse_item("A ::= . {C}? , $")
        closure_items = item.closure()

        assert cmp_item_list(closure_items, [
            "{C}? ::=   . , $",
            "{C}? ::=   . c , $"]) 

        grammar = TestGrammar.make_new_grammar("""C ::= c""")
        item = parse_item("A ::= . {C}* , $")
        closure_items = item.closure()

        assert cmp_item_list(closure_items, [
            "{C}* ::=   . {C}* {C}* , $ c", 
            "{C}* ::=   . , $ c",
            "{C}* ::=   . c , $ c"])

        grammar = TestGrammar.make_new_grammar("""B ::= {D}? {c}?
                                               D ::= c b""")
        item = parse_item("A ::= . B , $")
        closure_items = item.closure()

        assert cmp_item_list(closure_items, [
            "B ::=   . {D}? {c}? , $",
            "{D}? ::=   . , $ c",
            "{D}? ::=   . c b , $ c",
            "{c}? ::=   . , $"])

        grammar = TestGrammar.make_new_grammar("""B ::= {D}? {C}?
                                               D ::= c b
                                               C ::= c""")
        item = parse_item("A ::= . B , $")
        closure_items = item.closure()

        assert cmp_item_list(closure_items, [
            "B ::=   . {D}? {C}? , $",
            "{D}? ::=   . , $ c",
            "{D}? ::=   . c b , $ c", 
            "{C}? ::=   . , $",
            "{C}? ::=   . c , $"]) 

        grammar = TestGrammar.make_new_grammar("""B ::= {b}*
                                               | a
                                               C ::= c""")
        item = parse_item("A ::= . B C, $")
        closure_items = item.closure()

        assert cmp_item_list(closure_items, [
            "B ::=   . {b}* , c",
            "B ::=   . a , c",
            "{b}* ::=   . {b}* {b}* , c",
            "{b}* ::=   . , c"])
        
#TODO ISSUES NEEDING FIXING
"""
- make sure if you have matching sets, you combine their lookahead, eg x = *b b
    unsure about this one, wouldnt they be different items? check...
"""




# closure = put all rules where symbol is on LHS
# if symbol is optional, need to do next symbol too
# also do closure, for all item sets generated

# LOOKAHEAD (find follow()):
# if symbol is last, pass current lookahead
# find next terminal that will occur after the symbol

# class TestState(unittest.TestCase):
#     def test__init__(self):
#         pass
#     def test_is_reduction_ambiguous(self):
#         pass
#     def test_add_reduction(self):
#         pass
#     def test_merge_state(self):
#         pass
#     def test_connect_states(self):
#         pass