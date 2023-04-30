from enum import Enum, auto
from collections.abc import Mapping


class LogicalSentence:
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self) -> str: 
        return f"LogicalSentence({self.expr})"
    
    def __eq__(self, other) -> bool:
        return self.__repr__() == other.__repr__()
    
    def __hash__(self) -> int:
        return hash(("sentence", self.__repr__()))

    def prettyPrint(self) -> str:
        return f"{self.expr.prettyPrint()}"

    def eval(self, vals : Mapping[str, bool]) -> bool:
        return self.expr.eval(vals)

    def get_all_symbols(self):
        return self.expr.get_all_symbols()



class Biimplication:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def __repr__(self) -> str:
        return f"Biimplication({self.left}, {self.right})"
    
    def prettyPrint(self) -> str:
        return f"{self.left.prettyPrint()} <=> {self.right.prettyPrint()}"
    
    def eval(self, vals : Mapping[str, bool]) -> bool:
        return self.left.eval(vals) == self.right.eval(vals)

    def get_all_symbols(self):
        return self.left.get_all_symbols().union(self.right.get_all_symbols())


class Implication:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def __repr__(self) -> str:
        return f"Implication({self.left}, {self.right})"
    
    def prettyPrint(self) -> str:
        return f"{self.left.prettyPrint()} => {self.right.prettyPrint()}"

    def eval(self, vals : Mapping[str, bool]) -> bool:
        if (self.left.eval(vals) == False): return True
        else: return self.right.eval(vals)

    def get_all_symbols(self):
        return self.left.get_all_symbols().union(self.right.get_all_symbols())


class Conjunction:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def __repr__(self) -> str:
        return f"Conjunction({self.left}, {self.right})"
    
    def prettyPrint(self) -> str:
        return f"{self.left.prettyPrint()} & {self.right.prettyPrint()}"

    def eval(self, vals : Mapping[str, bool]) -> bool:
        return self.left.eval(vals) and self.right.eval(vals)

    def get_all_symbols(self):
        return self.left.get_all_symbols().union(self.right.get_all_symbols())
    

class Disjunction:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def __repr__(self) -> str:
        return f"Disjunction({self.left}, {self.right})"
    
    def prettyPrint(self) -> str:
        return f"{self.left.prettyPrint()} | {self.right.prettyPrint()}"
    
    def eval(self, vals : Mapping[str, bool]) -> bool:
        return self.left.eval(vals) or self.right.eval(vals)

    def get_all_symbols(self):
        return self.left.get_all_symbols().union(self.right.get_all_symbols())


class Negation:
    def __init__(self, expr):
        self.expr = expr
    
    def __repr__(self) -> str:
        return f"Not({self.expr})"
    
    def prettyPrint(self) -> str:
        return f"!{self.expr.prettyPrint()}"

    def eval(self, vals : Mapping[str, bool]) -> bool:
        return not self.expr.eval(vals)

    def get_all_symbols(self):
        return self.expr.get_all_symbols()


class Symbol:
    def __init__(self, symbol: str):
        self.symbol = symbol
    
    def __repr__(self) -> str:
        return f"Symbol({self.symbol})"
    
    def prettyPrint(self) -> str:
        return self.symbol

    def eval(self, vals : Mapping[str, bool]) -> bool:
        return vals[self.symbol]

    def get_all_symbols(self):
        return {self.symbol}


class Bracket:
    def __init__(self, expr):
        self.expr = expr
    
    def __repr__(self) -> str:
        return f"Bracket({self.expr})"
    
    def prettyPrint(self) -> str:
        return f"({self.expr.prettyPrint()})"

    def eval(self, vals : Mapping[str, bool]) -> bool:
        return self.expr.eval()

    def get_all_symbols(self):
        return self.expr.get_all_symbols()


class Operations(Enum):
    SYMBOL = auto(),
    BIIMPLICATION = auto(),
    IMPLICATION = auto(),
    CONJUNCTION = auto(),
    DISJUNCTION = auto(),
    NEGATION = auto(),
    OPEN_BRACKET = auto(),
    CLOSED_BRACKET = auto(),

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return str(self)


class Logic:
    @staticmethod
    def remove_left_space(sentence):
        while (sentence[0] == ' '):
            return Logic.remove_left_space(sentence[1:])
        return sentence 
    
    @staticmethod
    def lex(sentence, ops):
        while sentence != "":
            sentence = Logic.remove_left_space(sentence)

            if sentence[0].isalpha():

                symbol = ""
                while sentence != "" and sentence[0].isalnum():
                    symbol += sentence[0]
                    sentence = sentence[1:]

                ops.append((Operations.SYMBOL, symbol))
                continue

            elif sentence[0:3] == "<=>":
                sentence = sentence[3:]
                ops.append(Operations.BIIMPLICATION)
                continue

            elif sentence[0:2] == "=>":
                sentence = sentence[2:]
                ops.append(Operations.IMPLICATION)
                continue

            elif sentence[0] == "&":
                sentence = sentence[1:]
                ops.append(Operations.CONJUNCTION)
                continue

            elif sentence[0] == "|":
                sentence = sentence[1:]
                ops.append(Operations.DISJUNCTION)
                continue

            elif sentence[0] == "!":
                sentence = sentence[1:]
                ops.append(Operations.NEGATION)
                continue
            elif sentence[0] == "(":
                sentence = sentence[1:]
                ops.append(Operations.OPEN_BRACKET)
                continue
            elif (sentence[0] == ")"):
                sentence = sentence[1:]
                ops.append(Operations.CLOSED_BRACKET)
                continue
            else:
                print(f"ERROR: Could not parse sentence: {sentence}")
                exit(1)

        return ops

    @staticmethod
    def parse(lexed):
        # ORDER:
        # SYMBOL
        # BRACKETS
        # NEGATION
        # CONJUNCTION
        # DISJUNCTION
        # IMLICATION
        # BIIMPLICATION
        
        # BRACKETS (lex type)
        for idx, op in enumerate(lexed):
            if op == Operations.OPEN_BRACKET:
                bracket_counter = 0
                for idx2, op2 in enumerate(lexed[idx+1:]):
                    if op2 == Operations.OPEN_BRACKET:
                        bracket_counter += 1
                    elif op2 == Operations.CLOSED_BRACKET:
                        if bracket_counter == 0:
                            lexed = lexed[:idx] + [Bracket(Logic.parse(lexed[idx+1 : idx+idx2+1]))] + lexed[idx+idx2+2:]
                            return Logic.parse(lexed)
                        else:
                            bracket_counter -= 1
                
                raise Exception("There are too many open brackets")
            
        for idx, op in enumerate(lexed):
            if op == Operations.CLOSED_BRACKET:
                raise Exception("There are too many closed brackets")

        # BIIMPLICATION
        for idx, op in enumerate(lexed):
            if op == Operations.BIIMPLICATION:
                return Biimplication(Logic.parse(lexed[0:idx]), Logic.parse(lexed[idx+1:]))

        # IMPLICATION
        for idx, op in enumerate(lexed):
            if op == Operations.IMPLICATION:
                return Implication(Logic.parse(lexed[0:idx]), Logic.parse(lexed[idx+1:]))
        
        # DISJUNCTION
        for idx, op in enumerate(lexed):
            if op == Operations.DISJUNCTION:
                return Disjunction(Logic.parse(lexed[0:idx]), Logic.parse(lexed[idx+1:]))
        
        # CONJUNCTION
        for idx, op in enumerate(lexed):
            if op == Operations.CONJUNCTION:
                return Conjunction(Logic.parse(lexed[0:idx]), Logic.parse(lexed[idx+1:]))
        
        # NEGATION
        for idx, op in enumerate(lexed):
            if op == Operations.NEGATION:
                if (type(lexed[idx+1]) == tuple ):
                    return Negation(Logic.parse([lexed[idx+1]]))
                else:
                    return Negation(Logic.parse(lexed[idx+1:]))

        # SYMBOL
        for idx, op in enumerate(lexed):
            if type(op) == tuple:
                return Symbol(op[1])

        # BRACKETS (class type)
        for idx, op in enumerate(lexed):
            if type(op) == Bracket:
                return lexed[0]

        return lexed

    @staticmethod
    def logicFromString(sentence: str) -> LogicalSentence:
        return LogicalSentence(Logic.parse(Logic.lex(sentence, [])))





