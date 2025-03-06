from __future__ import annotations
from Grammar import Grammar
from Utils import Rule, InputError

class Item:

    @property
    def lhs(self):
        return self.rule.lhs

    @property
    def rhs(self):
        return self.rule.rhs

    @staticmethod
    def get_rule_with_pos(item: Item) -> str:
        expansion = " "
        for i in range(len(item.rhs)):
            if i == item.pos:
                expansion += " . "
            expansion += item.rhs[i] + " "
        if (item.pos >= len(item.rhs)):
            expansion += " . "

        return item.lhs + " ::= " + expansion

    def print_item(self) -> None:
        lookahead_list = ""
        for terminal in self.lookahead:
            lookahead_list += terminal + " "

        print(self.get_rule_with_pos(self) + "\n" + lookahead_list)

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

    # eq & hash used to easily search for duplicates when performing recursive closure and follow 
    def __eq__(self, other: Item) -> bool:
        if not isinstance(other, Item):
            raise RuntimeError(f"Trying to compare a class of Item with a {type(other)}")

        # look-ahead can be different in LALR(1)
        return (
            self.lhs == other.lhs and   
            self.rhs == other.rhs and 
            self.pos == other.pos 
        )   
    
    def __hash__(self):
        return hash(self.get_rule_with_pos(self)) 

    def __repr__(self) -> str:
        return Item.get_rule_with_pos(self)

    def _find_follow(self, _offset: int = 0) -> set[str]:
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
        pos = self.pos + _offset
        if pos >= len(self.rhs): 
            raise IndexError(InputError.MSG_item_OOB(self.lhs, self.rhs, pos))

        terminals = set()

        # if the current symbol can repeat, the repeat would follow the current
        curr_symbol = self.rhs[pos]
        if Grammar.is_repetitive(curr_symbol):
            terminals |= Grammar.find_first(curr_symbol)

        # follow of the end symbol = follow of LHS/reduction = item's look-ahead
        if pos == len(self.rhs) - 1:
            terminals |= self.lookahead
            return terminals

        next_symbol = self.rhs[pos + 1]
        if Grammar.is_optional(next_symbol):
            terminals |= self._find_follow(_offset + 1)

        terminals |= Grammar.find_first(next_symbol)
        return terminals

    def is_closure_invalid(self, seen: set):
        return (len(self.rhs) == 0 
            or self.pos >= len(self.rhs) 
            or Grammar.is_terminal(self.rhs[self.pos])
            or self.rhs[self.pos] in seen
        )

    def get_symbol_lhs(self) -> list[Item]:
        new_items = []
        symbol = self.rhs[self.pos]
        lookahead = self._find_follow()

        # symbol needs to be able to repeat any number of times
        if Grammar.is_repetitive(symbol):
            new_items.append(Item(Rule(symbol, [symbol, symbol]), lookahead))
        
        # empty rhs means we can create the LHS with no input needed
        if Grammar.is_optional(symbol):
            new_items.append(Item(Rule(symbol, []), lookahead))

        lhs = Grammar.remove_tags(symbol)
        for rhs in Grammar._rules[lhs]:
            new_items.append(Item(Rule(symbol, rhs), lookahead))

        return new_items

    #TODO optimize duplicate work with cache
    def closure(self, seen = None) -> list[Item]:
        """

            Performs closure on a given item set. Returns all rules where the current symbol is on the LHS
            and applies closure to any rules returned

            Parameters: no parameters

            Return: list[Item] Returns a list of item sets that are produced from closure
        """    
        if not seen: seen = set()

        if self.is_closure_invalid(seen): return []
        seen.add(self.rhs[self.pos])

        new_items = self.get_symbol_lhs()

        i = 0
        while i < len(new_items):
            item = new_items[i]
            if item not in seen: 
                new_items += item.closure(seen)
            i += 1

        return new_items