# Multi-Agent Exercise (mango Framework)

This project contains solutions to Exercise Sheet 1 for the course **Agent-based Control in Energy Systems**.  
The implementation uses the **mango** multi-agent framework built on Python's `asyncio`.

## What This Project Covers
- Creating and activating a mango **Container**
- Using a **PrintingAgent**
- Implementing custom agents that:
  - React to incoming messages
  - Keep internal state (message counters)
  - Communicate with other agents (ping-pong behavior)
- Extending agents to exchange values using the **Fibonacci sequence**
- Demonstrating **reflexive vs. deliberative agent** behavior
- Designing a small conceptual **multi-agent system** for an energy-use scenario

## Requirements
- Python **3.10+**
- `mango` framework installed
- Basic understanding of `asyncio`

## Setup
```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## RUNNING THE CODE:

python -m asyncio run <script_name>.py


## Notes

All exercises follow the lifecycle and messaging concepts defined in mango.

The example systems are conceptual and intended for learning, not production.