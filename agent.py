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

# Testing the agent




agent = BeliefRevisionAgent()
agent.add_belief(Logic.logicFromString("A"))
agent.add_belief(Logic.logicFromString("B"))
agent.add_belief(Logic.logicFromString("C"))
print(agent.belief_base.beliefs)
agent.revise_belief(Logic.logicFromString("!A"), simple_revision)
print(agent.belief_base.beliefs)
