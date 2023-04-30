from Logic import *
from collections import deque

####################################################
####               BELIEF-BASE                  ####
####################################################

class BeliefBase:
    def __init__(self):
        self.beliefs = set()

    def add_belief(self, belief):
        # Add belief to the belief base
        self.beliefs.add(Logic.logicFromString(belief))

    def remove_belief(self, belief):
        # Remove belief from the belief base
        self.beliefs.discard(Logic.logicFromString(belief))

    def revise_belief(self, new_belief, revision_method):
        # Revise the belief base using a specific revision method
        self.beliefs = revision_method(self.beliefs, new_belief)


class BeliefRevisionAgent:
    def __init__(self):
        self.belief_base = BeliefBase()

    def add_belief(self, belief):
        self.belief_base.add_belief(belief)

    def remove_belief(self, belief):
        self.belief_base.remove_belief(belief)

    def revise_belief(self, new_belief, revision_method):
        self.belief_base.revise_belief(new_belief, revision_method)


def simple_revision(belief_base, new_belief):
    # Revise the belief base using the simple revision method
    # Remove conflicting beliefs, then add the new belief
    if type(new_belief.expr) == Negation:
        belief_base.discard(LogicalSentence(new_belief.expr.expr))
    elif LogicalSentence(Negation(new_belief.expr)) in belief_base:
        belief_base.discard(LogicalSentence(Negation(new_belief.expr)))
    belief_base.add(new_belief)
    return belief_base


####################################################
####               CNF CONVERSION               ####
####################################################

def cnf(logical) -> LogicalSentence:
        match logical:
            case LogicalSentence():
                return  LogicalSentence(cnf(logical.expr))
            
            case Biimplication():
                cnf_left = cnf(logical.left)
                cnf_right = cnf(logical.right)
                return cnf(Conjunction(Implication(cnf_left, cnf_right), Implication(cnf_right, cnf_left)))
            
            case Implication():
                return cnf(Disjunction(cnf(Negation(logical.left)), cnf(logical.right)))
            
            case Conjunction():
                return Conjunction(cnf(logical.left), cnf(logical.right))
            
            case Disjunction():
                match logical.left, logical.right:
                    case Conjunction(), other:
                        return Conjunction(cnf(Disjunction(logical.left.left, logical.right)), cnf(Disjunction(logical.left.right, logical.right)))
                    case other, Conjunction():
                        return Conjunction(cnf(Disjunction(logical.left, logical.right.left)), cnf(Disjunction(logical.left, logical.right.right)))
                    case other1, other2:
                        return Disjunction(cnf(other1), cnf(other2))
                    
            case Negation():
                match logical.expr:
                    case Negation():
                        return cnf(logical.expr.expr)
                    case Conjunction():
                        return cnf(Disjunction(cnf(Negation(logical.expr.left)), cnf(Negation(logical.expr.right))))
                    case Disjunction():
                        return cnf(Conjunction(cnf(Negation(logical.expr.left)), cnf(Negation(logical.expr.right))))
                    case Bracket():
                        match logical.expr.expr:
                            case Negation():
                                return cnf(logical.expr.expr.expr)
                            case other:
                                return Negation(cnf(logical.expr.expr))
                    case other:
                        return Negation(cnf(other))
                    
            case Symbol():
                return logical
            
            case Bracket():
                return Bracket(cnf(logical.expr))
            
            case _:
                raise Exception(f"Case {type(logical)} not covered")

####################################################
####             GENERAL FUNCTIONS              ####
####################################################

def bb_conjunction(beliefs):
    
    if len(beliefs) == 1:
        return beliefs[0].expr

    return Conjunction(beliefs[0].expr, bb_conjunction(beliefs[1:]))

def get_clauses(sentence):
    return split_conjunction(cnf(sentence))

# Split conjunctions into separate clauses, so we can have a set of clauses that only contain disjunctions
# For example (A | B) & (C | D) becomes (A | B), (C | D) in our set of clauses since we don't care about conjunctions
def split_conjunction(logical, split_set = set()):
    match logical:
        case LogicalSentence():
            return split_conjunction(logical.expr, split_set)
        case Biimplication():
            return set()
        case Implication():
            return set()
        case Conjunction():
            left = split_conjunction(logical.left, split_set.copy())
            right = split_conjunction(logical.right, split_set.copy())
            
            if not left:
                if (logical.left.__class__ == Bracket):
                    split_set.add(LogicalSentence(logical.left.expr))
                else: 
                    split_set.add(LogicalSentence(logical.left))
            else:
                split_set = split_set.union(left)

            if not right:
                if (logical.right.__class__ == Bracket):
                    split_set.add(LogicalSentence(logical.right.expr))
                else: 
                    split_set.add(LogicalSentence(logical.right))
            else:
                split_set = split_set.union(right)

            return split_set
        case Disjunction():
            return set()
        case Negation():
            return split_set.union(split_conjunction(logical.expr, split_set))
        case Symbol():
            return set()
        case Bracket():
            return set()


####################################################
####                DPLL-ENTAILS                ####
####################################################
## NOT FULLY FINISHED

def clean(logical, model):
    match logical:
        case LogicalSentence() | Negation():
            return logical.__class__(clean(logical.expr, model))
        case Disjunction():
            if logical.left.eval(model):
                return clean(logical.right, model)
            elif logical.right.eval(model):
                return clean(logical.left, model)
            else:
                return Disjunction(clean(logical.left, model), clean(logical.right, model))
        case Conjunction():
            return Conjunction(clean(logical.left, model), clean(logical.right, model))
        case Symbol():
            return logical


def find_pure_symbol(symbols, clauses, model):

    if not symbols or not clauses:
        return None, None

    for symbol in symbols:

        symbol_sign = None
        pure = True

        
        for clause in clauses:

            # CLEAN CLAUSE USING MODEL

            signs = clause.get_sign(symbol)
            if Sign.POSITIVE in signs and Sign.NEGATIVE in signs:
                pure = False
                break
            elif Sign.POSITIVE in signs:
                if (symbol_sign == Sign.NEGATIVE):
                    pure = False
                    break
                symbol_sign = Sign.POSITIVE
            elif Sign.NEGATIVE in signs:
                if (symbol_sign == Sign.POSITIVE):
                    pure = False
                    break
                symbol_sign = Sign.NEGATIVE

        if pure:
            if symbol_sign == Sign.POSITIVE: 
                return symbol, True
            elif symbol_sign == Sign.NEGATIVE:
                return symbol, False
    
    return None, None
            

def find_unit_clause(clauses, model):
    for clause in clauses:
        clean_clause = clean(clause, model).expr
        symbols = clean_clause.get_symbols()
        if len(symbols) == 1:
            symbol, = symbols
            if clean_clause.__class__ == Symbol:
                return symbol, True
            elif clean_clause.__class__ == Negation:
                return symbol, False
            else:
                raise Exception("Unreachable")

    return None, None

def dpll_entails(belief_base, sentence):
    kb = LogicalSentence(Conjunction(bb_conjunction(list(belief_base)), Negation(sentence.expr)))
    return not dpll_satisfiable(kb)


def dpll_satisfiable(sentence):
    clauses = get_clauses(sentence)
    symbols = sentence.get_symbols()
    return dpll(clauses, symbols, {})

def dpll(clauses, symbols, model):

    if not clauses or not symbols:
        return True

    clauses_true = False
    for clause in clauses:

        value = model.get(clause)

        if value == None:
            continue

        if value:
            clauses_true = True
        else:
            return False
    if clauses_true:
        return True


    symbol, value = find_pure_symbol(symbols, clauses, model)
    if not symbol == None:
        model[symbol] = value
        symbols.remove(symbol)
        return dpll(clauses, symbols, model)
    
    symbol, value = find_unit_clause(clauses, model)
    if not symbol == None:
        model[symbol] = value
        symbols.remove(symbol)
        return dpll(clauses, symbols, model)
    
    if len(symbols) <= 1:
        symbol = list(symbols)[0]
        rest = set()
    else:
        symbol, *rest = symbols

    model_true = model.copy()
    model_true[symbol] = True
    model_false = model.copy()
    model_false[symbol] = False

    return dpll(clauses, set(rest), model_true) or dpll(clauses, set(rest), model_false)


####################################################
####               PL-FC-ENTAILS                ####
####################################################


# Excpects  sentence consisting of conjunctions of literals and only one positive
def get_literals_sign(sentence, negatives=set(), positives=set()):
    match sentence:

        case LogicalSentence():
            return get_literals_sign(sentence.expr, negatives, positives)

        case Disjunction():
            negatives_left, positives_left = get_literals_sign(sentence.left, negatives, positives)
            negatives_right, positives_right = get_literals_sign(sentence.right, negatives, positives)

            return negatives_left.union(negatives_right), positives_left.union(positives_right)

        case Negation():
            return {sentence.expr}, set()
        case Symbol():
            return set(), {sentence}
        case _:
            raise Exception("Sentence is not definite")

def construct_conjunction(symbols):
    if len(symbols) == 1:
        return symbols[0]
    
    return Conjunction(symbols[0], construct_conjunction(symbols[1:]))

def convert_definite_to_implication(sentence):
    negatives, positives = get_literals_sign(sentence)
    if len(positives) != 1:
        raise Exception("Sentence is not definite")
    
    positive_symbol, = positives

    if len(negatives) == 0:
        return LogicalSentence(Implication(LogicTrue(), positive_symbol))
    
    return LogicalSentence(Implication(construct_conjunction(list(negatives)), positive_symbol))

# Converts belief base of definite clauses to implications
def convert_dbb_to_implication(belief_base):
    return list(map(lambda e: convert_definite_to_implication(e), belief_base))

# Requires definite clauses to be written as implications
def pl_fc_entails(belief_base, symbol):
    count = {belief: len(belief.get_symbols()) for belief in belief_base}
    inferred = {s: False for belief in belief_base for s in belief.get_symbols()}
    q = deque()
    for belief in belief_base:
        if belief.expr.right.__class__ == Symbol:
            q.append(belief.expr.right)

    while q:
        p = q.pop()

        if p == symbol.expr:
            return True
        
        if inferred[p] == False:
            inferred[p] == True
            for clause in belief_base:
                if p in clause.expr.left:
                    count[clause] -= 1
                    if count[clause] == 0:
                        q.append(clause.expr.right)
    return False

# Demonstration of pl_fc_entails
def test_pl_fc_entails(agent):
    agent.add_belief("a")
    agent.add_belief("!b | c")
    symbol = Logic.logicFromString("c")
    agent.belief_base.beliefs = convert_dbb_to_implication(agent.belief_base.beliefs)
    print(pl_fc_entails(agent.belief_base.beliefs, symbol))


####################################################
####               PL-RESOLUTION                ####
####################################################
def pl_resolution(belief_base, sentence):
    clauses = list(get_clauses(LogicalSentence(Conjunction(bb_conjunction(list(belief_base)), Negation(sentence.expr)))))
    new = set()

    while True:
        for c1 in clauses:
            for c2 in clauses:
                if c1 == c2:
                    continue

            resolvents = pl_resolve(c1, c2)

            # Checking empty clause. Is this right?
            if ("" in resolvents):
                return True
            
            new = new.union(resolvents)

        if new.issubset(clauses):
            return False
        
        clauses = clauses.union(new)


def pl_resolve(clause1, clause2):
    pass

# Testing
def test_pl_resolution(agent):
    agent.add_belief("a")
    agent.add_belief("!b | c")
    sentence = Logic.logicFromString("c")
    print(pl_resolution(agent.belief_base.beliefs, sentence))

####################################################
####                 TESTING                    ####
####################################################

# Testing
agent = BeliefRevisionAgent()

#test_pl_fc_entails(agent)
test_pl_resolution(agent)