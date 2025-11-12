import asyncio
import mango

class PingPongAgent(mango.Agent):
    def __init__(self):
        super().__init__()
        self.message_count = 0
        self.partner_addr = None

    def handle_message(self, content, meta):
        
        print(f"[{self.addr}] Received: '{content}'")

        # Send message to partner until counter reaches 10
        if self.message_count < 10 and self.partner_addr:
            if 'ping' in content.lower():
                response = "Pong!"
            else:
                response = "Ping!"
            
            self.schedule_instant_message(response, self.partner_addr)
            self.message_count += 1
            print(f"[{self.addr}] Sent: '{response}' {self.message_count}")
            #print(f"[{self.addr}] Sent: '{response}'")

async def main():
    # Create container
    container = mango.create_tcp_container(('127.0.0.1', 5555))

    # Create two agents
    agent1 = PingPongAgent()
    agent2 = PingPongAgent()

    # Register agents
    container.register(agent1)
    container.register(agent2)

    # Make them know each other
    agent1.partner_addr = agent2.addr
    agent2.partner_addr = agent1.addr

    print("Starting ping-pong communication...")
    
    # Activate container and start communication
    async with mango.activate(container):
        # Start BOTH agents with initial messages
        await agent1.send_message("Start ping!", agent2.addr)
        await asyncio.sleep(2)  # Wait for communication to complete
    
    print(f"Final counts - Agent1: {agent1.message_count}, Agent2: {agent2.message_count}")

if __name__ == "__main__":
    asyncio.run(main())