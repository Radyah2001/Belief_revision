import Logic
from Logic import *
# Package that comes with base python
from itertools import product, chain, combinations


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def maxichoice(selection_function, iterable):
    return max(iterable, key=selection_function)


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

    def clear_beliefs(self):
        self.beliefs.clear()

    def entails(self, logical_sentence: LogicalSentence) -> bool:
        symbols = set()
        for belief in self.beliefs:
            symbols = symbols.union(belief.get_all_symbols())
        symbols = symbols.union(logical_sentence.get_all_symbols())
        symbols = list(symbols)

        for values in product([True, False], repeat=len(symbols)):
            assignment = {symbols[i]: values[i] for i in range(len(symbols))}
            if all(belief.eval(assignment) for belief in self.beliefs):
                if not logical_sentence.eval(assignment):
                    return False
        return True

    def partial_meet_contraction(self, belief, selection_function):
        # Get the set of all belief base subsets that do not entail the given belief
        non_entailing_subsets = set(s for s in powerset(self.beliefs) if not BeliefBase.from_beliefs(s).entails(belief))

        # Apply the selection function to choose a maximal non-entailing subset
        maximal_subset = maxichoice(selection_function, non_entailing_subsets)

        # Replace the belief base with the maximal non-entailing subset
        self.beliefs = set(maximal_subset)

    @staticmethod
    def from_beliefs(beliefs):
        bb = BeliefBase()
        bb.beliefs = set(beliefs)
        return bb


class BeliefRevisionAgent:
    def __init__(self):
        self.belief_base = BeliefBase()

    def add_belief(self, belief):
        self.belief_base.add_belief(belief)

    def remove_belief(self, belief):
        self.belief_base.remove_belief(belief)

    def revise_belief(self, new_belief, revision_method):
        self.belief_base.revise_belief(new_belief, revision_method)

    def print_beliefs(self):
        print("Beliefs:")
        for belief in self.belief_base.beliefs:
            print(belief)

    def clear_beliefs(self):
        self.belief_base.clear_beliefs()

    def contract_belief(self, belief, selection_function):
        self.belief_base.partial_meet_contraction(belief, selection_function)


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
            return LogicalSentence(cnf(logical.expr))
        case Biimplication():
            cnf_left = cnf(logical.left)
            cnf_right = cnf(logical.right)
            return cnf(Conjunction(Implication(cnf_left, cnf_right), Implication(cnf_right, cnf_left)))
        case Implication():
            return cnf(Disjunction(cnf(Negation(logical.left)), cnf(logical.right)))
        case Conjunction():
            match logical.left, logical.right:
                case Disjunction(), other:
                    return Disjunction(cnf(Conjunction(logical.left.left, logical.right)),
                                       cnf(Conjunction(logical.left.right, logical.right)))
                case other, Disjunction():
                    return Disjunction(cnf(Conjunction(logical.left, logical.right.left)),
                                       cnf(Conjunction(logical.left, logical.right.right)))
                case other1, other2:
                    return Conjunction(cnf(other1), cnf(other2))
        case Disjunction():
            match logical.left, logical.right:
                case Conjunction(), other:
                    return Conjunction(cnf(Disjunction(logical.left.left, logical.right)),
                                       cnf(Disjunction(logical.left.right, logical.right)))
                case other, Conjunction():
                    return Conjunction(cnf(Disjunction(logical.left, logical.right.left)),
                                       cnf(Disjunction(logical.left, logical.right.right)))
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


def test_AGM_postulates(agent):
    # Closure
    initial_beliefs = agent.belief_base.beliefs.copy()
    new_belief = Logic.logicFromString("A => B")
    agent.revise_belief(new_belief, simple_revision)
    revised_beliefs = agent.belief_base.beliefs
    for b in initial_beliefs:
        assert b in revised_beliefs, f"Closure postulate failed. {b} not in revised beliefs."

    # Inclusion
    assert new_belief in revised_beliefs, "Inclusion postulate failed."

    # Success
    consistent_belief = Logic.logicFromString("D")
    agent.revise_belief(consistent_belief, simple_revision)
    revised_beliefs = agent.belief_base.beliefs
    assert consistent_belief in revised_beliefs, "Success postulate failed."

    # Preservation
    for b in initial_beliefs:
        assert b in revised_beliefs, f"Preservation postulate failed. {b} not in revised beliefs."

    # Consistency
    inconsistent_belief = Logic.logicFromString("!D")
    agent.revise_belief(inconsistent_belief, simple_revision)
    is_consistent = not (agent.belief_base.entails(Logic.logicFromString("D")) and
                         agent.belief_base.entails(Logic.logicFromString("!D")))
    assert is_consistent, "Consistency postulate failed."

    # Minimal change
    # Not applicable in the simple_revision method, as it does not consider minimal change in belief revision.


def simple_selection_function(belief_set):
    return len(belief_set)


# Testing the agent


agent = BeliefRevisionAgent()
agent.add_belief(Logic.logicFromString("A"))
agent.add_belief(Logic.logicFromString("B"))
agent.add_belief(Logic.logicFromString("C"))
# AGM postulates test
test_AGM_postulates(agent)
agent.clear_beliefs()

# Logical entailment test
agent.add_belief(Logic.logicFromString("A"))
agent.add_belief(Logic.logicFromString("A & B"))
agent.add_belief(Logic.logicFromString("A | B"))
agent.add_belief(Logic.logicFromString("C"))
agent.print_beliefs()

print(Logic.logicFromString("A & B").prettyPrint())
print(Logic.logicFromString("A | !B").prettyPrint())
entailed = agent.belief_base.entails(Logic.logicFromString("A & B & C"))
print(entailed)

entailed = agent.belief_base.entails(Logic.logicFromString("A & !B"))
print(entailed)

agent.contract_belief(Logic.logicFromString("A"), simple_selection_function)
agent.print_beliefs()
