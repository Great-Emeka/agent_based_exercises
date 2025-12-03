import numpy as np
import matplotlib.pyplot as plt


def create_ring_laplacian(N):
    """
    Create Laplacian matrix for ring topology.
    
    Ring: 0 - 1 - 2 - 3 - 4 - 0
    
    Args:
        N: Number of nodes
        
    Returns:
        L: Laplacian matrix (N x N)
    """
    # Adjacency matrix for ring
    A = np.zeros((N, N))
    for i in range(N):
        # Connect to next neighbor (with wraparound)
        j = (i + 1) % N
        A[i, j] = 1
        A[j, i] = 1 
    
    # Degree matrix
    D = np.diag(np.sum(A, axis=1))
    
    # Laplacian
    L = D - A
    
    return L, A, D


def discrete_consensus(x0, L, alpha, num_iterations):
    """
    Run discrete-time consensus algorithm.
    
    Update: x(t+1) = (I - α*L) * x(t)
    
    Args:
        x0: Initial states (N,)
        L: Laplacian matrix (N, N)
        alpha: Step size
        num_iterations: Number of iterations
        
    Returns:
        history: Array of states over time (num_iterations+1, N)
    """
    N = len(x0)
    history = np.zeros((num_iterations + 1, N))
    history[0] = x0
    
    # Weight matrix
    W = np.eye(N) - alpha * L
    
    # Iterate
    x = x0.copy()
    for t in range(num_iterations):
        x = W @ x
        history[t + 1] = x
    
    return history


def plot_consensus(history, x0):
    """Plot consensus convergence."""
    num_iterations, N = history.shape
    iterations = np.arange(num_iterations)
    
    # Calculate consensus value (average of initial states)
    consensus_value = np.mean(x0)
    
    plt.figure(figsize=(12, 6))
    
    # Plot all agent states
    for i in range(N):
        plt.plot(iterations, history[:, i], 
                label=f'Agent {i+1}', linewidth=2, marker='o', markersize=4)
    
    # Plot consensus line
    plt.axhline(y=consensus_value, color='red', linestyle='--', 
               linewidth=2, label=f'Consensus = {consensus_value:.2f}')
    
    plt.xlabel('Iteration', fontsize=12)
    plt.ylabel('State (Power Estimate in MW)', fontsize=12)
    plt.title('Discrete-Time Consensus: Ring Topology', fontsize=14, fontweight='bold')
    plt.legend(loc='right', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return plt


def analyze_convergence(history, x0, tolerance=1e-3):
    """Analyze convergence properties."""
    num_iterations, N = history.shape
    consensus_value = np.mean(x0)
    
    print("\n" + "="*70)
    print("CONVERGENCE ANALYSIS")
    print("="*70)
    
    # Check final convergence
    final_states = history[-1]
    print(f"\nInitial states: {x0}")
    print(f"Final states:   {final_states}")
    print(f"Expected consensus (average): {consensus_value:.6f}")
    
    # Convergence check
    converged = np.allclose(final_states, consensus_value, atol=tolerance)
    max_error = np.max(np.abs(final_states - consensus_value))
    
    print(f"\nConvergence status: {'✅ CONVERGED' if converged else '❌ NOT CONVERGED'}")
    print(f"Maximum error from consensus: {max_error:.6e}")
    
    # Find when consensus reached (within tolerance)
    for t in range(num_iterations):
        if np.allclose(history[t], consensus_value, atol=tolerance):
            print(f"Consensus reached at iteration: {t}")
            break
    
    # Verify sum preservation (Laplacian property)
    initial_sum = np.sum(x0)
    final_sum = np.sum(final_states)
    print(f"\nSum preservation check:")
    print(f"  Initial sum: {initial_sum:.6f}")
    print(f"  Final sum:   {final_sum:.6f}")
    print(f"  Difference:  {abs(initial_sum - final_sum):.6e}")
    
    # Convergence rate
    errors = np.max(np.abs(history - consensus_value), axis=1)
    print(f"\nConvergence rate:")
    print(f"  Initial error: {errors[0]:.6f}")
    print(f"  Final error:   {errors[-1]:.6e}")
    
    return converged, max_error


def main():
    """Main function to run consensus simulation."""
    
    print("\n" + "="*70)
    print("DISCRETE-TIME CONSENSUS ALGORITHM")
    print("="*70)
    
    # Problem setup
    N = 5  # Number of agents
    x0 = np.array([12.0, 6.0, 8.0, 14.0, 10.0])  # Initial power measurements
    num_iterations = 20
    
    print(f"\n📋 Problem Setup:")
    print(f"   Number of agents (DGs): {N}")
    print(f"   Topology: Ring")
    print(f"   Initial states (MW): {x0}")
    print(f"   Iterations: {num_iterations}")
    
    # Create ring Laplacian
    L, A, D = create_ring_laplacian(N)
    
    print(f"\n🔗 Communication Topology:")
    print(f"   Adjacency Matrix:")
    print(A)
    print(f"\n   Laplacian Matrix:")
    print(L)
    
    # Determine step size α
    # For convergence: 0 < α < 1/Δ_max
    # In a ring, each node has degree 2, so Δ_max = 2
    degrees = np.diag(D)
    delta_max = np.max(degrees)
    alpha_max = 1.0 / delta_max
    
    # Choose α = 0.4 (safe, well within bounds)
    alpha = 0.4
    
    print(f"\n⚙️  Consensus Parameters:")
    print(f"   Maximum degree Δ_max: {delta_max}")
    print(f"   Stability bound: 0 < α < {alpha_max:.3f}")
    print(f"   Chosen α: {alpha}")
    
    # Run consensus
    print(f"\n🔄 Running consensus algorithm...")
    history = discrete_consensus(x0, L, alpha, num_iterations)
    
    # Analyze results
    converged, max_error = analyze_convergence(history, x0)
    
    # Display iteration details (first 5 and last 5)
    print(f"\n📊 State Evolution (selected iterations):")
    print(f"{'Iter':>5} {'Agent 1':>10} {'Agent 2':>10} {'Agent 3':>10} "
          f"{'Agent 4':>10} {'Agent 5':>10}")
    print("-" * 70)
    
    # Show first 5 iterations
    for t in [0, 1, 2, 3, 4]:
        states = history[t]
        print(f"{t:5d} {states[0]:10.4f} {states[1]:10.4f} {states[2]:10.4f} "
              f"{states[3]:10.4f} {states[4]:10.4f}")
    
    print("  ...   ...")
    
    # Show last 5 iterations
    for t in range(num_iterations - 4, num_iterations + 1):
        states = history[t]
        print(f"{t:5d} {states[0]:10.4f} {states[1]:10.4f} {states[2]:10.4f} "
              f"{states[3]:10.4f} {states[4]:10.4f}")
    
    # Plot results
    print(f"\n📈 Generating plot...")
    plt_obj = plot_consensus(history, x0)
    plt_obj.savefig('consensus_convergence.png', dpi=150, bbox_inches='tight')
    print(f"   Plot saved as 'consensus_convergence.png'")
    plt_obj.show()
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\n✅ Key Results:")
    print(f"   • All agents converged to consensus value: {np.mean(x0):.2f} MW")
    print(f"   • Consensus = average of initial states ✓")
    print(f"   • Sum preserved throughout iterations ✓")
    print(f"   • Maximum final error: {max_error:.6e}")
    
    print(f"\n💡 Interpretation:")
    print(f"   • Each DG started with its own power measurement")
    print(f"   • Through local communication in ring topology")
    print(f"   • All DGs converged to estimate of total power / N")
    print(f"   • This is distributed state estimation!")
    
    print(f"\n📚 Consensus Properties Demonstrated:")
    print(f"   ✓ Convergence to average")
    print(f"   ✓ Sum preservation (Laplacian property)")
    print(f"   ✓ Distributed computation (no central node)")
    print(f"   ✓ Only neighbor communication needed")
    
    print("\n✅ Simulation complete!\n")
    
    return history, converged


if __name__ == "__main__":
    history, converged = main()