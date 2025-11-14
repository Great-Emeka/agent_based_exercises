import asyncio
from mango import Agent, AgentAddress, create_tcp_container, json_serializable, activate
from mango.messages.codecs import JSON
from typing import Dict, Any, Optional

# 1. Self-defined message class (this part is correct)
@json_serializable
class MyMessage:
    def __init__(self, text: str, data: Dict[str, Any]):
        self.text = text
        self.data = data

    def __repr__(self):
        return f"MyMessage(text='{self.text}', data={self.data})"

# 2. Receiver Agent (this part is correct)
class ReceiverAgent(Agent):
    def __init__(self):
        super().__init__()
        self.message_counter = 0
        self.expected_messages = 3
        self.done_event = asyncio.Event()

    def handle_message(self, content, meta):
        print(f"Receiver: Received {content!r} (type: {type(content).__name__})")
        self.message_counter += 1
        if self.message_counter >= self.expected_messages:
            self.done_event.set()

# 3. Sender Agent with the corrected on_ready method
class SenderAgent(Agent):
    def __init__(self):
        super().__init__()
        self.receiver_addr: Optional[AgentAddress] = None

    def on_ready(self):
        """
        This is the lifecycle hook called by Mango when the agent is ready.
        """
        asyncio.create_task(self.send_all_messages())


    async def send_all_messages(self):
        """The agent's main logic, running as a standard asyncio task."""
        if not self.receiver_addr:
            print("Sender: Error - Receiver address has not been set.")
            return

        print("Sender: Agent is ready, sending messages...")
        messages_to_send = [
            "Hello from a string!",
            {"message": "This is a dictionary"},
            MyMessage("This is a custom object", {"value": 42})
        ]

        for msg in messages_to_send:
            await self.send_message(content=msg, receiver_addr=self.receiver_addr)
        
        print("Sender: All messages sent.")

# 4. The main function that sets up the containers and agents
async def main():
    """Sets up and runs the multi-container agent system."""
    codec = JSON()
    codec.add_serializer(*MyMessage.__serializer__())

    c1 = create_tcp_container(addr=('127.0.0.1', 5555), codec=codec)
    c2 = create_tcp_container(addr=('127.0.0.1', 5556), codec=codec)

    sender_agent = SenderAgent()
    receiver_agent = ReceiverAgent()
    
    a1 = c1.register(agent=sender_agent)
    a2 = c2.register(agent=receiver_agent)

    a1.receiver_addr = a2.addr

    async with activate(c1, c2):
        print("Main: Containers are active. Waiting for receiver to signal completion...")
        await a2.done_event.wait()
        print("\nMain: Receiver confirmed all messages received. Shutting down.")


if __name__ == "__main__":
    asyncio.run(main())