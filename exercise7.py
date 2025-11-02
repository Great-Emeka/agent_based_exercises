import asyncio
import mango
import random

# Reflexive Agent: Simple stimulus-response behavior
class ReflexiveAgent(mango.Agent):
    def __init__(self):
        super().__init__()
        
    def handle_message(self, content, meta):
        # Simple reflex: immediate response based on keywords
        if "temperature" in str(content).lower():
            response = "Turning on AC"
        elif "light" in str(content).lower():
            response = "Turning on lights"
        elif "door" in str(content).lower():
            response = "Locking door"
        else:
            response = "I don't understand this command"
            
        print(f"[{self.addr}] Reflexive: Received '{content}' -> Immediate response: '{response}'")
        # Note: No reply sending to avoid address issues

# Deliberative Agent: Maintains internal state and uses reasoning
class DeliberativeAgent(mango.Agent):
    def __init__(self):
        super().__init__()
        self.internal_state = {
            'temperature_history': [],
            'preferred_temperature': 22,
            'energy_consumption': 0,
            'decision_log': []
        }
        
    def handle_message(self, content, meta):
        if isinstance(content, dict) and 'temperature' in content:
            current_temp = content['temperature']
            self.internal_state['temperature_history'].append(current_temp)
            
            # Deliberation: analyze history and make reasoned decision
            if len(self.internal_state['temperature_history']) >= 3:
                avg_temp = sum(self.internal_state['temperature_history'][-3:]) / 3
                preferred = self.internal_state['preferred_temperature']
                
                # Complex reasoning based on multiple factors
                if avg_temp > preferred + 3:
                    action = "Activate emergency cooling"
                    energy_impact = 3
                elif avg_temp > preferred + 2:
                    action = "Increase cooling power"
                    energy_impact = 2
                elif avg_temp < preferred - 2:
                    action = "Increase heating"
                    energy_impact = 1
                else:
                    action = "Maintain optimal settings"
                    energy_impact = 0
                    
                self.internal_state['energy_consumption'] += energy_impact
                
                reasoning = f"Analysis: Avg={avg_temp:.1f}°C, Preferred={preferred}°C, Energy={self.internal_state['energy_consumption']} units"
                response = f"{action} | {reasoning}"
                self.internal_state['decision_log'].append(response)
                
                print(f"[{self.addr}] Deliberative: After 3 readings -> Complex decision: '{response}'")
            else:
                print(f"[{self.addr}] Deliberative: Received temp {current_temp}°C -> Need more data ({len(self.internal_state['temperature_history'])}/3)")
                
        elif content == "get_stats":
            print(f"[{self.addr}] Deliberative: System Statistics: {self.internal_state}")
        else:
            print(f"[{self.addr}] Deliberative: Received '{content}' -> Need structured data")

async def main():
    container = mango.create_tcp_container(('127.0.0.1', 5555))

    # Create agents
    reflex_agent = ReflexiveAgent()
    deliberative_agent = DeliberativeAgent()

    # Register agents
    container.register(reflex_agent)
    container.register(deliberative_agent)

    print("=== Testing Reflexive vs Deliberative Agents ===")
    print("Reflexive: Immediate, predetermined responses")
    print("Deliberative: Maintains state, analyzes history, makes reasoned decisions\n")
    
    async with mango.activate(container):
        # Test reflexive agent
        print("--- Testing Reflexive Agent ---")
        await container.send_message("It's hot here!", reflex_agent.addr)
        await asyncio.sleep(0.3)
        await container.send_message("Turn on the light", reflex_agent.addr)
        await asyncio.sleep(0.3)
        await container.send_message("Close the door", reflex_agent.addr)
        await asyncio.sleep(0.3)
        await container.send_message("Random message", reflex_agent.addr)
        
        await asyncio.sleep(1)
        
        # Test deliberative agent
        print("\n--- Testing Deliberative Agent ---")
        await container.send_message({"temperature": 25}, deliberative_agent.addr)
        await asyncio.sleep(0.3)
        await container.send_message({"temperature": 26}, deliberative_agent.addr)
        await asyncio.sleep(0.3)
        await container.send_message({"temperature": 27}, deliberative_agent.addr)
        await asyncio.sleep(0.3)
        await container.send_message("get_stats", deliberative_agent.addr)
        
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())