from ttc import GamePlay
import customtkinter as ctk
from functools import partial
from CTkMessagebox import CTkMessagebox

row_span = 2
appWidth = 480
appHeight = 420
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk, GamePlay):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        states_values = self.load_policy()
        if states_values == {}: print("\nWEIGHTS FILE NOT FOUND"); exit(0)
        self.get_action_ = partial(self.get_action, states_values)

        self.geometry(f"{appWidth}x{appHeight}")
        self.title("TIC TAC TOE GUI")
        self.resizable(0,0)
        
        self.reset()
        reset_game = ctk.CTkButton(self, text= "RESET", command = self.reset)
        reset_game.grid(row=3*row_span, column=1, rowspan=row_span,
                        padx=10, pady=10, sticky = "ew")

        

    def reset(self):
        self.reset_board()
        self.board_buttons = {}
        for i in range(3):
            for j in range(3):
                pos = 3*i + j            
                self.board_buttons[pos] = ctk.CTkButton(self, text= "", font=("Arial",30,'bold'),
                                                        command=partial(self.human_play, pos),
                                                        height=100, corner_radius=9)
                
                self.board_buttons[pos].grid(row=i*row_span, column=j, rowspan=row_span, 
                                             padx=10, pady=10, sticky="ew")

        if self.curr_player == '0':
            self.symbols = {'0': "X", '1': "O"}
            self.ai_play()
        else:
            self.symbols = {'1': "X", '0': "O"}


    def ai_play(self):
        pos = self.get_action_()
        symb = self.symbols[self.curr_player]
        self.board_buttons[pos].configure(text = f"{symb}")
        self.board[pos] = self.curr_player
        
        result = self.check_winner(pos)
        if result != -1: self.declare_winner(result)


    def human_play(self, pos):
        if pos not in self.avlbl_spaces:
            CTkMessagebox(title = "Invalid Move", message = "Already ccupied!!")
        else:
            symb = self.symbols[self.curr_player]
            self.board_buttons[pos].configure(text = f"{symb}")
            self.board[pos] = self.curr_player
            
            result = self.check_winner(pos)
            if result == -1: self.ai_play()
            else: self.declare_winner(result)


    def declare_winner(self, result):
        message = ""
        if result == 0: message = "DRAW!!!"
        elif result == 1: message = f"Winner: {self.symbols[self.curr_player]}!!"
        CTkMessagebox(title="Winner", message=message)


if __name__ == "__main__":
    app = App()
    app.mainloop()