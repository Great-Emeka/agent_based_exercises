import mango
import asyncio

async def main():
    container = mango.create_tcp_container(addr=('127.0.0.1', 5555))
    #print(f"Container address: {container.addr}")

    agent = mango.PrintingAgent()
    container.register(agent)
    
    async with mango.activate(container) as c:
        await c.send_message("Hello Agent", receiver_addr=agent.addr)

if __name__ == "__main__":
    asyncio.run(main())