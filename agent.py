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
                        return cnf(Conjunction(cnf(Disjunction(logical.left.left, logical.right)), cnf(Disjunction(logical.left.right, logical.right))))
                    case other, Conjunction():
                        return cnf(Conjunction(cnf(Disjunction(logical.left, logical.right.left)), cnf(Disjunction(logical.left, logical.right.right))))
                    case other1, other2:
                        other1_cnf = cnf(other1)
                        other2_cnf = cnf(other2)

                        if (type(other1_cnf) == Conjunction or type(other2_cnf) == Conjunction):
                            return cnf(Disjunction(other1_cnf, other2_cnf))
                        return Disjunction(other1_cnf, other2_cnf)
                    
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
                    case Symbol():
                        return Negation(cnf(logical.expr))
                    case other:
                        return cnf(Negation(cnf(other)))
            case Symbol():
                return logical
            
            case Bracket():
                return Bracket(cnf(logical.expr))
            
            case _:
                raise Exception(f"Case {type(logical)} not covered")


####################################################
####               PL-FC-ENTAILS                ####
####################################################


# Excpects sentence consisting of conjunctions of literals and only one positive
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