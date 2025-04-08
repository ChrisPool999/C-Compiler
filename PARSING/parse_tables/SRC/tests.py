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
    
class TestItem(unittest.TestCase):
    
    def test_item_eq_method(self):
        item = parse_item("X ::= . a X , a b")
        item2 = parse_item("X ::= . b , a b")
        assert item != item2 

        item = parse_item("X ::= . a X , a b")
        item2 = parse_item("X ::= . a X ,")
        assert item != item2

        item = parse_item("X ::= . a X , a b")
        item2 = parse_item("X ::= . a X , a b")
        assert item == item2  

    def test_closure_basic(self):
        grammar = TestGrammar.make_new_grammar("""X ::= a X 
                                               | b""")
        item = parse_item("x ::= . X X, $")
        closure_items = item.closure()

        assert closure_items[0] == parse_item("X ::= . a X , a b")
        assert closure_items[1] == parse_item("X ::= . b , a b")
        assert len(closure_items) == 2

    def test_closure_result_loop(self):
        grammar = TestGrammar.make_new_grammar("""A ::= B
                                               B ::= c""")
        item = parse_item("X ::= . A B, $")
        closure_items = item.closure()

        assert closure_items[0] == parse_item("A ::= B , c")
        assert closure_items[1] == parse_item("B ::= c , c")
        assert len(closure_items) == 2

    def test_closure_cycles(self):
        grammar = TestGrammar.make_new_grammar("""A ::= a
                                               a ::= A""")
        item = parse_item("A ::= . a , $")
        closure_items = item.closure()

        assert closure_items[0] == parse_item("a ::=   . A , $")
        assert closure_items[1] == parse_item("A ::=   . a , $")
        assert len(closure_items) == 2

        grammar = TestGrammar.make_new_grammar("""X ::= a X""")
        item = parse_item("X ::= a . X , $")
        closure_items = item.closure()

        assert closure_items[0] == parse_item("X ::= . a X , $")
        assert len(closure_items) == 1

    def test_closure_terminal(self):
        # basic
        grammar = TestGrammar.make_new_grammar("""A ::= B
                                               B ::= c""")
        item = parse_item("X ::= . a B, $")
        closure_items = item.closure()

        assert closure_items == []

        # test with tags
        grammar = TestGrammar.make_new_grammar("""A ::= B
                                               B ::= c""")
        item = parse_item("X ::= . {a}* B, $")
        closure_items = item.closure()

        assert closure_items[0] == parse_item("{a}* ::=   . , c")
        assert closure_items[1] == parse_item("{a}* ::=   . a {a}* , a c")
        assert len(closure_items) == 2

    def test_closure_option_tag(self):
        # basic
        grammar = TestGrammar.make_new_grammar("""B ::= b
                                               C ::= c""")
        item = parse_item("A ::= . {B}? C, $")
        closure_items = item.closure()

        assert closure_items[0] == parse_item( "{B}? ::=   . , c")
        assert closure_items[1] == parse_item("{B}? ::=   . B , c")
        assert closure_items[2] == parse_item("B ::=   . b , c")
        assert len(closure_items) == 3

        # final symbol option tag
        grammar = TestGrammar.make_new_grammar("""C ::= c""")
        item = parse_item("A ::= . {C}? , $")
        closure_items = item.closure()

        assert closure_items[0] == parse_item("{C}? ::=   . , $")
        assert closure_items[1] == parse_item("{C}? ::=   . C , $")
        assert closure_items[2] == parse_item("C ::=   . c , $")
        assert len(closure_items) == 3

        # double optional
        grammar = TestGrammar.make_new_grammar("""B ::= {D}? {C}?
                                               D ::= c b
                                               C ::= c""")
        item = parse_item("A ::= . B , $")
        closure_items = item.closure()

        assert closure_items[0] == parse_item("B ::=   . {D}? {C}? , $")
        assert closure_items[1] == parse_item("{D}? ::=   . , $ c")
        assert closure_items[2] == parse_item("{D}? ::=   . D , $ c")
        assert closure_items[3] == parse_item("D ::=   . c b , $ c")
        assert len(closure_items) == 4

    def test_closure_repetitive_tag(self):
        # basic
        grammar = TestGrammar.make_new_grammar("""B ::= b
                                               C ::= c""")
        item = parse_item("A ::= . {B}* C, $")
        closure_items = item.closure()

        assert closure_items[0] == parse_item("{B}* ::=   . , c")
        assert closure_items[1] == parse_item("{B}* ::=   . B {B}* , b c")
        assert closure_items[2] == parse_item("B ::=   . b , b c")
        assert len(closure_items) == 3

        # final symbol repetition tag
        grammar = TestGrammar.make_new_grammar("""C ::= c""")
        item = parse_item("A ::= . {C}* , $")
        closure_items = item.closure()

        assert closure_items[0] == parse_item("{C}* ::=   . , $")
        assert closure_items[1] == parse_item("{C}* ::=   . C {C}* , $ c")
        assert closure_items[2] == parse_item("C ::=   . c , $ c")
        assert len(closure_items) == 3

    def test_closure_plus_tag(self):
        # basic
        grammar = TestGrammar.make_new_grammar("""B ::= b
                                               C ::= c""")
        item = parse_item("A ::= . {B}+ C, $")
        closure_items = item.closure()

        assert closure_items[0] == parse_item("{B}+ ::=   . B , c")
        assert closure_items[1] == parse_item("{B}+ ::=   . B {B}+ , c b")
        assert closure_items[2] == parse_item("B ::=   . b , c b")
        assert len(closure_items) == 3

        # final symbol plus tag
        grammar = TestGrammar.make_new_grammar("""B ::= b""")
        item = parse_item("A ::= . {B}+ , $")
        closure_items = item.closure()

        assert closure_items[0] == parse_item("{B}+ ::=   . B , $")
        assert closure_items[1] == parse_item("{B}+ ::= . B {B}+ , $ b")
        assert closure_items[2] == parse_item("B ::=   . b , $ b")
        assert len(closure_items) == 3

class TestState(unittest.TestCase):

    @classmethod
    def reset_states(self):
        for c, other_states in State.state_map.items():
            other_states.core = None
            other_states._items = []
            other_states.edges = {}
            other_states.reductions = {}

        State.state_map = {}

    def test_init_state(self):
        grammar = TestGrammar.make_new_grammar("""S ::= X X
                                               X ::= a X
                                               | b""")
        core = parse_item("S' ::=   . S , $")
        state = State(core)

        assert state.core == Core(parse_item("S' ::=   . S , $"))
        assert state.items[0] == parse_item("S ::=   . X X , $")
        assert state.items[1] == parse_item("X ::=   . a X , b a")
        assert state.items[2] == parse_item("X ::=   . b , b a")
        assert len(state.items) == 3
        self.reset_states()

    def test_state_edges(self):
        grammar = TestGrammar.make_new_grammar("""S ::= X X
                                               X ::= a X
                                               | b""")
        core = parse_item("S' ::=   . S , $")
        state = State(core)
        State.make_graph(state)

        assert "S" in state.edges
        assert "X" in state.edges
        assert "a" in state.edges
        assert "b" in state.edges
        assert len(state.edges) == 4
        self.reset_states()

    def test_connecting_state(self):
        grammar = TestGrammar.make_new_grammar("""S ::= X X
                                               X ::= a X
                                               | b""")
        core = parse_item("S' ::=   . S , $")
        state = State(core)
        State.make_graph(state)

        edge = state.edges["X"]
        assert edge.core == Core(parse_item("S ::= X  . X , $"))
        assert parse_item("X ::=   . a X , $") in edge.items
        assert parse_item("X ::=   . b , $") in edge.items
        assert len(edge.items) == 2
        self.reset_states()

#     # check matching states are merged

#     # check grammar reduction rules are valid
#     # check any grammer ambiguity is found 
#     # check for cycles
#     # check for States with multiple cores


# PROBLEM #1   --   SOLVED, BUT MY SOLUTION IS VERY HACK
# EX: S ::= {A}? {B}* {C}* 

# - table/states
#   - recursive nature of repetion leads to repetitive item set being merged
#   - items that end a recursion item set, must ONLY be the following symbol

#   - EXAMPLE:
#   - X = B* C , B C <-- core
#   - B* = . , B C <-- lookahead of parent shouldnt have itself, merged with B = B B*
#   - B* = B B* , B C  <-- because it comes from here, but this lookahead is right

#   - INCLUDES + TAG TOO

# PROBLEM #2
# multiple cores wont merge any lookaheads inside the item set