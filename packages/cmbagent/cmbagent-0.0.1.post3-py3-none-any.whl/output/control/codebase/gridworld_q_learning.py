# filename: codebase/gridworld_q_learning.py
import numpy as np
import random
import os

# Set the path for saving data
database_path = "data/"
if not os.path.exists(database_path):
    os.makedirs(database_path)


class GridWorld:
    r"""
    A simple grid-world environment representing a delivery robot navigating a neighborhood.

    Grid legend:
        0: Empty cell (street)
        1: Obstacle (building) - impassable
        2: Hazard (construction site) - high penalty
        3: Goal (delivery location) - high reward

    Attributes
    ----------
    grid : np.ndarray
        2D array representing the environment.
    start_pos : tuple of int
        Starting position (row, col) of the agent.
    goal_pos : tuple of int
        Goal position (row, col).
    state_space : list of tuple
        List of all possible (row, col) positions.
    action_space : list of int
        List of possible actions: 0=up, 1=down, 2=left, 3=right.
    n_actions : int
        Number of possible actions.
    """

    def __init__(self):
        # Define a 5x5 grid
        self.grid = np.array([
            [0, 0, 0, 1, 3],
            [0, 1, 0, 1, 1],
            [0, 1, 0, 0, 0],
            [0, 0, 2, 1, 0],
            [1, 0, 0, 0, 0]
        ])
        self.n_rows, self.n_cols = self.grid.shape
        self.start_pos = (4, 0)  # bottom-left corner
        self.goal_pos = tuple(np.argwhere(self.grid == 3)[0])
        self.state_space = [(r, c) for r in range(self.n_rows) for c in range(self.n_cols)]
        self.action_space = [0, 1, 2, 3]  # up, down, left, right
        self.n_actions = len(self.action_space)
        self.reset()

    def reset(self):
        r"""
        Reset the environment to the starting state.

        Returns
        -------
        tuple of int
            The starting position (row, col).
        """
        self.agent_pos = self.start_pos
        return self.agent_pos

    def step(self, action):
        r"""
        Take an action in the environment.

        Parameters
        ----------
        action : int
            The action to take (0=up, 1=down, 2=left, 3=right).

        Returns
        -------
        next_state : tuple of int
            The new position after taking the action.
        reward : float
            The reward received after taking the action.
        done : bool
            Whether the episode has ended.
        info : dict
            Additional information (empty here).
        """
        row, col = self.agent_pos
        if action == 0:  # up
            row = max(row - 1, 0)
        elif action == 1:  # down
            row = min(row + 1, self.n_rows - 1)
        elif action == 2:  # left
            col = max(col - 1, 0)
        elif action == 3:  # right
            col = min(col + 1, self.n_cols - 1)

        # Check for obstacle
        if self.grid[row, col] == 1:
            # Hit a building, stay in place
            row, col = self.agent_pos

        self.agent_pos = (row, col)
        cell_type = self.grid[row, col]

        # Rewards
        if cell_type == 3:
            reward = 10.0  # Goal reached
            done = True
        elif cell_type == 2:
            reward = -5.0  # Hazard
            done = False
        elif (row, col) == self.agent_pos and self.grid[row, col] == 1:
            reward = -1.0  # Obstacle (should not happen due to check above)
            done = False
        else:
            reward = -1.0  # Step cost
            done = False

        if (row, col) == self.goal_pos:
            done = True

        return (row, col), reward, done, {}

    def state_to_index(self, state):
        r"""
        Convert a (row, col) state to a unique index.

        Parameters
        ----------
        state : tuple of int
            The (row, col) position.

        Returns
        -------
        int
            The index of the state.
        """
        return state[0] * self.n_cols + state[1]

    def index_to_state(self, index):
        r"""
        Convert a state index to (row, col).

        Parameters
        ----------
        index : int
            The state index.

        Returns
        -------
        tuple of int
            The (row, col) position.
        """
        return (index // self.n_cols, index % self.n_cols)


# Q-learning implementation

def q_learning(env, num_episodes=500, alpha=0.1, gamma=0.9, epsilon=0.2, max_steps=100):
    r"""
    Q-learning algorithm for the grid-world environment.

    Parameters
    ----------
    env : GridWorld
        The grid-world environment.
    num_episodes : int
        Number of episodes for training.
    alpha : float
        Learning rate (how much new information overrides old).
    gamma : float
        Discount factor (importance of future rewards).
    epsilon : float
        Exploration rate (probability of random action).
    max_steps : int
        Maximum steps per episode.

    Returns
    -------
    Q : np.ndarray
        Q-table of shape (n_states, n_actions).
    episode_rewards : list of float
        Total reward per episode.
    """
    n_states = env.n_rows * env.n_cols
    n_actions = env.n_actions
    Q = np.zeros((n_states, n_actions))
    episode_rewards = []

    for episode in range(num_episodes):
        state = env.reset()
        state_idx = env.state_to_index(state)
        total_reward = 0.0

        for step in range(max_steps):
            # Epsilon-greedy action selection
            if random.uniform(0, 1) < epsilon:
                action = random.choice(env.action_space)
            else:
                action = np.argmax(Q[state_idx, :])

            next_state, reward, done, _ = env.step(action)
            next_state_idx = env.state_to_index(next_state)

            # Q-learning update
            best_next_action = np.argmax(Q[next_state_idx, :])
            td_target = reward + gamma * Q[next_state_idx, best_next_action]
            td_error = td_target - Q[state_idx, action]
            Q[state_idx, action] += alpha * td_error

            state_idx = next_state_idx
            total_reward += reward

            if done:
                break

        episode_rewards.append(total_reward)

    return Q, episode_rewards


def save_q_table(Q, filename):
    r"""
    Save the Q-table to a .npy file.

    Parameters
    ----------
    Q : np.ndarray
        The Q-table.
    filename : str
        Path to save the file.
    """
    np.save(filename, Q)
    print("Q-table saved to " + filename)


def save_episode_rewards(rewards, filename):
    r"""
    Save the episode rewards to a .npy file.

    Parameters
    ----------
    rewards : list of float
        List of total rewards per episode.
    filename : str
        Path to save the file.
    """
    np.save(filename, rewards)
    print("Episode rewards saved to " + filename)


if __name__ == "__main__":
    # Hyperparameters with intuitive explanations:
    # alpha: learning rate (0.1) - how quickly the robot updates its knowledge (higher = faster, but less stable)
    # gamma: discount factor (0.9) - how much the robot cares about future rewards (close to 1 = long-term planning)
    # epsilon: exploration rate (0.2) - how often the robot tries new paths (higher = more exploration)
    env = GridWorld()
    Q, episode_rewards = q_learning(env, num_episodes=500, alpha=0.1, gamma=0.9, epsilon=0.2, max_steps=100)

    # Save results
    q_table_file = database_path + "q_table_gridworld.npy"
    rewards_file = database_path + "episode_rewards_gridworld.npy"
    save_q_table(Q, q_table_file)
    save_episode_rewards(episode_rewards, rewards_file)

    # Print summary
    print("Training completed for delivery robot grid-world.")
    print("Final Q-table (rounded to 2 decimals):")
    print(np.round(Q, 2))
    print("First 10 episode rewards: " + str(episode_rewards[:10]))
    print("Last 10 episode rewards: " + str(episode_rewards[-10:]))
    print("Q-table and episode rewards saved in 'data/' directory.")
