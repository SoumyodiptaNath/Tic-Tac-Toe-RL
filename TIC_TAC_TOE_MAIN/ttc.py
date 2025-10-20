import pickle  # Used to save and load the learned policy (the state-value dictionary)
import random  # Used for epsilon-greedy exploration and random player starts
from sys import path
from tqdm import tqdm  # Provides a progress bar for training loops
from os.path import join


# Define the file path for storing the learned weights
file_path = join(path[0], "weights_ttc.bin")


class GamePlay():
    def __init__(self) -> None:
        """Initializes the game environment."""
        self.reset_board()

    def curr_state(self):
        """
        Returns the current board state as a unique string.
        This string (e.g., ' 01 10 ') is used as the key in the state-value dictionary.
        """
        return ''.join(self.board.values())

    def print_board(self):
        """Utility function to print the current board to the console."""
        for i in range(3):
            for j in range(3):
                print(self.board[3*i + j], end=',\t')
            print('\n')
        print('#####################')

    def reset_board(self):
        """Resets the game to an empty state for a new episode."""
        self.epsilon = -1  # Epsilon (exploration rate) will be set by the train() method
        self.avlbl_spaces = list(range(9))  # List of available (empty) board positions
        self.curr_player = random.choice(['0', '1'])  # Randomly choose which player starts
        self.board = {pos: ' ' for pos in self.avlbl_spaces}  # Board state as a dictionary

    def save_policy(self, states_values):
        """Saves the trained state-value dictionary to a file using pickle."""
        num_states = len(list(states_values.keys()))
        print(f"\nStoring {num_states} weights at:\n{file_path}\n...")
        with open(file_path, 'wb') as f_write:
            pickle.dump(states_values, f_write)
        print("DONE...")

    def load_policy(self):
        """Loads a pre-trained policy from a file. If not found, initializes an empty one."""
        try:
            with open(file_path, 'rb') as f_read:
                states_values = pickle.load(f_read)
            print(f"\nOpened Weights Successfully from:\n{file_path}\n...")

        except FileNotFoundError:
            print("\nPre-existing Weights not found...\nCreating New ones...")
            states_values = {}
        return states_values

    def check_winner(self, last_move):
        """
        Checks if the last move resulted in a win, draw, or if the game continues.
        Returns:
            1: The current player won
            0: The game is a draw
           -1: The game continues
        """
        # Efficiently check only the row, column, and diagonals related to the last move
        col = last_move % 3
        row = last_move - col
        # Check row
        if self.board[row] == self.curr_player and self.board[row+1] == self.curr_player and self.board[row+2] == self.curr_player:
            return 1
        # Check column
        if self.board[col] == self.curr_player and self.board[col+3] == self.curr_player and self.board[col+6] == self.curr_player:
            return 1
        # Check main diagonal
        if self.board[0] == self.curr_player and self.board[4] == self.curr_player and self.board[8] == self.curr_player:
            return 1
        # Check anti-diagonal
        if self.board[2] == self.curr_player and self.board[4] == self.curr_player and self.board[6] == self.curr_player:
            return 1

        self.avlbl_spaces.remove(last_move)
        if len(self.avlbl_spaces) == 0:
            return 0  # Game is a draw

        # If no win or draw, switch players and continue
        self.curr_player = '0' if self.curr_player == '1' else '1'
        return -1

    def update_states_values(self, rewards, states_values):
        """
        Performs the core value function update.
        This iterates backward through all states visited in the episode and applies
        a Bellman-like update to propagate the final reward.
        """
        # Iterate backwards from the last state to the first
        for state in self.states_visited[::-1]:
            curr_vals = states_values.get(state)

            if curr_vals is None:
                curr_vals = 0.  # Initialize the value of this state if never seen before
                states_values[state] = curr_vals

            # Value update formula: V(s) = V(s) + lr * (gamma * V(s_next) - V(s))
            # Here, 'rewards' is effectively V(s_next) from the previous (backward) iteration
            states_values[state] += self.lr*(self.gamma*rewards - curr_vals)
            
            # The current state's new value becomes the "next state's value" for the move that came before it
            rewards = states_values[state]

    def get_action(self, states_values):
        """
        Selects an action based on the current policy (epsilon-greedy).
        """
        # Epsilon-greedy: Explore
        if random.random() < self.epsilon:
            action = random.choice(self.avlbl_spaces)  # Choose a random available move
        
        # Epsilon-greedy: Exploit
        else:
            max_val = -1e4
            # Iterate through all possible next moves
            for space in self.avlbl_spaces:
                self.board[space] = self.curr_player  # 1. Simulate the move
                curr_val = states_values.get(self.curr_state())  # 2. Get the value of the resulting state
                
                if curr_val is None:
                    curr_val = 0.  # Treat unseen states as neutral

                if curr_val > max_val:
                    max_val = curr_val
                    action = space  # This is the best move found so far
                
                self.board[space] = ' '  # 3. Undo the simulated move
                
        return action

    def train(self, iterns, learning_rate=0.5, decay_factor=0.9):
        """Trains the agent using self-play."""
        self.gamma = decay_factor  # Discount factor for future rewards
        self.lr = learning_rate  # Learning rate
        
        # Player '0' is the agent we are training (true_states_values)
        # Player '1' is a "dummy" opponent that also learns (dummy_states_values)
        # This is a form of self-play.
        dummy_states_values = {}
        true_states_values = {}
        dummy_reward = 0.
        true_reward = 0.

        # Run for a fixed number of episodes (games)
        for i in tqdm(range(int(iterns))):
            running = True
            self.states_visited = []  # Track all states visited in this episode
            # Epsilon decays linearly from 0.95 down to ~0
            self.epsilon = 0.95 - (i/iterns)

            # --- Start of a single episode (one game) ---
            while running:
                # Both players use an epsilon-greedy policy based on their own value functions
                if self.curr_player == '0':
                    action = self.get_action(true_states_values)
                else:
                    action = self.get_action(dummy_states_values)

                self.board[action] = self.curr_player
                self.states_visited.append(self.curr_state())  # Record the state *after* the move
                result = self.check_winner(action)
                
                if result != -1:
                    running = False  # Game over (win or draw)
            # --- End of a single episode ---

            # Assign final rewards based on the game outcome
            if result == 1:  # A player won
                if self.curr_player == '0':
                    true_reward = 1.
                    dummy_reward = -2.  # Penalize the loser more
                if self.curr_player == '1':
                    true_reward = -2.
                    dummy_reward = 1.

            if result == 0:  # The game was a draw
                # Assign small positive rewards for a draw
                if self.curr_player == '0':
                    true_reward = 0.2
                    dummy_reward = 0.5
                if self.curr_player == '1':
                    true_reward = 0.5
                    dummy_reward = 0.2

            # Backpropagate the rewards to update the value functions for both players
            self.update_states_values(dummy_reward, dummy_states_values)
            self.update_states_values(true_reward, true_states_values)
            
            self.reset_board()  # Prepare for the next episode

        self.save_policy(true_states_values)  # Save the policy for our main agent ('0')
        del self.states_visited, self.lr, self.gamma  # Clean up

    def test(self, num_games):
        """Tests the trained policy against an opponent that plays randomly."""
        win_count = 0
        states_values = self.load_policy()  # Load the trained policy for player '0'
        self.epsilon = -1  # Disable exploration (pure exploitation)

        for _ in tqdm(range(int(num_games))):
            running = True
            while running:
                if self.curr_player == '0':
                    move = self.get_action(states_values)  # Agent '0' uses its learned policy
                else:
                    move = random.choice(self.avlbl_spaces)  # Agent '1' plays randomly
                
                self.board[move] = self.curr_player
                result = self.check_winner(move)
                if result != -1:
                    running = False

            # This condition seems to be checking for wins by player '1' (the int)
            # You might want to change this to `self.curr_player == '0'` to count agent wins
            if result == 1 and self.curr_player == 1:
                win_count += 1
            self.reset_board()
            
        print(win_count, num_games-win_count)


if __name__ == "__main__":
    iterns = 1e5
    G = GamePlay()
    
    # Train the agent
    G.train(iterns)
    
    # Test the agent against a random opponent
    G.test(iterns)

    # --- Uncomment this block to play against the trained agent ---
    # running = True
    # states_values = G.load_policy()
    # G.epsilon = -1  # Make sure the agent doesn't explore
    # players_list = ["Computer", "You"]
    # G.curr_player = '0'  # Let the computer (Agent '0') start
    # G.print_board()

    # while running:
    #     if G.curr_player == '0':
    #         print("Computer's turn...")
    #         move = G.get_action(states_values)
    #     else:
    #         move = int(input("Enter Space Number (1-9): "))-1
        
    #     if move not in G.avlbl_spaces:
    #         print("Invalid move. Try again.")
    #         continue
            
    #     G.board[move] = G.curr_player
    #     G.print_board()
        
    #     result = G.check_winner(move)
    #     if result == 1:
    #         print(f"WINNER: {players_list[int(G.curr_player)]}!")
    #         running = False
    #     if result == 0:
    #         print("DRAW!")
    #         running = False
