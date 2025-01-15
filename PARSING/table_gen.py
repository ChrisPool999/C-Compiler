class Grammer:
    def __init__(self, filename):
        self.productionRules = {}
        self._parse_grammer(filename)
        self.first = {}
        self.found = {}

    def _parse_grammer(self, filename):
        with open(filename, 'r') as file:
            expansions = []
            symbols = ""

            # fix this, its shit and doesnt even work for the start symbol
            # it never gets added on line 25
            old_symbol = ""
            for line in file:        
                symbols = line.split()

                if (len(symbols) == 0):
                    continue

                if symbols[1] == "::=":

                    if len(expansions):
                        self.rules()[old_symbol] = expansions
                        expansions = []
                        old_symbol = symbols[0]

                    expansions.append(symbols[2 : len(symbols)])

                elif (symbols[0] == '|'):
                    expansions.append(symbols[1 : len(symbols)])
            
            # self.production_rules[symbols[0]] = expansions

    def getRid(self, list):
        return list[-2] == '}'

    def find_first(self, LHS):
        if (LHS in self.found):
            return
        self.found[LHS] = 123

        # obviously this is extremely hacky, and was just brute forced
        # for my amusement 
        if (LHS[0] == '{'):
            LHS = LHS[1:len(LHS)]
        if (len(LHS) >= 2 and LHS[-2] == '}'):
            LHS = LHS[:-2]

        if not LHS in self.rules():
            print(LHS)
            return
        
        for rule in self.rules()[LHS]:
            self.find_first(rule[0])

    def rules(self):
        return self.productionRules
  

# NOTE! ALOT TO FIX, WAS JUST FUCKING AROUND TRYING TO GET IT TO WORK

def main():
    grammer = Grammer("PARSING/BNF.txt")
    grammer.find_first("<direct-declarator>")
    print("\n")
    # grammer.find_first("<declarator>")        

if __name__ == "__main__":
    main()


# if word1 = non-terminal & word2 = "::=" THEN RULE
# if word1 = '|' then its an additional RHS
# empty line required after each definition ends

# production rules should be a map of arrays



# braces                     {}
# parenthesis                ()
# arrays                     []
# klen star                  *
# or                         |
# one or more                +
# one or none                ?
# non braces enclosing eg   void

# <parameter-list> , ...    -> can optionally append a comma seperated list of parameter-list

# If a punctuation is next to a symbol it has optionality 
# If a punctuation is seperated by spaces, its a part of the grammer