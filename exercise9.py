import asyncio
import mango
import random

class HouseAgent(mango.Agent):
    def handle_message(self, content, meta):
        if content == "price_announcement":
            price = random.uniform(0.12, 0.18)
            production = random.randint(0, 10)
            consumption = random.randint(3, 7)
            balance = production - consumption
            
            if balance > 0:
                print(f"House: Selling {balance}kWh at {price:.3f}€")
            elif balance < 0:
                print(f"House: Buying {-balance}kWh at {price:.3f}€")
            else:
                print(f"House: Balanced")

async def main():
    container = mango.create_tcp_container(('127.0.0.1', 5555))
    
    # Create 3 house agents
    houses = [HouseAgent() for _ in range(3)]
    for house in houses:
        container.register(house)
    
    print("=== Energy Market Concept ===")
    
    async with mango.activate(container):
        for round in range(3):
            print(f"\nRound {round + 1}:")
            for house in houses:
                await container.send_message("price_announcement", house.addr)
            await asyncio.sleep(0.5)

    print("\n=== Simulation Complete ===")
    print("This demonstrates how agents can represent autonomous energy producers/consumers")
    print("Each house agent makes independent decisions based on local information")


if __name__ == "__main__":
    asyncio.run(main())