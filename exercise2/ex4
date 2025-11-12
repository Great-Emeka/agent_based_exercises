import asyncio
import mango

# Reusing the same SimpleAgent class from my Exercise 2
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
            print(f"Agent {self.my_id} learned about neighbor: {neighbor_id}")

async def main():
    container = mango.create_tcp_container(('127.0.0.1', 5555))
    
    # Create 10 agents
    agents = [SimpleAgent() for _ in range(10)]
    for agent in agents:
        container.register(agent)
    
    print("Exercise 4: Small World Topology with k=2")
    print("Each agent connects to 2 neighbors on each side")
    
    async with mango.activate(container):
        # Assign IDs
        for i, agent in enumerate(agents):
            await container.send_message("your_id", agent.addr, sender_id=i)
        
        await asyncio.sleep(0.5)
        
        # Create Small World connections (k=2)
        n = 10
        connections_made = 0
        
        for i in range(n):
            # Connect to 2 neighbors on left and 2 on right
            neighbors_to_connect = [
                (i - 2) % n,  # 2 steps left
                (i - 1) % n,  # 1 step left  
                (i + 1) % n,  # 1 step right
                (i + 2) % n   # 2 steps right
            ]
            
            for neighbor_idx in neighbors_to_connect:
                await container.send_message("neighbor_info", agents[neighbor_idx].addr, sender_id=i)
                connections_made += 1
        
        print(f"Total connections made: {connections_made}")
        
        await asyncio.sleep(1)
        
        # Verify results
        print("\n=== Verification ===")
        correct_count = 0
        for i, agent in enumerate(agents):
            expected = {(i-2)%10, (i-1)%10, (i+1)%10, (i+2)%10}
            if agent.known_ids == expected:
                correct_count += 1
                print(f"Agent {i}: ✓ Correct - knows all 4 neighbors")
            else:
                print(f"Agent {i}: ✗ Missing some neighbors")
                print(f"  Has: {sorted(agent.known_ids)}")
                print(f"  Expected: {sorted(expected)}")
        
        print(f"\nSuccess rate: {correct_count}/10 agents have correct neighborhood")

if __name__ == "__main__":
    asyncio.run(main())