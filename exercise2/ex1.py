import asyncio
import mango

class RingAgent(mango.Agent):
    def __init__(self, agent_id):
        super().__init__()
        self.agent_id = agent_id
        self.received_greetings = []
        self.expected_greetings = 2  # Each agent should receive 2 greetings

    def handle_message(self, content, meta):
        if content == "greeting":
            sender_id = meta['sender_id']
            self.received_greetings.append(sender_id)
            print(f"Agent {self.agent_id} received from Agent {sender_id}")

async def main():
    container = mango.create_tcp_container(('127.0.0.1', 5555))
    
    # Create exactly 5 agents as required
    agents = [RingAgent(i) for i in range(5)]
    for agent in agents:
        container.register(agent)
    
    # Set up proper ring topology: 0-1-2-3-4-0
    for i in range(5):
        left_neighbor = agents[(i - 1) % 5]
        right_neighbor = agents[(i + 1) % 5]
        agents[i].neighbors = [left_neighbor.addr, right_neighbor.addr]
    
    # Create completion event
    completion_event = asyncio.Event()
    
    print("Starting 5-agent ring topology...")
    
    async with mango.activate(container):
        # Each agent sends ONE greeting to EACH neighbor (2 greetings per agent)
        messages_sent = 0
        for agent in agents:
            for neighbor_addr in agent.neighbors:
                await container.send_message("greeting", neighbor_addr, sender_id=agent.agent_id)
                messages_sent += 1
                print(f"Agent {agent.agent_id} sent greeting to neighbor")
        
        print(f"Total messages sent: {messages_sent}")
        
        # Monitor completion using asyncio.Event
        async def check_completion():
            while True:
                total_received = sum(len(agent.received_greetings) for agent in agents)
                print(f"Progress: {total_received}/10 greetings received")
                
                if total_received >= 10:
                    completion_event.set()
                    break
                await asyncio.sleep(0.1)
        
        # Start monitoring task
        monitor_task = asyncio.create_task(check_completion())
        
        # Wait for completion event
        print("Waiting for all greetings to be received...")
        await completion_event.wait()
        monitor_task.cancel()
        
        print("✓ All 10 greetings received! System terminating.")
        
        # Verify results
        print("\n=== Final Results ===")
        total_received = 0
        for agent in agents:
            total_received += len(agent.received_greetings)
            print(f"Agent {agent.agent_id}: received from {sorted(agent.received_greetings)}")
        
        print(f"Total greetings received: {total_received}/10")

if __name__ == "__main__":
    asyncio.run(main())