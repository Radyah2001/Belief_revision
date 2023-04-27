from Logic import *

class BeliefBase:
    def __init__(self):
        self.beliefs = set()

    def add_belief(self, belief):
        # Add belief to the belief base
        self.beliefs.add(belief)

    def remove_belief(self, belief):
        # Remove belief from the belief base
        self.beliefs.discard(belief)

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
                match logical.left, logical.right:
                    case Disjunction(), other:
                        return Disjunction(cnf(Conjunction(logical.left.left, logical.right)), cnf(Conjunction(logical.left.right, logical.right)))
                    case other, Disjunction():
                        return Disjunction(cnf(Conjunction(logical.left, logical.right.left)), cnf(Conjunction(logical.left, logical.right.right)))
                    case other1, other2:
                        return Conjunction(cnf(other1), cnf(other2))
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
                return logical.expr
            case _:
                raise Exception(f"Case {type(logical)} not covered")
            
def clean(logical, literal):
    match logical:
        case LogicalSentence():
            return LogicalSentence(clean(logical.expr))
        case Disjunction():
            if logical.left.eval({literal.symbol: True}):
                return clean(logical.right)
            elif logical.right.eval({literal.symbol:True}):
                return clean(logical.left)
            else:
                return Disjunction(clean(logical.left), clean(logical.right))

# Split conjunctions into separate clauses, so we can have a set of clauses that only contain disjunctions
# For example (A | B) & (C | D) becomes (A | B), (C | D) in our set of clauses since we don't care about conjunctions
def split_conjunction(logical):
    ## not sure how to implement this
    pass
           
def unit_propagation(clauses, unit_clause):
    new_clauses = set()
    for clause in clauses:
        # Skip the unit clause
        if clause == unit_clause:
            continue
        # If the unit clause is in the clause, remove that clause
        if unit_clause.expr in clause.expr:
            continue
        # If the negation of the unit clause is in the clause, remove the negation
        if type(unit_clause.expr) == Negation and unit_clause.expr.expr in clause.expr:
            new_clause = clean(clause, unit_clause.expr.expr)
            new_clauses.add(new_clause)
        if unit_clause.expr in clause.expr:
            new_clause = clean(clause, unit_clause.expr)
            new_clauses.add(new_clause)
        # Otherwise, keep the clause
        else:
            new_clauses.add(clause)
    return new_clauses

# Helper function to convert a belief base and a query into a set of clauses with no conjunctions
def resolution_clauses(belief_base, phi):
    clauses = set()
    for belief in belief_base:
        clause = cnf(belief)
        split_conjunctions = split_conjunction(clause)
        if split_conjunctions:
            for split in split_conjunctions:
                clauses.add(split)
        else:
            clauses.add(clause)
    # Add the negation of the query to check for contradiction
    phi.expr = Negation(phi.expr)
    clauses.add(cnf(phi))
    return clauses

def pure_literal_

# Resolution algorithm
def resolution(belief_base, phi):
    # Turn the belief base and the query into a set of clauses
    clauses = resolution_clauses(belief_base, phi)
    
    # Unit propagation
    # Keep doing unit propagation until there are no more unit clauses
    contains_literal = True
    while contains_literal:
        contains_literal = False
        for clause in clauses:
            if clause.is_literal():
                contains_literal = True
                clauses = unit_propagation(clauses, clause)
                break # Restart the loop to avoid concurrent modification of the set
    # If the set of clauses is empty after unit propagation, then the belief base entails the query
    if not clauses:
        return True
    
    
    
            
            




# Testing the agent




agent = BeliefRevisionAgent()
agent.add_belief(Logic.logicFromString("r <=> (p | s)"))

print(resolution(agent.belief_base.beliefs, Logic.logicFromString("!p")))
