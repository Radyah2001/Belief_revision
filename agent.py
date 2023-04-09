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
    if new_belief.startswith("not "):
        belief_base.discard(new_belief[4:])
    elif "not " + new_belief in belief_base:
        belief_base.discard("not " + new_belief)
    belief_base.add(new_belief)
    return belief_base


# Testing the agent
agent = BeliefRevisionAgent()
agent.add_belief("A")
agent.add_belief("B")
agent.add_belief("C")
agent.revise_belief("not B", simple_revision)
print(agent.belief_base.beliefs)
