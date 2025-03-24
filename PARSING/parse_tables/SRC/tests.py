from pathlib import Path
import unittest

from Singleton import Singleton
from BNFError import BNFError
from Grammar import Grammar, Rule
from Item import Item
from Generator import Generator, State, Core
from unittest.mock import mock_open, patch

# Item
#   closure (remove tag, terminal)

# State
#   intial state is right
#   manages to connect states
#   avoids duplicates

class TestGrammar(unittest.TestCase):

    @classmethod
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
    
# class TestItem(unittest.TestCase):
    
    # def test_closure(self):

        # res = parse_item("x ::= X X").closure()
        # assert cmp_item(res[0], parse_item("X ::= . a X , a b"))
        # assert cmp_item(res[0], parse_item("X ::= . b , a b"))

        # Grammar._rules = {}
        # Grammar._rules["<declaration-specifier>"] = [
        #     ["<storage-class-specifier>"],
        #     ["<type-specifier>"],
        #     ["<type-qualifier>"]
        # ]
        # Grammar._rules["<declarator>"] = [
        #     ["{<pointer>}?", "<direct-declarator>"]
        # ]
        # item = Item(Rule("<parameter-declaration>", ["{<declaration-specifier>}*", "<declarator>"]))
        # for i in item.closure():
        #     print(i)

 
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

c = TestGrammar()
c.test_parsing_basic()
c.test_parsing_spaces()
c.test_parsing_tags()
c.test_find_first_basic()
c.test_find_first_tags()
c.test_remove_tags()

# class TestCore(unittest.TestCase):
#     def test_add(self):
#         pass
#     def test__init__(self):
#         pass

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

# def test_remove_tags(self):
#     # only tags
#     with pytest.raises(RuntimeError):
#         Grammar.remove_tags("*****")
#     with pytest.raises(RuntimeError):
#         Grammar.remove_tags("++*++")

#     # values <= 2
#     assert Grammar.remove_tags(" ") == " "
#     assert Grammar.remove_tags("") == ""
#     assert Grammar.remove_tags("*") == "*"
#     assert Grammar.remove_tags("+=") == "+="
#     assert Grammar.remove_tags("+=*") == "="
    
#     assert Grammar.remove_tags("<>") == "<>"
#     assert Grammar.remove_tags("<*>") == "<*>"
#     assert Grammar.remove_tags("<foo>") == "<foo>"
#     assert Grammar.remove_tags("<foo>*") == "<foo>"

#     assert Grammar.remove_tags("{<external-declaration>}*") == "<external-declaration>"
#     assert Grammar.remove_tags("{<expression>}?") == "<expression>"

#     assert Grammar.remove_tags("{<foo>*}") == "<foo>"
#     assert Grammar.remove_tags("{ <foo>* }") == " <foo>* "