from pathlib import Path
import unittest

from Grammar import Grammar, Rule
from Item import Item
from Generator import Generator, State, Core

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

    def test_closure_question_tag(self):
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

    def test_closure_kleene_tag(self):
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
        for core, states in State.state_map.items():
            states.core = None
            states._items = []
            states.edges = {}
            states.reductions = {}

        State.state_map = {}
        State.state_list = []

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

class TestGenerator(unittest.TestCase):

    def test_table_output(self):
        # BASIC
        grammar = TestGrammar.make_new_grammar("""E ::=	E + T
                                               |	T
                                               T ::= T * F
                                               |	F
                                               F ::=	( E )
                                               |	id
                                               """)

        start = Generator._get_augment_start()
        Grammar._rules[start.lhs] = [start.rhs] 
        State.make_graph(State(start))
        table = Generator.create_table()

        assert len(table) == 12
        assert {'E': 1, 'T': 2, 'F': 3, '(': 4, 'id': 5} in table
        assert {'+': 6, '$': Rule(lhs="S'", rhs=['E'])} in table
        assert {'*': 7, ')': Rule(lhs='E', rhs=['T']), '+': Rule(lhs='E', rhs=['T']), '$': Rule(lhs='E', rhs=['T'])} in table
        assert {'*': Rule(lhs='T', rhs=['F']), ')': Rule(lhs='T', rhs=['F']), '+': Rule(lhs='T', rhs=['F']), '$': Rule(lhs='T', rhs=['F'])} in table
        assert {'E': 8, 'T': 2, 'F': 3, '(': 4, 'id': 5} in table
        assert {'*': Rule(lhs='F', rhs=['id']), ')': Rule(lhs='F', rhs=['id']), '+': Rule(lhs='F', rhs=['id']), '$': Rule(lhs='F', rhs=['id'])} in table
        assert {'T': 9, 'F': 3, '(': 4, 'id': 5} in table
        assert {'F': 10, '(': 4, 'id': 5} in table
        assert {')': 11, '+': 6} in table
        assert {'*': 7, ')': Rule(lhs='E', rhs=['E', '+', 'T']), '+': Rule(lhs='E', rhs=['E', '+', 'T']), '$': Rule(lhs='E', rhs=['E', '+', 'T'])} in table
        assert {'*': Rule(lhs='T', rhs=['T', '*', 'F']), ')': Rule(lhs='T', rhs=['T', '*', 'F']), '+': Rule(lhs='T', rhs=['T', '*', 'F']), '$': Rule(lhs='T', rhs=['T', '*', 'F'])} in table
        assert {'*': Rule(lhs='F', rhs=['(', 'E', ')']), ')': Rule(lhs='F', rhs=['(', 'E', ')']), '+': Rule(lhs='F', rhs=['(', 'E', ')']), '$': Rule(lhs='F', rhs=['(', 'E', ')'])} in table

        TestState.reset_states()
        grammar = TestGrammar.make_new_grammar("""X ::=	{A}* {B}? {C}+""")
        start = Generator._get_augment_start()
        Grammar._rules[start.lhs] = [start.rhs] 
        State.make_graph(State(start))
        table = Generator.create_table()

        # TAGS
        assert len(table) == 10
        assert {'X': 1, '{A}*': 2, 'A': 3, 'C': Rule(lhs='{A}*', rhs=[]), 'B': Rule(lhs='{A}*', rhs=[])} in table
        assert {'$': Rule(lhs="S'", rhs=['X'])} in table
        assert {'{B}?': 4, 'B': 5, 'C': Rule(lhs='{B}?', rhs=[])} in table
        assert {'{A}*': 6, 'A': 3, 'C': Rule(lhs='{A}*', rhs=[]), 'B': Rule(lhs='{A}*', rhs=[])} in table
        assert {'{C}+': 7, 'C': 8} in table
        assert {'C': Rule(lhs='{B}?', rhs=['B'])} in table
        assert {'A': Rule(lhs='{A}*', rhs=['A', '{A}*']), 'C': Rule(lhs='{A}*', rhs=['A', '{A}*']), 'B': Rule(lhs='{A}*', rhs=['A', '{A}*'])} in table
        assert {'$': Rule(lhs='X', rhs=['{A}*', '{B}?', '{C}+'])} in table
        assert {'{C}+': 9, 'C': 8, '$': Rule(lhs='{C}+', rhs=['C'])} in table
        assert {'C': Rule(lhs='{C}+', rhs=['C', '{C}+']), '$': Rule(lhs='{C}+', rhs=['C', '{C}+'])} in table

G = TestGenerator()
G.test_table_output()

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