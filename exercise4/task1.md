# Exercise 1: Economic Dispatch - Linear Program Formulation

## Problem Data

### Components:
- **Power Plant 1 (PP1)**: 
  - Capacity: 10 MW
  - Cost: 60 €/MWh
  
- **Power Plant 2 (PP2)**:
  - Capacity: 6 MW
  - Cost: 58 €/MWh
  
- **Battery Storage**:
  - Capacity: 10 MWh
  - Initial State of Charge (SoC): 10% = 1 MWh
  - Charge/Discharge cost: 32 €/MWh
  - Power limit: 5 MW (both charge and discharge)
  - Efficiency: 100% (idealized, no losses)

### Time Configuration:
- Duration: 2 hours
- Time steps: 15 minutes (0.25 hours)
- Number of steps: 8
- Time set: T = {1, 2, 3, 4, 5, 6, 7, 8}

### Demand Target (MW):
```
D = [16, 10, 18, 19, 10, 4, 16, 21]ᵀ
```

---

## Decision Variables

For each time step t ∈ T:

- **g₁[t]**: Power output from Plant 1 (MW)
- **g₂[t]**: Power output from Plant 2 (MW)
- **p_charge[t]**: Battery charging power (MW)
- **p_discharge[t]**: Battery discharging power (MW)
- **soc[t]**: Battery state of charge (MWh)

All variables are **non-negative reals**: g₁[t], g₂[t], p_charge[t], p_discharge[t], soc[t] ≥ 0

---

## Objective Function

**Minimize total operational cost:**

```
minimize: Σ (Δt × (c₁·g₁[t] + c₂·g₂[t] + c_bat·p_charge[t] + c_bat·p_discharge[t]))
          t∈T
```

Where:
- Δt = 0.25 hours (time step duration)
- c₁ = 60 €/MWh (Plant 1 cost)
- c₂ = 58 €/MWh (Plant 2 cost)
- c_bat = 32 €/MWh (Battery cost)

**Expanded:**
```
minimize: 0.25 × Σ (60·g₁[t] + 58·g₂[t] + 32·p_charge[t] + 32·p_discharge[t])
                  t=1..8
```

---

## Constraints

### 1. Power Balance (Demand Matching)
For each time step t ∈ T, generation must equal demand:

```
g₁[t] + g₂[t] + p_discharge[t] - p_charge[t] = D[t]
```

**Explanation:**
- Generation from plants: g₁[t] + g₂[t]
- Battery discharging adds power: +p_discharge[t]
- Battery charging consumes power: -p_charge[t]
- Must equal demand: D[t]

### 2. Generator Capacity Limits
```
g₁[t] ≤ 10  ∀t ∈ T    (Plant 1 capacity)
g₂[t] ≤ 6   ∀t ∈ T    (Plant 2 capacity)
```

### 3. Battery Charging/Discharging Power Limits
```
p_charge[t] ≤ 5     ∀t ∈ T    (Max charging power)
p_discharge[t] ≤ 5  ∀t ∈ T    (Max discharging power)
```

### 4. Battery State of Charge (SoC) Dynamics
```
soc[1] = soc_initial + Δt × (p_charge[1] - p_discharge[1])
soc[t] = soc[t-1] + Δt × (p_charge[t] - p_discharge[t])  ∀t ∈ {2,3,...,8}
```

Where:
- soc_initial = 1 MWh (10% of 10 MWh capacity)
- Δt = 0.25 hours

**Explanation:** 
- Energy stored increases when charging
- Energy stored decreases when discharging
- Energy = Power × Time

### 5. Battery Capacity Constraints
```
0 ≤ soc[t] ≤ 10  ∀t ∈ T
```

**Explanation:**
- Cannot discharge below 0 MWh (empty)
- Cannot charge above 10 MWh (full capacity)

### 6. Non-negativity
```
g₁[t], g₂[t], p_charge[t], p_discharge[t], soc[t] ≥ 0  ∀t ∈ T
```

---

## Complete Mathematical Model

### **Minimize:**
```
Z = 0.25 × Σ (60·g₁[t] + 58·g₂[t] + 32·p_charge[t] + 32·p_discharge[t])
            t=1..8
```

### **Subject to:**
```
Power Balance:
  g₁[t] + g₂[t] + p_discharge[t] - p_charge[t] = D[t]  ∀t ∈ {1,...,8}

Generator Limits:
  g₁[t] ≤ 10  ∀t
  g₂[t] ≤ 6   ∀t

Battery Power Limits:
  p_charge[t] ≤ 5     ∀t
  p_discharge[t] ≤ 5  ∀t

Battery SoC Dynamics:
  soc[1] = 1 + 0.25 × (p_charge[1] - p_discharge[1])
  soc[t] = soc[t-1] + 0.25 × (p_charge[t] - p_discharge[t])  ∀t ∈ {2,...,8}

Battery Capacity:
  0 ≤ soc[t] ≤ 10  ∀t

Non-negativity:
  g₁[t], g₂[t], p_charge[t], p_discharge[t] ≥ 0  ∀t
```

---