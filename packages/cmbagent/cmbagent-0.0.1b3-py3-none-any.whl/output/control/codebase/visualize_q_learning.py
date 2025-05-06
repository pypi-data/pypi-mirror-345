# filename: codebase/visualize_q_learning.py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import os
from matplotlib import rcParams

from codebase.gridworld_q_learning import GridWorld

# Set LaTeX rendering and font
rcParams['text.usetex'] = True
rcParams['font.family'] = 'serif'

database_path = "data/"
q_table_file = database_path + "q_table_gridworld.npy"
rewards_file = database_path + "episode_rewards_gridworld.npy"

# Load Q-table and rewards
Q = np.load(q_table_file)
episode_rewards = np.load(rewards_file)

env = GridWorld()

def plot_learning_curve(episode_rewards, save_path):
    r"""
    Plot the learning curve (total reward per episode).

    Parameters
    ----------
    episode_rewards : list or np.ndarray
        Total reward per episode.
    save_path : str
        Path to save the plot.
    """
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(episode_rewards, color='tab:blue', linewidth=1)
    ax.set_xlabel(r'Episode', fontsize=13)
    ax.set_ylabel(r'Total reward', fontsize=13)
    ax.set_title(r'Learning Curve: Total Reward per Episode', fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.relim()
    ax.autoscale_view()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close(fig)
    print(r"Learning curve plot saved: " + save_path)
    print(r"This plot shows the total reward the agent received in each episode, indicating learning progress.")


def plot_policy(Q, env, save_path):
    r"""
    Visualize the grid-world and the learned policy (arrows for best action).

    Parameters
    ----------
    Q : np.ndarray
        Q-table.
    env : GridWorld
        The environment.
    save_path : str
        Path to save the plot.
    """
    n_rows, n_cols = env.n_rows, env.n_cols
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-0.5, n_cols - 0.5)
    ax.set_ylim(-0.5, n_rows - 0.5)
    ax.set_xticks(np.arange(-0.5, n_cols, 1))
    ax.set_yticks(np.arange(-0.5, n_rows, 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(True, which='both', color='gray', linewidth=1, alpha=0.5)

    # Draw grid cells
    for r in range(n_rows):
        for c in range(n_cols):
            cell = env.grid[r, c]
            if cell == 1:
                rect = patches.Rectangle((c-0.5, n_rows-1-r-0.5), 1, 1, linewidth=0, edgecolor=None, facecolor='black', alpha=0.7)
                ax.add_patch(rect)
            elif cell == 2:
                rect = patches.Rectangle((c-0.5, n_rows-1-r-0.5), 1, 1, linewidth=0, edgecolor=None, facecolor='orange', alpha=0.5)
                ax.add_patch(rect)
            elif cell == 3:
                rect = patches.Rectangle((c-0.5, n_rows-1-r-0.5), 1, 1, linewidth=0, edgecolor=None, facecolor='green', alpha=0.5)
                ax.add_patch(rect)
            if (r, c) == env.start_pos:
                ax.text(c, n_rows-1-r, r'S', ha='center', va='center', fontsize=16, color='blue', fontweight='bold')
            if (r, c) == env.goal_pos:
                ax.text(c, n_rows-1-r, r'G', ha='center', va='center', fontsize=16, color='darkgreen', fontweight='bold')

    # Draw policy arrows
    action_arrows = {0: (0, 0.3), 1: (0, -0.3), 2: (-0.3, 0), 3: (0.3, 0)}
    for r in range(n_rows):
        for c in range(n_cols):
            if env.grid[r, c] == 1 or env.grid[r, c] == 3:
                continue
            idx = env.state_to_index((r, c))
            best_action = np.argmax(Q[idx])
            dx, dy = action_arrows[best_action]
            ax.arrow(c, n_rows-1-r, dx, dy, head_width=0.15, head_length=0.15, fc='k', ec='k')

    ax.set_title(r'Learned Policy: Arrows Indicate Best Action', fontsize=14)
    ax.relim()
    ax.autoscale_view()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close(fig)
    print(r"Policy visualization saved: " + save_path)
    print(r"This plot shows the grid-world with obstacles (black), hazards (orange), goal (green), start (S), and arrows for the best action in each state.")


def plot_q_values(Q, env, save_path):
    r"""
    Visualize the Q-values for each state-action pair as a heatmap.

    Parameters
    ----------
    Q : np.ndarray
        Q-table.
    env : GridWorld
        The environment.
    save_path : str
        Path to save the plot.
    """
    n_rows, n_cols = env.n_rows, env.n_cols
    fig, axes = plt.subplots(1, 4, figsize=(16, 5))
    action_names = [r'up', r'down', r'left', r'right']
    for a in range(4):
        q_grid = np.zeros((n_rows, n_cols))
        for r in range(n_rows):
            for c in range(n_cols):
                idx = env.state_to_index((r, c))
                q_grid[r, c] = Q[idx, a]
        im = axes[a].imshow(q_grid, cmap='coolwarm', origin='upper')
        axes[a].set_title(r'Q-values: ' + action_names[a], fontsize=13)
        axes[a].set_xticks([])
        axes[a].set_yticks([])
        fig.colorbar(im, ax=axes[a], fraction=0.046, pad=0.04)
    plt.suptitle(r'Q-values for Each Action', fontsize=15)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    for ax in axes:
        ax.relim()
        ax.autoscale_view()
    plt.savefig(save_path, dpi=300)
    plt.close(fig)
    print(r"Q-value heatmaps saved: " + save_path)
    print(r"Each subplot shows the Q-values for a specific action (up, down, left, right) across the grid.")


def interactive_demo(Q, env, save_path):
    r"""
    Create an interactive demonstration (animation) of the agent's path using the learned Q-table.

    Parameters
    ----------
    Q : np.ndarray
        Q-table.
    env : GridWorld
        The environment.
    save_path : str
        Path to save the animation (as .mp4).
    """
    n_rows, n_cols = env.n_rows, env.n_cols
    path = []
    state = env.start_pos
    path.append(state)
    max_steps = 50
    for _ in range(max_steps):
        idx = env.state_to_index(state)
        action = np.argmax(Q[idx])
        next_state, _, done, _ = env.step(action)
        path.append(next_state)
        if done:
            break
        state = next_state

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-0.5, n_cols - 0.5)
    ax.set_ylim(-0.5, n_rows - 0.5)
    ax.set_xticks(np.arange(-0.5, n_cols, 1))
    ax.set_yticks(np.arange(-0.5, n_rows, 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(True, which='both', color='gray', linewidth=1, alpha=0.5)

    # Draw static grid
    for r in range(n_rows):
        for c in range(n_cols):
            cell = env.grid[r, c]
            if cell == 1:
                rect = patches.Rectangle((c-0.5, n_rows-1-r-0.5), 1, 1, linewidth=0, edgecolor=None, facecolor='black', alpha=0.7)
                ax.add_patch(rect)
            elif cell == 2:
                rect = patches.Rectangle((c-0.5, n_rows-1-r-0.5), 1, 1, linewidth=0, edgecolor=None, facecolor='orange', alpha=0.5)
                ax.add_patch(rect)
            elif cell == 3:
                rect = patches.Rectangle((c-0.5, n_rows-1-r-0.5), 1, 1, linewidth=0, edgecolor=None, facecolor='green', alpha=0.5)
                ax.add_patch(rect)
            if (r, c) == env.start_pos:
                ax.text(c, n_rows-1-r, r'S', ha='center', va='center', fontsize=16, color='blue', fontweight='bold')
            if (r, c) == env.goal_pos:
                ax.text(c, n_rows-1-r, r'G', ha='center', va='center', fontsize=16, color='darkgreen', fontweight='bold')

    agent_marker, = ax.plot([], [], 'o', color='red', markersize=18, label='Agent')
    path_line, = ax.plot([], [], '-', color='red', linewidth=2, alpha=0.5)

    def init():
        agent_marker.set_data([], [])
        path_line.set_data([], [])
        return agent_marker, path_line

    def animate(i):
        y = [n_rows-1-s[0] for s in path[:i+1]]
        x = [s[1] for s in path[:i+1]]
        agent_marker.set_data([x[-1]], [y[-1]])
        path_line.set_data(x, y)
        return agent_marker, path_line

    ani = animation.FuncAnimation(fig, animate, frames=len(path), init_func=init, blit=True, interval=600, repeat=False)
    ani.save(save_path, writer='ffmpeg', dpi=300)
    plt.close(fig)
    print(r"Interactive agent path animation saved: " + save_path)
    print(r"This animation shows the agent's step-by-step path from start to goal using the learned policy.")


if __name__ == "__main__":
    import time
    timestamp = str(int(time.time()))

    # Plot learning curve
    plot_learning_curve(
        episode_rewards,
        database_path + "learning_curve_1_" + timestamp + ".png"
    )

    # Plot learned policy
    plot_policy(
        Q, env,
        database_path + "policy_arrows_2_" + timestamp + ".png"
    )

    # Plot Q-values heatmaps
    plot_q_values(
        Q, env,
        database_path + "q_values_heatmap_3_" + timestamp + ".png"
    )

    # Interactive demonstration (animation)
    interactive_demo(
        Q, env,
        database_path + "agent_path_demo_4_" + timestamp + ".mp4"
    )
