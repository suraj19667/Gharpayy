"""Round-robin agent assignment logic."""
from agents.models import Agent, RoundRobinState


def assign_agent_round_robin():
    """Assign the next agent using round-robin logic."""
    agents = list(Agent.objects(is_active=True))
    if not agents:
        return None

    state = RoundRobinState.get_or_create()
    idx = state.current_index % len(agents)
    assigned = agents[idx]

    # Advance the index for next assignment
    state.current_index = (idx + 1)
    state.save()

    return assigned
