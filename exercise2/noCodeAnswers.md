### Exercise 3
**Answer:** 
The agents store the neighborhood in a list data structure containing agent addresses.


### Exercise 5
**Answer:** 
No, they don't necessarily contain the same IDs. The neighborhood contains only direct neighbor addresses, while received_ids contains IDs from any agent that sent a message. They match only if communication stays within the defined neighborhood.



### Exercise 6
**Answer:**
- Ring Topology: 30 total messages (10 topology + 20 agent info)
- Small World (k=2): 50 total messages (10 topology + 40 agent info)
- Star Topology: 28 total messages (10 topology + 18 agent info)
*Hence, the star topology is most efficient for message count, while small world provides better connectivity but that means more messages.*


### Exercise 7
**Answer:**
- To make all agents know the IDs of all other agents in the system, we would need to:
- Change the topology agent to send the complete list of all agent addresses to every agent, not just their local neighbors
- Implement a broadcast mechanism where each agent shares its ID with all other agents directly
- Or use a centralized directory where one agent maintains a complete registry and others can query it.
*Hence, we can modify the topology distribution to include all agent addresses in the topology message sent to each agent.*

