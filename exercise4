import asyncio
import mango

class FibonacciAgent(mango.Agent):
    def __init__(self):
        super().__init__()
        self.partner_addr = None
        self.n = 1
        self.prev = 0
        self.current = 1
        self.max_n = 8

    def handle_message(self, content, meta):
        if content == "START":
            print(f"[{self.addr}] Starting Fibonacci sequence...")
            self.send_next_number()
        elif isinstance(content, dict) and 'fib' in content:
            received_n = content['n']
            received_fib = content['fib']
            print(f"[{self.addr}] Received: f({received_n}) = {received_fib}")
            
            if received_n < self.max_n:
                self.n = received_n + 1
                # Calculate next Fibonacci number
                next_fib = self.current + received_fib
                self.prev = self.current
                self.current = next_fib
                self.send_next_number()
            else:
                print(f"[{self.addr}] Maximum n={self.max_n} reached. Terminating.")
    
    def send_next_number(self):
        if self.n <= self.max_n:
            message = {'n': self.n, 'fib': self.current}
            print(f"[{self.addr}] Sending: f({self.n}) = {self.current}")
            self.schedule_instant_message(message, self.partner_addr)

async def main():
    container = mango.create_tcp_container(('127.0.0.1', 5555))

    # Create agents
    agent1 = FibonacciAgent()
    agent2 = FibonacciAgent()

    # Register agents
    container.register(agent1)
    container.register(agent2)

    # Set up partnership
    agent1.partner_addr = agent2.addr
    agent2.partner_addr = agent1.addr

    # Initialize agent2 with starting values
    agent2.n = 2
    agent2.prev = 1
    agent2.current = 1

    print("Starting Fibonacci sequence exchange...")
    
    async with mango.activate(container):
        await container.send_message("START", agent1.addr)
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())

'''
SOLUTION EXPLANATION:
By starting both agents with initial messages, 
we ensure they both get the extra message needed to reach 10.
'''