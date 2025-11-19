import asyncio
import random
from enum import Enum
from typing import Dict, Optional

from mango import Agent, AgentAddress, create_tcp_container, activate

# Use an Enum for colors for clarity and type safety
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

    def __repr__(self):
        return self.name

# The set of all available colors
ALL_COLORS = set(Color)

class ConstraintAgent(Agent):
    """
    An agent that tries to choose a color different from its neighbors.
    """
    def __init__(self):
        super().__init__()
        self.color: Optional[Color] = None
        self.neighbors: Dict[str, AgentAddress] = {}
        self.neighbor_colors: Dict[str, Color] = {}
        self.stable_event = asyncio.Event()

    def on_ready(self):
        """Called when the agent is initialized. It broadcasts its initial color."""
        print(f"Agent {self.aid} starting with color {self.color}.")
        asyncio.create_task(self.share_color())

    def handle_message(self, content: Dict, meta: Dict):
        """Handles color update messages from other agents."""
        sender_aid = meta['sender_id']
        
        new_color = content['color']
        
        if self.neighbor_colors.get(sender_aid) != new_color:
            self.neighbor_colors[sender_aid] = new_color
            print(f"Agent {self.aid} received update: {sender_aid} is now {new_color}.")
            asyncio.create_task(self.re_evaluate_state())

    async def share_color(self):
        """Sends its current color to all its neighbors."""
        message = {'color': self.color}
        for neighbor_addr in self.neighbors.values():
            await self.send_message(content=message, receiver_addr=neighbor_addr)

    async def re_evaluate_state(self):
        """The core logic: check for conflicts and resolve them if necessary."""
        # Only evaluate after hearing from all neighbors.
        if len(self.neighbor_colors) < len(self.neighbors):
            return

        has_conflict = False
        for neighbor_aid, neighbor_color in self.neighbor_colors.items():
            if self.color == neighbor_color:
                # Tie-breaking rule: agent with the lexicographically larger AID changes.
                if self.aid > neighbor_aid:
                    has_conflict = True
                    print(f"Agent {self.aid} detected conflict with {neighbor_aid} (both {self.color}). {self.aid} will change.")
                    await self.change_color()
                    return

        if not has_conflict:
            print(f"Agent {self.aid} is STABLE with color {self.color}.")
            self.stable_event.set()

    async def change_color(self):
        """Chooses a new valid color and broadcasts the change."""
        current_neighbor_colors = set(self.neighbor_colors.values())
        available_colors = list(ALL_COLORS - current_neighbor_colors)

        if not available_colors:
            print(f"CRITICAL: Agent {self.aid} has no valid colors to choose from!")
            return

        new_color = random.choice(available_colors)
        print(f"Agent {self.aid} is CHANGING from {self.color} to {new_color}.")
        self.color = new_color
        
        self.stable_event.clear()
        
        await self.share_color()


async def main():
    """Sets up the container, agents, topology, and runs the simulation."""
    container = create_tcp_container(addr=('127.0.0.1', 5555))

    agents = [ConstraintAgent() for _ in range(3)]
    a0, a1, a2 = [container.register(agent=a) for a in agents]

    # Initialize with a random INVALID combination (guaranteed conflict)
    initial_colors = random.sample(list(Color), 2)
    color_assignments = [initial_colors[0], initial_colors[0], initial_colors[1]]
    random.shuffle(color_assignments)
    a0.color, a1.color, a2.color = color_assignments

    print("--- Initial State ---")
    print(f"{a0.aid}: {a0.color}, {a1.aid}: {a1.color}, {a2.aid}: {a2.color}")
    print("-----------------------")

    # Define the topology: a fully connected triangle
    a0.neighbors = {a1.aid: a1.addr, a2.aid: a2.addr}
    a1.neighbors = {a0.aid: a0.addr, a2.aid: a2.addr}
    a2.neighbors = {a0.aid: a0.addr, a1.aid: a1.addr}
    
    async with activate(container):
        await asyncio.gather(
            a0.stable_event.wait(),
            a1.stable_event.wait(),
            a2.stable_event.wait(),
        )

    print("\n--- Final State ---")
    print(f"Solution found: {a0.aid}: {a0.color}, {a1.aid}: {a1.color}, {a2.aid}: {a2.color}")
    print("-------------------")


if __name__ == "__main__":
    asyncio.run(main())