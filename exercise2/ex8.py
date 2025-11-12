import asyncio
import networkx as nx
import mango

class SimpleAgent(mango.Agent):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def on_ready(self):
        # Auto-send greeting to neighbors when ready
        for neighbor in self.neighbors():
            self.schedule_instant_message("Hello!", neighbor)
            print(f"{self.name} sent greeting to neighbor")

    def handle_message(self, content, meta):
        print(f"{self.name} received: {content}")

async def main():
    container = mango.create_tcp_container(('127.0.0.1', 5555))

    # Create ring topology with NetworkX
    G = nx.cycle_graph(5)
    topology = mango.custom_topology(G)

    # Bind agents to topology nodes
    agents = []
    for i, node in enumerate(mango.per_node(topology)):
        agent = SimpleAgent(f"Agent{i}")
        container.register(agent)
        node.add(agent)
        agents.append(agent)

    print("Exercise 8: Using mango.custom_topology with NetworkX")
    
    async with mango.activate(container):
        await asyncio.sleep(1)
        print("✓ Topology communication complete!")

if __name__ == "__main__":
    asyncio.run(main())