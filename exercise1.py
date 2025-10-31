import asyncio
import mango

async def main():
    # 1. Create a TCP container
    container = mango.create_tcp_container(('127.0.0.1', 5555))

    # Create the agent (but do NOT register yet)
    agent = mango.PrintingAgent()

    print("\n--- Stage 1: BEFORE register ---")
    print("Agent address:", agent.addr, "(This is because Agent has not been registered or activated yet)") 
    
    
    # 2. Register the agent (but container is still not active)
    container.register(agent)

    print("\n--- Stage 2: AFTER register but BEFORE activate ---")
    print("Agent address:", agent.addr)   # Now the agent has an address
    await container.send_message("Hello Agent1!", agent.addr)
    # Still no output yet because container isn't active

    print("\n--- Stage 3: AFTER activate ---")
    # Now we activate the container
    async with mango.activate(container):
        await container.send_message("Message after activation!", agent.addr)
        # Now the agent prints the received message
        await asyncio.sleep(0.2)  # Allow message to process

if __name__ == "__main__":
    asyncio.run(main())
