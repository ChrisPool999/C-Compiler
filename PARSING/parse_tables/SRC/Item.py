from __future__ import annotations
from Grammar import Grammar, Rule
from BNFError import BNFError
import copy

class Item:

    @property
    def lhs(self):
        return self.rule.lhs

    @property
    def rhs(self):
        return self.rule.rhs

    @staticmethod
    def get_rule_with_pos(item: Item) -> str:
        # if not isinstance(item, Item):
            # raise ValueError("arg should be of type Item")

        expansion = " "
        for i in range(len(item.rhs)):
            if i == item.pos:
                expansion += " . "
            expansion += item.rhs[i] + " "
        if (item.pos == len(item.rhs)):
            expansion += " . "

        if item.pos > len(item.rhs):
            raise RuntimeError("item position out of bounds")

        return item.lhs + " ::= " + expansion

    # dot position refers to the progress made in completing a grammer rule
    def __init__(self, rule: Rule, lookahead: set[str] = set(), pos: int = 0):
        if not isinstance(rule, Rule):
            raise TypeError(f"rule must be a Rule type, it's a {type(rule)} rule -> {rule}")

        if not isinstance(rule.rhs, list):
            raise TypeError(f"RHS must be a list, it's a {type(rule.rhs)} RHS -> {rule.rhs}")
        
        if not isinstance(lookahead, set):
            raise TypeError(f"lookahead must be a set, it's a {type(lookahead)} lookahead -> {lookahead}")        

        self.rule = rule
        self.lookahead = lookahead 
        self.pos = pos

    def __eq__(self, item: Item) -> bool:
        return (
        self.lhs == item.lhs and
        self.rhs == item.rhs and
        self.lookahead == item.lookahead and
        self.pos == item.pos
        )

    def __hash__(self) -> int:
        return hash(self.get_rule_with_pos(self)) 

    def hash_rule(self, lhs: str, rhs: list[str]) -> int:
        string = lhs + " ::= "
        for symbol in rhs:
            string += symbol + " "

        return hash(string)

    def __repr__(self) -> str:
        lookahead_list = ""
        for terminal in self.lookahead:
            lookahead_list += terminal + " "

        return (self.get_rule_with_pos(self) + ", " + lookahead_list)

    def _find_follow(self, offset: int = 0) -> set[str]:
        """ 
            Finds the follow() of a symbol\n
            The follow() is the set of terminals that can appear after a symbol within a rule\n
            Includes any cases where the symbol may be optional, repetitive, or the last symbol in a rule\n

            Parameters:\n
            item (Item)\n
            offset (int) (Only intended for internal use) Offset shifts the progress position of rule forward. \n

            Returns:
            set[str]: returns a set of terminals symbols that could possibly follow a symbol in a rule
        """        
        pos = self.pos + offset
        if pos >= len(self.rhs): 
            return set()

        terminals = set()

        # if the current symbol can repeat, the next symbol could be a repetition
        curr_symbol = self.rhs[self.pos]
        if Grammar.is_repetitive(curr_symbol):
            terminals |= Grammar.find_first(curr_symbol)

        # follow of the end symbol = follow of LHS/reduction = item's look-ahead
        if pos == len(self.rhs) - 1:
            terminals |= self.lookahead
            return terminals

        next_symbol = self.rhs[pos + 1]
        if Grammar.is_optional(next_symbol):
            terminals |= self._find_follow(offset + 1)

        terminals |= Grammar.find_first(next_symbol)
        return terminals

    def is_closure_invalid(self, seen: set):
        return (len(self.rhs) == 0 
            or self.pos >= len(self.rhs) 
            or (Grammar.is_terminal(self.rhs[self.pos]) and not Grammar.is_optional(self.rhs[self.pos]) and not Grammar.is_repetitive(self.rhs[self.pos]))
        )

    def _create_tag_sets(self, symbol: str) -> list[Item]:
        new_items = []

        # symbol needs to be able to repeat any number of times
        if Grammar.is_repetitive(symbol):
            repetition_symbol = "{" + Grammar.remove_tags(symbol) + "}*"
            lookahead = self._find_follow()
            item = Item(Rule(symbol, [symbol, repetition_symbol]), lookahead)
            new_items.append(item)
        
        # empty rhs means we can create the LHS with no input needed
        if Grammar.is_optional(symbol):
            new_item = copy.deepcopy(self)
            new_item.rhs[new_item.pos] = Grammar.remove_tags(new_item.rhs[new_item.pos])
            lookahead = new_item._find_follow()
            
            new_items.append(Item(Rule(symbol, []), lookahead))

        return new_items

    def _get_closure_items(self, seen) -> list[Item]:
        symbol = self.rhs[self.pos]
        items = self._create_tag_sets(symbol)

        lhs = Grammar.remove_tags(symbol)
        if lhs in Grammar._rules:
            lookahead = self._find_follow()
            for rhs in Grammar._rules[lhs]:
                items.append(Item(Rule(symbol, rhs), lookahead))

        new = []
        for item in items:
            if self.hash_rule(item.lhs, item.rhs) not in seen:
                new.append(item)
                seen[self.hash_rule(item.lhs, item.rhs)] = item.lookahead
            else:
                seen[self.hash_rule(item.lhs, item.rhs)] |= item.lookahead

        return new

    #TODO optimize duplicate work with cache
    def closure(self, seen = None) -> list[Item]:
        """
            Performs closure on a given item set. Returns all rules where the current symbol is on the LHS
            and applies closure to any rules returned

            Parameters: no parameters

            Return: list[Item] Returns a list of item sets that are produced from closure
        """    
        if not seen: seen = {}

        if self.is_closure_invalid(seen): 
            return []

        new_items = self._get_closure_items(seen)

        if self.pos + 1 < len(self.rhs) and Grammar.is_optional(self.rhs[self.pos]):
            new_items += Item(Rule(self.lhs, self.rhs), self.lookahead, self.pos + 1).closure(seen)

        i = 0
        while i < len(new_items):
            item = new_items[i]
            new_items += item.closure(seen)
            i += 1

        return new_items
    