import asyncio
import mango
import random

class HouseAgent(mango.Agent):
    def __init__(self, house_id, production_capacity):
        super().__init__()
        self.house_id = house_id
        self.production_capacity = production_capacity
        self.energy_balance = 0
        self.profit = 0
        self.market_agent_addr = None
        
    def handle_message(self, content, meta):
        if content.get('type') == 'MARKET_ANNOUNCEMENT':
            self.market_agent_addr = meta['sender_addr'] if meta and 'sender_addr' in meta else None
            price = content['price']
            
            # Simulate energy production and consumption
            production = random.randint(0, self.production_capacity)
            consumption = random.randint(2, 6)
            self.energy_balance = production - consumption
            
            print(f"House {self.house_id}: Produced {production} kWh, Consumed {consumption} kWh, Balance: {self.energy_balance} kWh")
            
            if self.energy_balance > 0 and self.market_agent_addr:
                # Sell surplus energy
                offer = {
                    'type': 'ENERGY_OFFER',
                    'house_id': self.house_id,
                    'amount': self.energy_balance,
                    'min_price': price * 0.8  # Willing to sell at discount
                }
                # Convert tuple to AgentAddress for sending
                market_addr = mango.AgentAddress(protocol_addr=self.market_agent_addr, aid='market')
                self.schedule_instant_message(offer, market_addr)
                print(f"House {self.house_id}: Offering {self.energy_balance} kWh at {offer['min_price']:.3f} €/kWh")
            elif self.energy_balance < 0 and self.market_agent_addr:
                # Need to buy energy
                request = {
                    'type': 'ENERGY_REQUEST', 
                    'house_id': self.house_id,
                    'amount': -self.energy_balance,
                    'max_price': price * 1.2  # Willing to pay premium
                }
                # Convert tuple to AgentAddress for sending
                market_addr = mango.AgentAddress(protocol_addr=self.market_agent_addr, aid='market')
                self.schedule_instant_message(request, market_addr)
                print(f"House {self.house_id}: Requesting {-self.energy_balance} kWh at max {request['max_price']:.3f} €/kWh")
            else:
                print(f"House {self.house_id}: Balanced - no trading needed")
                
        elif content.get('type') == 'TRADE_CONFIRMATION':
            if content['house_id'] == self.house_id:
                self.profit += content['profit']
                print(f"House {self.house_id}: Trade confirmed! Profit: {content['profit']:.2f} €, Total profit: {self.profit:.2f} €")

class MarketAgent(mango.Agent):
    def __init__(self):
        super().__init__()
        self.offers = []
        self.requests = []
        self.market_price = 0.15  # €/kWh
        
    def handle_message(self, content, meta):
        if content.get('type') == 'ENERGY_OFFER':
            sender_addr = meta['sender_addr'] if meta and 'sender_addr' in meta else None
            self.offers.append({
                'house_id': content['house_id'],
                'amount': content['amount'],
                'price': content['min_price'],
                'sender': sender_addr
            })
            print(f"Market: Received offer from House {content['house_id']} for {content['amount']} kWh at {content['min_price']:.3f} €/kWh")
            
        elif content.get('type') == 'ENERGY_REQUEST':
            sender_addr = meta['sender_addr'] if meta and 'sender_addr' in meta else None
            self.requests.append({
                'house_id': content['house_id'],
                'amount': content['amount'],
                'price': content['max_price'], 
                'sender': sender_addr
            })
            print(f"Market: Received request from House {content['house_id']} for {content['amount']} kWh at max {content['max_price']:.3f} €/kWh")
            
        # Simple matching logic
        if len(self.offers) > 0 and len(self.requests) > 0:
            self.match_orders()
    
    def match_orders(self):
        """Simple order matching algorithm"""
        if self.offers and self.requests:
            offer = self.offers.pop(0)
            request = self.requests.pop(0)
            
            # Determine trade price (average of offer and request prices)
            trade_price = (offer['price'] + request['price']) / 2
            trade_amount = min(offer['amount'], request['amount'])
            
            # Calculate profits
            seller_profit = trade_amount * (trade_price - offer['price'])
            buyer_cost = trade_amount * trade_price
            
            # Notify participants
            seller_confirmation = {
                'type': 'TRADE_CONFIRMATION',
                'house_id': offer['house_id'],
                'profit': seller_profit
            }
            buyer_confirmation = {
                'type': 'TRADE_CONFIRMATION',
                'house_id': request['house_id'], 
                'profit': -buyer_cost  # Negative for buyer (cost)
            }
            
            # Convert sender tuples to AgentAddress objects
            if offer['sender']:
                seller_addr = mango.AgentAddress(protocol_addr=offer['sender'], aid=f"house{offer['house_id']}")
                self.schedule_instant_message(seller_confirmation, seller_addr)
            
            if request['sender']:
                buyer_addr = mango.AgentAddress(protocol_addr=request['sender'], aid=f"house{request['house_id']}")
                self.schedule_instant_message(buyer_confirmation, buyer_addr)
            
            print(f"Market: Matched House {offer['house_id']} (seller) with House {request['house_id']} (buyer)")
            print(f"        Traded {trade_amount} kWh at {trade_price:.3f} €/kWh")

async def main():
    container = mango.create_tcp_container(('127.0.0.1', 5555))

    # Create market agent
    market_agent = MarketAgent()
    container.register(market_agent)

    # Create house agents with different production capacities
    houses = []
    for i in range(3):
        house = HouseAgent(house_id=i+1, production_capacity=8+i*2)
        container.register(house)
        houses.append(house)

    print("=== Energy Trading Market Simulation ===")
    
    async with mango.activate(container):
        # Simulate multiple trading rounds
        for round_num in range(3):
            print(f"\n--- Trading Round {round_num + 1} ---")
            
            # Market announces current price with some fluctuation
            market_announcement = {
                'type': 'MARKET_ANNOUNCEMENT',
                'price': 0.15 + random.uniform(-0.03, 0.03)
            }
            
            # Notify all houses
            for house in houses:
                await container.send_message(market_announcement, house.addr)
            
            await asyncio.sleep(1.5)  # Wait for trading to complete
    
    print("\n=== Simulation Complete ===")

if __name__ == "__main__":
    asyncio.run(main())