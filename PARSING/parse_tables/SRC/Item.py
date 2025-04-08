from __future__ import annotations
from Grammar import Grammar, Tags, Rule
from BNFError import BNFError
import copy
import shutil

class Item:

    @property
    def lhs(self):
        return self.rule.lhs

    @property
    def rhs(self):
        return self.rule.rhs

    @classmethod
    def get_yellow_str_output(cls, string: str) -> str:
        return f"\033[93m{string}\033[0m"

    @classmethod 
    def get_pink_str_output(cls, string: str) -> str:
        return f"\033[95m{string}\033[0m"

    @classmethod
    def get_green_str_output(cls, string: str) -> str:
        return f"\033[92m{string}\033[0m"

    @staticmethod
    def get_rule_with_pos(item: Item) -> str:
        if not isinstance(item, Item):
            raise ValueError("arg should be of type Item")

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

    def responsive_item_print(self) -> str:
        item = self.get_rule_with_pos(self)

        max = shutil.get_terminal_size().columns
        curr = len(item)

        lookahead_list = ""
        for terminal in self.lookahead:
            if curr + len(terminal) >= max - 6: 
                lookahead_list += "\n" + (" " * 20)
                curr = 20

            lookahead_list += terminal + " "            
            curr += len(terminal) + 1

        return item + " , " + lookahead_list


    def __repr__(self) -> str:
        return self.responsive_item_print()

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

    def _get_tagless_lookahead(self) -> set[str]:
        item = copy.deepcopy(self)
        item.rhs[item.pos] = Grammar.remove_tags(item.rhs[item.pos])
        return item._find_follow()

    def _create_plus_tag_items(self) -> list[Item]:
        if self.pos >= len(self.rhs) or Grammar.get_tag(self.rhs[self.pos]) != Tags.PLUS_TAG:
            raise ValueError(f"{self}: The next symbol on this item is not a plus tag.\n")       

        tag_symbol = self.rhs[self.pos]
        tagless_symbol = Grammar.remove_tags(tag_symbol)
        symbol_terminals = Grammar.find_first(tagless_symbol)
        lookahead = self._get_tagless_lookahead()

        items = []
        items.append(Item(Rule(tag_symbol, [tagless_symbol]), self._find_follow() - Grammar.find_first(tagless_symbol)))
        items.append(Item(Rule(tag_symbol, [tagless_symbol, tag_symbol]), lookahead | symbol_terminals))

        return items

    def _create_question_tag_items(self) -> list[Item]:
        if self.pos >= len(self.rhs) or Grammar.get_tag(self.rhs[self.pos]) != Tags.QUESTION_TAG:
            raise ValueError(f"{self}: The next symbol on this item is not a question tag.\n")       

        tag_symbol = self.rhs[self.pos]
        tagless_symbol = Grammar.remove_tags(tag_symbol)
        lookahead = self._find_follow()

        items = []
        items.append(Item(Rule(tag_symbol, []), lookahead))
        items.append(Item(Rule(tag_symbol, [tagless_symbol]), lookahead))

        return items

    def _create_kleene_tag_items(self) -> list[Item]:
        if self.pos >= len(self.rhs) or Grammar.get_tag(self.rhs[self.pos]) != Tags.KLEENE_TAG:
            raise ValueError(f"{self}: The next symbol on this item is not a kleene tag.\n")       

        tag_symbol = self.rhs[self.pos]
        tagless_symbol = Grammar.remove_tags(tag_symbol)
        symbol_terminals = Grammar.find_first(tagless_symbol)
        tagless_lookahead = self._get_tagless_lookahead()

        items = []                                               # HACK
        items.append(Item(Rule(tag_symbol, []), tagless_lookahead - Grammar.find_first(tagless_symbol)))
        items.append(Item(Rule(tag_symbol, [tagless_symbol, tag_symbol]), self._find_follow() | symbol_terminals))

        return items

    def _create_tag_sets(self, symbol: str, seen) -> list[Item]:
        items = []
        tag = Grammar.get_tag(symbol)

        if not tag:
            return []

        if tag == Tags.PLUS_TAG: items += self._create_plus_tag_items()
        if tag == Tags.QUESTION_TAG: items += self._create_question_tag_items()
        if tag == Tags.KLEENE_TAG: items += self._create_kleene_tag_items()

        return items

    def _get_closure_items(self, seen) -> list[Item]:
        symbol = self.rhs[self.pos]
        items = self._create_tag_sets(symbol, seen)

        if not Grammar.get_tag(symbol) and symbol in Grammar._rules:
            lookahead = self._find_follow()
            for rhs in Grammar._rules[symbol]:
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

        i = 0
        while i < len(new_items):
            item = new_items[i]
            new_items += item.closure(seen)
            i += 1

        return new_items
    