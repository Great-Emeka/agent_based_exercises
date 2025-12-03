## Problem Context:

**Scenario:** Microgrid with N distributed generators (DGs)
- Each DG agent measures only its own power output: P_i
- Goal: Estimate total system generation P_total = Σ P_i
- Challenge: No agent directly observes the global quantity

---

## 1. Centralized Observer-Controller

### Architecture Diagram
```
┌─────────────────────────────────────────────┐
│         CENTRAL OBSERVER-CONTROLLER         │
│                                             │
│  ┌─────────────┐      ┌──────────────┐    │
│  │  Observer   │      │  Controller  │    │
│  │             │      │              │    │
│  │  Computes:  │─────▶│  Computes:   │    │
│  │  P_total    │      │  Setpoints   │    │
│  └──────┬──────┘      └──────┬───────┘    │
│         │                     │             │
└─────────┼─────────────────────┼─────────────┘
          │                     │
    ┌─────▼─────────────────────▼─────┐
    │        Communication Bus         │
    └─┬────┬────┬────┬────┬────┬─────┘
      │    │    │    │    │    │
   ┌──▼─┐┌─▼──┐┌▼──┐┌▼──┐┌▼──┐┌▼─┐
   │DG1 ││DG2 ││DG3││DG4││DG5││DGN│
   └────┘└────┘└───┘└───┘└───┘└───┘
      ▲    ▲    ▲    ▲    ▲    ▲
      │    │    │    │    │    │
      Send P_i measurements upward
```

### How it Works:
| **Information Flow** | Star pattern: all data flows to/from center |
| **Communication** | N uplinks (measurements) + N downlinks (setpoints) |
| **Computation** | All done centrally |
| **Scalability** | Poor: Central bottleneck grows with N |
| **Robustness** | Poor: Single point of failure |
| **Optimality** | Excellent: Global view enables optimal decisions |
| **Latency** | Medium: Two hops for any action |


## 2. Decentralized Observer-Controller

### Architecture Diagram
```
┌─────────────────────────────────────────────┐
│       FULLY DECENTRALIZED SYSTEM            │
│                                             │
│   Each agent has local O/C                  │
└─────────────────────────────────────────────┘

    DG1 ←→ DG2 ←→ DG3 ←→ DG4 ←→ DG5
     ↕              ↕              ↕
    DGN ←─────────→ ... ←────────→ DG6

┌──────────────────────────────────┐
│  Agent i (Local O/C)             │
│                                  │
│  ┌──────────┐   ┌──────────┐     │
│  │ Observer │──▶│Controller│     │
│  │          │   │          │     │
│  │ Estimate │   │ Compute  │     │
│  │ P_total  │   │ P_i^ref  │     │
│  └────┬─────┘   └────┬─────┘     │
│       │              │           │
│    Local P_i      Adjust P_i     │
└───────┼──────────────┼──────────-┘
        │              │
     Measure        Actuate
```

### How it Works

| **Information Flow** | Peer-to-peer: only neighbor communication |
| **Communication** | O(N·d) where d = avg neighbors |
| **Computation** | Distributed across all agents |
| **Scalability** | Excellent: No central bottleneck |
| **Robustness** | Good: No single point of failure |
| **Optimality** | Approximate: Consensus ≈ global view |
| **Latency** | Higher: Multiple iterations needed |



## 3. Multi-Level Observer-Controller

### Architecture Diagram
```
┌─────────────────────────────────────────────┐
│         LEVEL 2: REGIONAL COORDINATOR       │
│                                             │
│    Region A Coord  ←→  Region B Coord       │
│         ▲                    ▲              │
└─────────┼────────────────────┼──────────────┘
          │                    │
    ┌─────┴──────┐       ┌────┴────────┐
    │            │       │             │
┌───▼────┐  ┌───▼────┐ ┌▼────┐  ┌────▼──┐
│ LEVEL 1: LOCAL CONTROLLERS │  │ LOCAL  │
│                             │  │        │
│ ┌─────┐  ┌─────┐           │ ┌┴─────┐ │
│ │DG1  │  │DG2  │           │ │DG4   │ │
│ │     │  │     │           │ │      │ │
└─┴─────┴──┴─────┴───────────┴─┴──────┴─┘
  Local     Local              Local
  Cluster   Cluster            Cluster
```

### How It Works

| **Information Flow** | Hierarchical: local → regional → global |
| **Communication** | Moderate: O(N/k + k) for k clusters |
| **Computation** | Distributed hierarchically |
| **Scalability** | Good: Hierarchical decomposition |
| **Robustness** | Moderate: Regional nodes are critical |
| **Optimality** | Good: Near-optimal with decomposition |
| **Latency** | Medium: Multiple levels |
