import asyncio
import mango

class SimpleAgent(mango.Agent):
    def __init__(self):
        super().__init__()
        self.known_ids = set()
        self.my_id = None

    def handle_message(self, content, meta):
        if content == "your_id":
            self.my_id = meta['sender_id']
            print(f"Agent assigned ID: {self.my_id}")
            
        elif content == "neighbor_info":
            neighbor_id = meta['sender_id']
            self.known_ids.add(neighbor_id)
            print(f"Agent learned about neighbor: {neighbor_id}")

async def main():
    container = mango.create_tcp_container(('127.0.0.1', 5555))
    
    # Create 10 agents
    agents = [SimpleAgent() for _ in range(10)]
    for agent in agents:
        container.register(agent)
    
    print("Exercise 2: Ring Topology with 10 Agents")
    
    async with mango.activate(container):
        # Step 1: Assign IDs to all agents
        for i, agent in enumerate(agents):
            await container.send_message("your_id", agent.addr, sender_id=i)
        
        await asyncio.sleep(0.5)
        
        # Step 2: Create ring topology - each agent informs its neighbors
        for i in range(10):
            left_neighbor = agents[(i - 1) % 10]
            right_neighbor = agents[(i + 1) % 10]
            
            # Agent i informs left neighbor
            await container.send_message("neighbor_info", left_neighbor.addr, sender_id=i)
            # Agent i informs right neighbor
            await container.send_message("neighbor_info", right_neighbor.addr, sender_id=i)
        
        await asyncio.sleep(1)
        
        # Results
        print("\n=== Final State ===")
        for i, agent in enumerate(agents):
            expected_neighbors = [(i-1)%10, (i+1)%10]
            print(f"Agent {i}: knows {sorted(agent.known_ids)} (expected: {sorted(expected_neighbors)})")

if __name__ == "__main__":
    asyncio.run(main())