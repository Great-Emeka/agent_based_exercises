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
            
        elif content == "neighbor_info":
            neighbor_id = meta['sender_id']
            self.known_ids.add(neighbor_id)

async def main():
    container = mango.create_tcp_container(('127.0.0.1', 5555))
    
    # Create 10 agents
    agents = [SimpleAgent() for _ in range(10)]
    for agent in agents:
        container.register(agent)
    
    print("Exercise 4: Small World Topology (k=2)")
    
    async with mango.activate(container):
        # Step 1: Assign IDs to all agents
        for i, agent in enumerate(agents):
            await container.send_message("your_id", agent.addr, sender_id=i)
        
        await asyncio.sleep(0.5)
        
        # Step 2: Create Small World topology with k=2
        # Each agent connects to 2 neighbors on each side (total 4 connections)
        n = len(agents)
        for i in range(n):
            # Connect to neighbors within distance 2
            for offset in [-2, -1, 1, 2]:
                neighbor_idx = (i + offset) % n
                # Agent i informs this neighbor
                await container.send_message("neighbor_info", agents[neighbor_idx].addr, sender_id=i)
        
        await asyncio.sleep(1)
        
        # Results
        print("\n=== Small World Topology Results ===")
        print("Each agent should know 4 neighbors (k=2 on each side)")
        
        total_connections = 0
        for i, agent in enumerate(agents):
            total_connections += len(agent.known_ids)
            expected_neighbors = [
                (i-2) % n, (i-1) % n,  # left side
                (i+1) % n, (i+2) % n   # right side
            ]
            print(f"Agent {i}: knows {len(agent.known_ids)} IDs -> {sorted(agent.known_ids)}")
            print(f"        Expected: {sorted(expected_neighbors)}")
        
        print(f"\nTotal connections: {total_connections} (should be {n * 4})")

if __name__ == "__main__":
    asyncio.run(main())