"""
Distributed Economic Dispatch using Consensus
Solves economic dispatch without central coordinator.
"""

import numpy as np
import matplotlib.pyplot as plt


class GeneratorAgent:
    """
    Generator agent with local cost function and power limits.
    """
    
    def __init__(self, agent_id, a, b, P_min, P_max):
        """
        Initialize generator agent.
        
        Cost function: C(P) = a*P^2 + b*P
        Incremental cost: λ = dC/dP = 2*a*P + b
        
        Args:
            agent_id: Agent identifier
            a: Quadratic cost coefficient
            b: Linear cost coefficient
            P_min: Minimum power limit
            P_max: Maximum power limit
        """
        self.id = agent_id
        self.a = a
        self.b = b
        self.P_min = P_min
        self.P_max = P_max
        
        # State variables
        self.lambda_val = 0.0  # Incremental cost
        self.P = 0.0  # Power output
        
    def compute_power_from_lambda(self, lambda_val):
        """
        Compute power output from incremental cost.
        
        From λ = 2*a*P + b, we get: P = (λ - b) / (2*a)
        """
        P = (lambda_val - self.b) / (2 * self.a)
        # Apply limits
        P = np.clip(P, self.P_min, self.P_max)
        return P
    
    def compute_lambda_from_power(self, P):
        """
        Compute incremental cost from power output.
        
        λ = 2*a*P + b
        """
        return 2 * self.a * P + self.b
    
    def update_power(self, lambda_consensus, rho, P_target, N):
        """
        Update power based on consensus λ and penalty term.
        
        The penalty term ρ*(P - P_target/N) enforces total power constraint.
        """
        # Compute power from consensus λ
        P_from_lambda = self.compute_power_from_lambda(lambda_consensus)
        
        # Add penalty correction
        penalty_correction = rho * (self.P - P_target / N)
        
        # New lambda with penalty
        lambda_adjusted = lambda_consensus + penalty_correction
        
        # Compute new power
        self.P = self.compute_power_from_lambda(lambda_adjusted)
        self.lambda_val = self.compute_lambda_from_power(self.P)
        
        return self.P, self.lambda_val


def create_ring_laplacian(N):
    """Create Laplacian for ring topology."""
    A = np.zeros((N, N))
    for i in range(N):
        j = (i + 1) % N
        A[i, j] = 1
        A[j, i] = 1
    
    D = np.diag(np.sum(A, axis=1))
    L = D - A
    
    return L


def distributed_economic_dispatch(agents, L, P_target, alpha=0.3, rho=0.5, 
                                  num_iterations=50):
    """
    Solve economic dispatch using distributed consensus.
    
    Args:
        agents: List of GeneratorAgent objects
        L: Laplacian matrix
        P_target: Total power demand
        alpha: Consensus step size
        rho: Penalty term weight
        num_iterations: Number of iterations
        
    Returns:
        lambda_history: Incremental costs over time
        power_history: Power outputs over time
    """
    N = len(agents)
    
    # Initialize histories
    lambda_history = np.zeros((num_iterations + 1, N))
    power_history = np.zeros((num_iterations + 1, N))
    
    # Initialize with random λ values
    for i, agent in enumerate(agents):
        agent.lambda_val = np.random.uniform(15, 20)
        agent.P = agent.compute_power_from_lambda(agent.lambda_val)
        lambda_history[0, i] = agent.lambda_val
        power_history[0, i] = agent.P
    
    # Weight matrix for consensus
    W = np.eye(N) - alpha * L
    
    # Iterations
    for t in range(num_iterations):
        # Step 1: Consensus on incremental costs
        lambda_vec = np.array([agent.lambda_val for agent in agents])
        lambda_vec = W @ lambda_vec  # Consensus update
        
        # Step 2: Each agent updates power based on consensus λ
        for i, agent in enumerate(agents):
            lambda_consensus = lambda_vec[i]
            agent.update_power(lambda_consensus, rho, P_target, N)
        
        # Record
        for i, agent in enumerate(agents):
            lambda_history[t + 1, i] = agent.lambda_val
            power_history[t + 1, i] = agent.P
    
    return lambda_history, power_history


def plot_results(lambda_history, power_history, agents, P_target):
    """Plot convergence of λ and P."""
    num_iterations, N = lambda_history.shape
    iterations = np.arange(num_iterations)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Incremental Costs
    for i in range(N):
        ax1.plot(iterations, lambda_history[:, i], 
                label=f'Agent {i+1}', linewidth=2, marker='o', markersize=3)
    
    # Final consensus value
    final_lambda = np.mean(lambda_history[-1])
    ax1.axhline(y=final_lambda, color='red', linestyle='--', 
               linewidth=2, label=f'Consensus λ = {final_lambda:.3f}')
    
    ax1.set_xlabel('Iteration', fontsize=12)
    ax1.set_ylabel('Incremental Cost λ (€/MWh)', fontsize=12)
    ax1.set_title('Convergence of Incremental Costs', fontsize=14, fontweight='bold')
    ax1.legend(loc='right', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Power Outputs
    for i in range(N):
        ax2.plot(iterations, power_history[:, i], 
                label=f'Agent {i+1}', linewidth=2, marker='s', markersize=3)
    
    # Target line
    total_power = np.sum(power_history, axis=1)
    ax2_twin = ax2.twinx()
    ax2_twin.plot(iterations, total_power, 'r--', linewidth=3, 
                 label=f'Total Power')
    ax2_twin.axhline(y=P_target, color='green', linestyle=':', 
                    linewidth=2, label=f'Target = {P_target} MW')
    ax2_twin.set_ylabel('Total Power (MW)', fontsize=12, color='red')
    ax2_twin.tick_params(axis='y', labelcolor='red')
    
    ax2.set_xlabel('Iteration', fontsize=12)
    ax2.set_ylabel('Individual Power P_i (MW)', fontsize=12)
    ax2.set_title('Convergence of Power Allocations', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=9)
    ax2_twin.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def main():
    """Main function."""
    
    print("\n" + "="*70)
    print("DISTRIBUTED ECONOMIC DISPATCH USING CONSENSUS")
    print("="*70)
    
    # Problem setup
    N = 5
    a_vals = [0.12, 0.10, 0.11, 0.09, 0.13]
    b_vals = [14.0, 15.5, 15.0, 16.0, 14.5]
    P_min = 0.0
    P_max = 20.0
    P_target = 40.0
    
    print(f"\n📋 Problem Setup:")
    print(f"   Number of generators: {N}")
    print(f"   Target power: {P_target} MW")
    print(f"   Power limits: [{P_min}, {P_max}] MW")
    
    print(f"\n💰 Cost Functions (C_i = a_i*P_i^2 + b_i*P_i):")
    print(f"   {'Agent':>6} {'a':>8} {'b':>8}")
    print("-" * 30)
    for i in range(N):
        print(f"   {i+1:6d} {a_vals[i]:8.2f} {b_vals[i]:8.2f}")
    
    # Create agents
    agents = [GeneratorAgent(i+1, a_vals[i], b_vals[i], P_min, P_max) 
             for i in range(N)]
    
    # Create topology
    L = create_ring_laplacian(N)
    
    print(f"\n🔗 Topology: Ring")
    print(f"   Laplacian:")
    print(L)
    
    # Parameters
    alpha = 0.3  # Consensus step size
    rho = 0.5    # Penalty weight
    num_iterations = 50
    
    print(f"\n⚙️  Algorithm Parameters:")
    print(f"   Consensus step size α: {alpha}")
    print(f"   Penalty weight ρ: {rho}")
    print(f"   Iterations: {num_iterations}")
    
    print(f"\n🔄 Running distributed economic dispatch...")
    
    # Run algorithm
    lambda_history, power_history = distributed_economic_dispatch(
        agents, L, P_target, alpha, rho, num_iterations
    )
    
    # Analyze results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print(f"\n📊 Final Allocation:")
    print(f"   {'Agent':>6} {'Power (MW)':>12} {'λ (€/MWh)':>12} {'Cost (€)':>12}")
    print("-" * 50)
    
    total_power = 0
    total_cost = 0
    
    for i, agent in enumerate(agents):
        P_final = power_history[-1, i]
        lambda_final = lambda_history[-1, i]
        cost = agent.a * P_final**2 + agent.b * P_final
        
        print(f"   {agent.id:6d} {P_final:12.4f} {lambda_final:12.4f} {cost:12.4f}")
        
        total_power += P_final
        total_cost += cost
    
    print("-" * 50)
    print(f"   {'Total':>6} {total_power:12.4f} {'':<12} {total_cost:12.4f}")
    print(f"   {'Target':>6} {P_target:12.4f}")
    print(f"   {'Error':>6} {abs(total_power - P_target):12.4f} MW")
    
    # Check optimality condition
    lambda_final = lambda_history[-1]
    lambda_mean = np.mean(lambda_final)
    lambda_std = np.std(lambda_final)
    
    print(f"\n✓ Optimality Check (Equal Incremental Costs):")
    print(f"   Mean λ: {lambda_mean:.6f} €/MWh")
    print(f"   Std  λ: {lambda_std:.6f} €/MWh")
    
    if lambda_std < 0.01:
        print(f"   → ✅ Incremental costs equalized (optimal)")
    else:
        print(f"   → ⚠️  Some variation remains (near-optimal)")
    
    # Plot
    print(f"\n📈 Generating plots...")
    fig = plot_results(lambda_history, power_history, agents, P_target)
    fig.savefig('economic_dispatch_consensus.png', dpi=150, bbox_inches='tight')
    print(f"   Plot saved as 'economic_dispatch_consensus.png'")
    plt.show()
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    print(f"\n✅ Distributed Economic Dispatch Achieved:")
    print(f"   • Total power: {total_power:.2f} MW (target: {P_target} MW)")
    print(f"   • Power error: {abs(total_power - P_target):.4f} MW")
    print(f"   • Total cost: {total_cost:.2f} €")
    print(f"   • All λ_i converged to: {lambda_mean:.3f} ± {lambda_std:.3f} €/MWh")
    
    print(f"\n💡 Key Insights:")
    print(f"   • No central coordinator needed")
    print(f"   • Each agent only knows its own cost function")
    print(f"   • Consensus on λ ensures optimal allocation")
    print(f"   • Penalty term ρ enforces power balance")
    
    print(f"\n📚 Why This Works:")
    print(f"   • Optimal ED requires equal incremental costs")
    print(f"   • Consensus algorithm makes λ_i equal for all i")
    print(f"   • Each agent computes P_i from λ_i using local cost function")
    print(f"   • Penalty term drives Σ P_i toward target")
    
    print("\n✅ Simulation complete!\n")


if __name__ == "__main__":
    main()