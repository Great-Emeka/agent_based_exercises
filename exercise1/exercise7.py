import asyncio
import mango

# Reflexive Agent: Immediate, predetermined response
class ReflexiveAgent(mango.Agent):
    def handle_message(self, content, meta):
        # Always responds the same way regardless of content
        print(f"Reflexive: Received '{content}' Hello") #-> Always says "Hello" back!

# Deliberative Agent: Uses internal state and reasoning
class DeliberativeAgent(mango.Agent):
    def __init__(self):
        super().__init__()
        self.message_count = 0
        self.previous_messages = []
    
    def handle_message(self, content, meta):
        self.message_count += 1
        self.previous_messages.append(content)
        
        # Makes decision based on history and state
        if self.message_count > 2:
            response = f"Received {self.message_count} msgs. Pattern detected!"
        else:
            response = f"Learning... ({self.message_count}/3 messages)"
            
        print(f"Deliberative: Received '{content}' -> {response}")

async def main():
    container = mango.create_tcp_container(('127.0.0.1', 5555))
    
    reflex = ReflexiveAgent()
    deliberative = DeliberativeAgent()
    
    container.register(reflex)
    container.register(deliberative)
    
    print("=== Reflexive vs Deliberative Agents ===\n")
    
    async with mango.activate(container):
        # Test both agents
        print("Testing Reflexive Agent:")
        await container.send_message("Hi!", reflex.addr)
        await container.send_message("How are you?", reflex.addr)
        await container.send_message("Weather?", reflex.addr)
        
        await asyncio.sleep(0.5)
        
        print("\nTesting Deliberative Agent:")
        await container.send_message("First", deliberative.addr)
        await container.send_message("Second", deliberative.addr) 
        await container.send_message("Third", deliberative.addr)

if __name__ == "__main__":
    asyncio.run(main())