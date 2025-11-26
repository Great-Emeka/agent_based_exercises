import pyomo.environ as pyo

def solve_economic_dispatch():
    # FIRSTLY, We CREATE MODEL
    model = pyo.ConcreteModel(name="Economic_Dispatch")
    
    # ========================================================================
    # Defining all PARAMETERS (Input Data)
    
    # Time configuration
    num_timesteps = 8
    dt = 0.25  # hours (15 minutes)
    model.T = pyo.RangeSet(1, num_timesteps)
    
    # Demand target (MW) for each time step
    demand_data = {
        1: 16.0,
        2: 10.0,
        3: 18.0,
        4: 19.0,
        5: 10.0,
        6: 4.0,
        7: 16.0,
        8: 21.0
    }
    
    # Power plant parameters
    PP1_capacity = 10.0  # MW
    PP1_cost = 60.0      # €/MWh
    
    PP2_capacity = 6.0   # MW
    PP2_cost = 58.0      # €/MWh
    
    # Battery parameters
    BAT_capacity = 10.0        # MWh (energy capacity)
    BAT_power_limit = 5.0      # MW (power limit for charge/discharge)
    BAT_initial_soc = 1.0      # MWh (10% of 10 MWh)
    BAT_cost = 32.0            # €/MWh
    
    # Create Pyomo parameters
    model.demand = pyo.Param(model.T, initialize=demand_data, 
                            within=pyo.NonNegativeReals)
    
    # ========================================================================
    # DEFINING DECISION VARIABLES
    # ========================================================================
    
    # Power plant generation (MW)
    model.g1 = pyo.Var(model.T, domain=pyo.NonNegativeReals, 
                       doc="Power Plant 1 output")
    model.g2 = pyo.Var(model.T, domain=pyo.NonNegativeReals, 
                       doc="Power Plant 2 output")
    
    # Battery power (MW)
    model.p_charge = pyo.Var(model.T, domain=pyo.NonNegativeReals, 
                            doc="Battery charging power")
    model.p_discharge = pyo.Var(model.T, domain=pyo.NonNegativeReals, 
                               doc="Battery discharging power")
    
    # Battery state of charge (MWh)
    model.soc = pyo.Var(model.T, domain=pyo.NonNegativeReals, 
                       doc="Battery state of charge")
    
    # ========================================================================
    # DEFINING CONSTRAINTS
    # ========================================================================
    
    # Constraint 1: Power Balance (Demand Matching)
    def power_balance_rule(m, t):
        """
        At each time step, generation + battery discharge - battery charge
        must equal demand.
        """
        return (m.g1[t] + m.g2[t] + m.p_discharge[t] - m.p_charge[t] 
                == m.demand[t])
    
    model.PowerBalance = pyo.Constraint(model.T, rule=power_balance_rule,
                                       doc="Supply must meet demand")
    
    # Constraint 2: Generator Capacity Limits
    def gen1_capacity_rule(m, t):
        """Power Plant 1 cannot exceed 10 MW."""
        return m.g1[t] <= PP1_capacity
    
    model.Gen1Capacity = pyo.Constraint(model.T, rule=gen1_capacity_rule)
    
    def gen2_capacity_rule(m, t):
        """Power Plant 2 cannot exceed 6 MW."""
        return m.g2[t] <= PP2_capacity
    
    model.Gen2Capacity = pyo.Constraint(model.T, rule=gen2_capacity_rule)
    
    # Constraint 3: Battery Power Limits
    def charge_limit_rule(m, t):
        """Battery charging power cannot exceed 5 MW."""
        return m.p_charge[t] <= BAT_power_limit
    
    model.ChargeLimit = pyo.Constraint(model.T, rule=charge_limit_rule)
    
    def discharge_limit_rule(m, t):
        """Battery discharging power cannot exceed 5 MW."""
        return m.p_discharge[t] <= BAT_power_limit
    
    model.DischargeLimit = pyo.Constraint(model.T, rule=discharge_limit_rule)
    
    # Constraint 4: Battery State of Charge (SoC) Dynamics
    def soc_dynamics_rule(m, t):
        """
        SoC changes based on charging and discharging.
        Energy = Power × Time
        """
        if t == 1:
            # First time step: start from initial SoC
            return m.soc[t] == BAT_initial_soc + dt * (m.p_charge[t] - m.p_discharge[t])
        else:
            # Subsequent time steps: update from previous SoC
            return m.soc[t] == m.soc[t-1] + dt * (m.p_charge[t] - m.p_discharge[t])
    
    model.SoCDynamics = pyo.Constraint(model.T, rule=soc_dynamics_rule,
                                      doc="Battery energy balance")
    
    # Constraint 5: Battery Capacity Limits
    def soc_min_rule(m, t):
        """Battery cannot be discharged below 0 MWh."""
        return m.soc[t] >= 0.0
    
    model.SoCMin = pyo.Constraint(model.T, rule=soc_min_rule)
    
    def soc_max_rule(m, t):
        """Battery cannot be charged above 10 MWh capacity."""
        return m.soc[t] <= BAT_capacity
    
    model.SoCMax = pyo.Constraint(model.T, rule=soc_max_rule)
    
    # ========================================================================
    # DEFINING OBJECTIVE FUNCTION
    # ========================================================================
    
    def total_cost_rule(m):
        """
        Minimize total operational cost over all time steps.
        Cost = time_duration × (generation_cost + battery_cost)
        """
        return sum(
            dt * (
                PP1_cost * m.g1[t] +           # Cost of Plant 1
                PP2_cost * m.g2[t] +           # Cost of Plant 2
                BAT_cost * m.p_charge[t] +     # Cost of charging
                BAT_cost * m.p_discharge[t]    # Cost of discharging
            )
            for t in m.T
        )
    
    model.TotalCost = pyo.Objective(rule=total_cost_rule, sense=pyo.minimize,
                                   doc="Minimize operational cost")
    
    # ========================================================================
    # SOLVING THE OPTIMIZATION PROBLEM
    # ========================================================================
    
    print("="*70)
    print("SOLVING ECONOMIC DISPATCH OPTIMIZATION")
    print("="*70)
    
    # Create solver instance
    solver = pyo.SolverFactory("glpk")  # Use GLPK LP solver
    
    # Solve the model
    result = solver.solve(model, tee=True)  # tee=True shows solver output
    
    # Check solver status
    if result.solver.status != pyo.SolverStatus.ok:
        print("\n⚠️  WARNING: Solver did not find optimal solution!")
        print(f"Solver Status: {result.solver.status}")
        return None
    
    if result.solver.termination_condition != pyo.TerminationCondition.optimal:
        print("\n⚠️  WARNING: Solution may not be optimal!")
        print(f"Termination Condition: {result.solver.termination_condition}")
    
    # ========================================================================
    # EXTRACTING AND DISPLAYING RESULTS
    # ========================================================================
    
    print("\n" + "="*70)
    print("OPTIMIZATION RESULTS")
    print("="*70)
    
    print(f"\n✅ Optimal Solution Found!")
    print(f"Total Cost: {pyo.value(model.TotalCost):.2f} €")
    
    print("\n" + "-"*70)
    print("TIME STEP SCHEDULE:")
    print("-"*70)
    print(f"{'Time':>4} {'Demand':>8} {'PP1':>8} {'PP2':>8} "
          f"{'Charge':>8} {'Disch':>8} {'SoC':>8}")
    print(f"{'':>4} {'(MW)':>8} {'(MW)':>8} {'(MW)':>8} "
          f"{'(MW)':>8} {'(MW)':>8} {'(MWh)':>8}")
    print("-"*70)
    
    for t in model.T:
        print(f"{t:4d} {pyo.value(model.demand[t]):8.2f} "
              f"{pyo.value(model.g1[t]):8.2f} {pyo.value(model.g2[t]):8.2f} "
              f"{pyo.value(model.p_charge[t]):8.2f} "
              f"{pyo.value(model.p_discharge[t]):8.2f} "
              f"{pyo.value(model.soc[t]):8.2f}")
    
    # Verify power balance
    print("\n" + "-"*70)
    print("VERIFICATION (Generation + Discharge - Charge = Demand):")
    print("-"*70)
    
    all_balanced = True
    for t in model.T:
        supply = (pyo.value(model.g1[t]) + pyo.value(model.g2[t]) + 
                 pyo.value(model.p_discharge[t]) - pyo.value(model.p_charge[t]))
        demand = pyo.value(model.demand[t])
        balanced = abs(supply - demand) < 0.001  # Numerical tolerance
        status = "✅" if balanced else "❌"
        all_balanced = all_balanced and balanced
        print(f"t={t}: Supply={supply:.2f} MW, Demand={demand:.2f} MW {status}")
    
    if all_balanced:
        print("\n✅ All time steps balanced correctly!")
    else:
        print("\n❌ WARNING: Some time steps not balanced!")
    
    # ========================================================================
    # RETURNING SOLUTION
    # ========================================================================
    
    solution = {
        'total_cost': pyo.value(model.TotalCost),
        'g1': {t: pyo.value(model.g1[t]) for t in model.T},
        'g2': {t: pyo.value(model.g2[t]) for t in model.T},
        'p_charge': {t: pyo.value(model.p_charge[t]) for t in model.T},
        'p_discharge': {t: pyo.value(model.p_discharge[t]) for t in model.T},
        'soc': {t: pyo.value(model.soc[t]) for t in model.T},
        'model': model
    }
    
    return solution


def main():
    """Main function to run the optimization."""
    solution = solve_economic_dispatch()
    
    if solution:
        print("\n" + "="*70)
        print("OPTIMIZATION COMPLETE")
        print("="*70)


if __name__ == "__main__":
    main()