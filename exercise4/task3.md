# Exercise 3: Does the Pyomo Solution Converge? Is it Optimal? Why?

## Answer

### **YES, the problem converges**

### **YES, the solution is optimal (globally)**

---

## Why Does It Converge?

### 1. **The Problem is Feasible**

A feasible solution exists because:

- **Sufficient generation capacity**: PP1 (10 MW) + PP2 (6 MW) = 16 MW combined capacity
- **Maximum demand**: 21 MW in time step 8
- **Battery can help**: Can discharge up to 5 MW to bridge the gap (16 + 5 = 21 MW)
- **Initial battery charge**: Starting with 1 MWh provides energy buffer

**Example feasible solution at t=8 (demand = 21 MW):**
- PP1: 10 MW (at capacity)
- PP2: 6 MW (at capacity)
- Battery discharge: 5 MW (at power limit)
- Total: 10 + 6 + 5 = 21 MW 

### 2. **The Feasible Region is Bounded**

All constraints create a bounded solution space:
- Generator outputs: 0 ≤ g₁ ≤ 10, 0 ≤ g₂ ≤ 6
- Battery power: 0 ≤ p_charge ≤ 5, 0 ≤ p_discharge ≤ 5
- Battery SoC: 0 ≤ soc ≤ 10

This creates a **compact, closed polytope** in which the optimal solution must exist.

### 3. **Linear Programming Guarantees Convergence**

Properties of LP that ensure convergence:
- **Simplex algorithm** (used by GLPK) always terminates in finite steps
- Either finds optimal solution or determines problem is infeasible/unbounded
- No local minima (only global optimum exists in LP)

---

## Why Is the Solution Optimal?

### 1. **Linear Program with Convex Feasible Region**

**Mathematical proof:**
- The feasible region is a **convex polytope** (intersection of linear constraints)
- The objective function is **linear** (convex)
- **Fundamental theorem of LP**: The optimum of a linear function over a convex polytope occurs at a vertex (corner point)
- The simplex algorithm systematically searches vertices until optimum is found

### 2. **No Local Optima in Linear Programs**

Unlike nonlinear optimization:
- **LP has NO local optima** - any optimum is global
- This is because the objective function is a hyperplane
- The optimal solution occurs where the hyperplane is tangent to the feasible region

### 3. **Solver Certification**

GLPK solver provides guarantees:
- Reports `SolverStatus.ok` when optimal solution found
- Reports `TerminationCondition.optimal` confirming global optimality
- Uses exact arithmetic (within numerical precision) for LP

### 4. **Verification**

We can verify optimality by checking:

**Primal Feasibility:**
- All constraints satisfied (power balance, capacity limits, SoC bounds)

**Dual Feasibility:**
- Shadow prices (dual variables) are non-negative for minimization problem
- Shadow price represents marginal cost of relaxing each constraint

**Complementary Slackness:**
- For each constraint, either:
  - Constraint is tight (active), OR
  - Dual variable is zero

---

## Intuition: Why This Solution Makes Economic Sense

### Economic Dispatch Strategy:

1. **Merit Order Dispatch**: Use cheapest resources first
   - PP2 costs 58 €/MWh (cheapest) → use first
   - Battery costs 32 €/MWh (for charge/discharge) → use strategically
   - PP1 costs 60 €/MWh (most expensive) → use last

2. **Battery Strategy**:
   - **Charge during low demand** (when cheap PP2 can handle it)
   - **Discharge during peak demand** (to avoid expensive PP1)
   - Acts as **energy arbitrage**: store cheap energy, release when expensive

3. **Optimal Behavior**:
   - When demand < 6 MW: Only PP2 runs, may charge battery
   - When 6 MW < demand < 16 MW: PP2 + PP1, battery as needed
   - When demand > 16 MW: All resources at maximum, battery discharges

---

## In Summary:

### **YES, the problem converges** because:
- The problem is feasible (solution exists)
- The feasible region is bounded
- LP algorithms guarantee finite termination

### **YES, the solution is globally optimal** because:
- Linear programs have no local optima
- The simplex algorithm finds the global optimum
- Solver provides mathematical guarantee of optimality