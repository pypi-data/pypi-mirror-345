from pykleene.nfa import NFA
class Grammar:
    nonTerminals: set[str] = set()
    terminals: set[str] = set()
    productions: dict[str, set[str]] = dict()
    startSymbol: str 

    def __init__(self, 
                 nonTerminals: set[str] = set(), 
                 terminals: set[str] = set(), 
                 productions: dict[str, set[str]] = dict(), 
                 startSymbol: str = None):
        self.nonTerminals = nonTerminals
        self.terminals = terminals
        self.productions = productions
        self.startSymbol = startSymbol

    def loadFromJSONDict(self, data: dict) -> None:
        try:
            newGrammar = Grammar()
            newGrammar.nonTerminals = set(data['nonTerminals'])
            newGrammar.terminals = set(data['terminals'])
            newGrammar.productions = dict()
            for lhs, productions in data['productions'].items():
                if lhs not in newGrammar.productions:
                    newGrammar.productions[lhs] = set()
                newGrammar.productions[lhs] = newGrammar.productions[lhs] | set(productions)
            newGrammar.startSymbol = data['startSymbol']
        except Exception as e:
            print(f"Illegal JSONDict: {e}")
        
        if newGrammar.isValid():
            self.nonTerminals = newGrammar.nonTerminals
            self.terminals = newGrammar.terminals
            self.productions = newGrammar.productions
            self.startSymbol = newGrammar.startSymbol  
        else:
            raise ValueError("Invalid grammar")

    def isValid(self) -> bool:
        for nonTerminal in self.nonTerminals:
            if len(nonTerminal) > 1:
                return False
        for terminal in self.terminals:
            if len(terminal) > 1:
                return False
        if len(self.terminals & self.nonTerminals) > 0:
            return False
        if self.startSymbol not in self.nonTerminals:
            return False 
        for lhs, productions in self.productions.items():
            if len(lhs) == 0:
                return False
            for char in lhs:
                if char not in self.nonTerminals and char not in self.terminals:
                    return False
            for rhs in productions:
                if len(rhs) == 0:
                    return False
                if rhs == 'ε':
                    continue
                for char in rhs:
                    if char not in self.terminals and char not in self.nonTerminals:
                        return False
        return True

    def isLeftLinear(self) -> bool:
        if not self.isValid():
            return False

        for lhs, productions in self.productions.items():
            if lhs not in self.nonTerminals:
                return False
            for rhs in productions:
                if len(rhs) == 0:
                    return False
                if rhs == 'ε':
                    continue
                if rhs[0] not in self.terminals and rhs[0] not in self.nonTerminals:
                    return False
                for char in rhs[1:]:
                    if char not in self.terminals:
                        return False
        return True

    def isRightLinear(self) -> bool:
        if not self.isValid():
            return False
        for lhs, productions in self.productions.items():
            if lhs not in self.nonTerminals:
                return False
            for rhs in productions:
                if len(rhs) == 0:
                    return False
                if rhs == 'ε':
                    continue
                if rhs[-1] not in self.terminals and rhs[-1] not in self.nonTerminals:
                    return False
                for char in rhs[:-1]:
                    if char not in self.terminals:
                        return False
        return True

    def isRegular(self) -> bool:
        if not self.isValid():
            return False 
        return self.isLeftLinear() or self.isRightLinear()

    def _getNewState(self) -> str:
        cnt = 0
        while f"q{cnt}" in self.nonTerminals:
            cnt += 1 
        return f"q{cnt}"

    def reverse(self) -> 'Grammar':
        from copy import deepcopy
        grammar = deepcopy(self)
        newProductions = dict()
        for lhs, productions in self.productions.items():
            newProductions[lhs] = set()
            for rhs in productions:
                newProductions[lhs].add(rhs[::-1])
        grammar.productions = newProductions
        return grammar

    def nfa(self) -> NFA:
        def rightLinearToNfa() -> NFA:
            nfa = NFA(
                states={self.startSymbol},
                alphabet=self.terminals,
                transitions=dict(),
                startStates={self.startSymbol},
                finalStates=set()
            )

            cnt = 0
            for lhs, productions in self.productions.items():
                for rhs in productions:
                    if rhs == 'ε':
                        nfa.finalStates.add(lhs)
                    elif rhs in self.terminals:
                        nextState = self._getNewState()
                        nfa.states.add(nextState)
                        nfa = nfa.addTransition(lhs, rhs, nextState)
                        nfa.finalStates.add(nextState)
                    elif rhs in self.nonTerminals:
                        nextState = rhs
                        nfa = nfa.addTransition(lhs, 'ε', nextState)
                    else:
                        currState = lhs
                        for i, char in enumerate(rhs[:-1]):
                            if i == len(rhs) - 2 and rhs[i + 1] in self.nonTerminals:
                                nextState = rhs[i + 1]
                                nfa.states.add(nextState)
                                nfa = nfa.addTransition(currState, char, nextState)
                                break
                            if i == len(rhs) - 1:
                                nextState = self._getNewState()
                                nfa.states.add(nextState)
                                nfa.addTransition(currState, char, nextState)
                                nfa = nfa.finalStates.add(nextState)
                            else:
                                nextState = self._getNewState() 
                                nfa.states.add(nextState)
                                nfa = nfa.addTransition(currState, char, nextState)
                                currState = nextState
            return nfa

        def leftLinearToNfa() -> NFA:
            reversedRightLinearGrammar = self.reverse()
            reversedGrammarNfa = reversedRightLinearGrammar.nfa()
            Nfa = reversedGrammarNfa.reverse()
            return Nfa

        if not self.isRegular():
            raise ValueError("Grammar is not regular")
        if self.isRightLinear():
            return rightLinearToNfa()
        if self.isLeftLinear():
            return leftLinearToNfa()     
        else:
            raise ValueError("Error in converting grammar to NFA")

    def toRightLinear(self) -> 'Grammar':
        if not self.isRegular():
            raise ValueError("Grammar is not regular")
        if self.isRightLinear():
            return self
        if self.isLeftLinear():
            nfa = self.nfa() 
            return nfa.grammar()
        else:
            raise ValueError("Error in converting grammar to right linear form")

    def toLeftLinear(self) -> 'Grammar':
        if not self.isRegular():
            raise ValueError("Grammar is not regular")
        if self.isLeftLinear():
            return self
        if self.isRightLinear():
            nfa = self.nfa()
            reversedNfa = nfa.reverse()
            reversedRightLinearGrammar = reversedNfa.grammar()
            leftLinearGrammar = reversedRightLinearGrammar.reverse()
            return leftLinearGrammar

    def isContextFree(self) -> bool:
        if not self.isValid():
            return False
        for lhs, productions in self.productions.items():
            if len(lhs) != 1 or lhs not in self.nonTerminals:
                return False
            for rhs in productions:
                if len(rhs) == 0:
                    return False
                if rhs == 'ε':
                    continue
                for char in rhs:
                    if char not in self.terminals and char not in self.nonTerminals:
                        return False
        return True

    def isContextSensitive(self) -> bool:
        if not self.isValid():
            return False

        lhsInEpsilonProduction = False
        for lhs, productions in self.productions.items():
            if len(lhs) > len(productions) or len(lhs) == 0:
                return False
            for char in lhs:
                if char not in self.nonTerminals and char not in self.terminals:
                    return False
            for rhs in productions:
                if len(rhs) == 0:
                    return False
                if rhs == 'ε':
                    if lhsInEpsilonProduction or lhs != self.startSymbol:
                        return False
                    lhsInEpsilonProduction = True
                for char in rhs:
                    if char not in self.nonTerminals and char not in self.terminals:
                        return False 

        if lhsInEpsilonProduction:
            for lhs, productions in self.productions.items():
                for rhs in productions:
                    if self.startSymbol in rhs:
                        return False

        return True

    def isUnrestricted(self) -> bool:
        if not self.isValid():
            return False
        for lhs, productions in self.productions.items():
            if len(lhs) == 0:
                return False
            for char in lhs:
                if char not in self.nonTerminals and char not in self.terminals:
                    return False
            for rhs in productions:
                if len(rhs) == 0:
                    return False
                if rhs == 'ε':
                    continue
                for char in rhs:
                    if char not in self.nonTerminals and char not in self.terminals:
                        return False
        return True

    def inCNF(self) -> bool:
        if not self.isContextFree():
            return False
        for _, productions in self.productions.items():
            for rhs in productions:
                if len(rhs) == 0:
                    return False
                if rhs == 'ε':
                    continue
                if len(rhs) == 1 and rhs in self.terminals:
                    continue
                if len(rhs) == 2 and rhs[0] in self.nonTerminals and rhs[1] in self.nonTerminals:
                    continue
                return False

        return True

    def inGNF(self) -> bool:
        if not self.isContextFree():
            return False
        for _, productions in self.productions.items():
            for rhs in productions:
                if len(rhs) == 0:
                    return False
                if rhs == 'ε':
                    continue
                if len(rhs) == 1 and rhs not in self.terminals:
                    return False
                if len(rhs) > 1:
                    if rhs[0] not in self.terminals:
                        return False
                    for char in rhs[1:]:
                        if char not in self.nonTerminals:
                            return False

        return True