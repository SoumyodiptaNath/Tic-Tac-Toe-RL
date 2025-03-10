import pickle
import random
from sys import path
from tqdm import tqdm
from os.path import join


file_path = join(path[0], "weights_ttc.bin")


class GamePlay():
    def __init__(self) -> None:
        self.reset_board()
    
    
    def curr_state(self):
        return ''.join(self.board.values())


    def print_board(self):
        for i in range(3):
            for j in range(3):
                print(self.board[3*i + j], end=',\t')
            print('\n')
        print('#####################')
        
        
    def reset_board(self):
        self.epsilon = -1
        self.avlbl_spaces = list(range(9))
        self.curr_player = random.choice(['0', '1'])
        self.board = {pos: ' ' for pos in self.avlbl_spaces}


    def save_policy(self, states_values):
        num_states = len(list(states_values.keys()))
        print(f"\nStoring {num_states} weights at:\n{file_path}\n...")
        with open(file_path, 'wb') as f_write: pickle.dump(states_values, f_write)
        print("DONE...")


    def load_policy(self):
        try:
            with open(file_path, 'rb') as f_read: states_values = pickle.load(f_read)
            print(f"\nOpened Weights Successfully from:\n{file_path}\n...")
        
        except FileNotFoundError:
            print("\nPre-existing Weights not found...\nCreating New ones...")
            states_values = {}
        return states_values
                
    
    def check_winner(self, last_move):
        col = last_move % 3; row = last_move - col
        if self.board[row] == self.curr_player and self.board[row+1] == self.curr_player and self.board[row+2] == self.curr_player: return 1
        if self.board[col] == self.curr_player and self.board[col+3] == self.curr_player and self.board[col+6] == self.curr_player: return 1
        if self.board[0] == self.curr_player and self.board[4] == self.curr_player and self.board[8] == self.curr_player: return 1
        if self.board[2] == self.curr_player and self.board[4] == self.curr_player and self.board[6] == self.curr_player: return 1
        
        self.avlbl_spaces.remove(last_move)
        if len(self.avlbl_spaces) == 0: return 0
        self.curr_player = '0' if self.curr_player == '1' else '1'; return -1
        

    def update_states_values(self, rewards, states_values):
        for state in self.states_visited[::-1]:
            curr_vals = states_values.get(state)
            
            if curr_vals == None:
                curr_vals = 0.
                states_values[state] = curr_vals
                
            states_values[state] += self.lr*(self.gamma*rewards - curr_vals)
            rewards = states_values[state]
        
        
    def get_action(self, states_values):
        if random.random() < self.epsilon:
            action = random.choice(self.avlbl_spaces)
        
        else:
            max_val = -1e4
            for space in self.avlbl_spaces:
                self.board[space] = self.curr_player
                curr_val = states_values.get(self.curr_state())
                
                if curr_val == None: curr_val = 0.
                if curr_val > max_val: max_val = curr_val; action = space
                self.board[space] = ' '
                
        return action
            
        
    def train(self, iterns, learning_rate=0.5, decay_factor=0.9):
        self.gamma = decay_factor
        self.lr = learning_rate
        dummy_states_values = {}
        true_states_values = {}
        dummy_reward = 0.
        true_reward = 0.
        
        for i in tqdm(range(int(iterns))):
            running = True
            self.states_visited = []
            self.epsilon = 0.95 - (i/iterns)
            
            while running:
                if self.curr_player == '0': action = self.get_action(true_states_values)
                else: action = self.get_action(dummy_states_values)
                
                self.board[action] = self.curr_player
                self.states_visited.append(self.curr_state())
                result = self.check_winner(action)
                if result != -1: running = False
            
            if result == 1: 
                if self.curr_player == '0': true_reward = 1.; dummy_reward = -2.
                if self.curr_player == '1': true_reward = -2.; dummy_reward = 1.
                    
            if result == 0:
                if self.curr_player == '0': true_reward = 0.2; dummy_reward = 0.5
                if self.curr_player == '1': true_reward = 0.5; dummy_reward = 0.2
            
            self.update_states_values(dummy_reward, dummy_states_values)
            self.update_states_values(true_reward, true_states_values)
            self.reset_board()
            
        self.save_policy(true_states_values)
        del self.states_visited, self.lr, self.gamma
    
    
    def test(self, num_games):
        win_count = 0
        states_values = self.load_policy()
        
        for _ in tqdm(range(int(num_games))):
            running = True
            while running:
                if self.curr_player == '0': move = self.get_action(states_values)
                else: move = random.choice(self.avlbl_spaces)
                self.board[move] = self.curr_player
                result = self.check_winner(move)
                if result != -1: running = False
            
            if result == 1 and self.curr_player == 1: win_count += 1
            self.reset_board()
        print(win_count, num_games-win_count)
         
        
    
    

if __name__ == "__main__":
    iterns = 1e5
    G = GamePlay()
    G.train(iterns)
    G.test(iterns)

    # running = True
    # states_values = G.load_policy()
    # players_list = ["Computer", "You"]
    # G.curr_player = '0'
    
    # while running:
    #     if G.curr_player == '0': move = G.get_action(states_values)
    #     else: move = int(input("Enter Space Number: "))-1
    #     G.board[move] = G.curr_player
    #     G.print_board()
        
    #     result = G.check_winner(move)
    #     if result == 1: print(f"WINNER: {players_list[int(G.curr_player)]}!"); running = False
    #     if result == 0: print("DRAW!"); running = False
        