# Import the backend game logic from your other file
from ttc import GamePlay
# Import the custom tkinter library for modern UI elements
import customtkinter as ctk
# Used to create a simplified version of the get_action function
from functools import partial
# A custom message box for a better look and feel
from CTkMessagebox import CTkMessagebox

# --- Global UI Constants ---
row_span = 2  # A layout helper, can likely be removed if not used extensively
appWidth = 480
appHeight = 420

# --- UI Theme and Appearance Setup ---
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Sets the color for widgets like buttons


class App(ctk.CTk, GamePlay):
    """
    Main application class.
    Inherits from ctk.CTk to become the main window.
    Inherits from GamePlay to get all the tic-tac-toe logic and AI functions.
    """
    def __init__(self, *args, **kwargs):
        # Initialize both parent classes
        super().__init__(*args, **kwargs)

        # --- Load the Trained AI Policy ---
        states_values = self.load_policy()
        if not states_values:  # Check if the dictionary is empty
            print("\nWEIGHTS FILE (weights_ttc.bin) NOT FOUND. CANNOT START.")
            exit(0)
        
        # Pre-load the get_action method with the learned state values.
        # This simplifies calling the AI's move selection later.
        self.get_action_ = partial(self.get_action, states_values)

        # --- Main Window Configuration ---
        self.geometry(f"{appWidth}x{appHeight}")
        self.title("TIC TAC TOE - AI Player")
        self.resizable(False, False)  # Prevent window resizing

        # Create the initial game board and the reset button
        self.reset()
        reset_game = ctk.CTkButton(self, text="RESET", command=self.reset)
        reset_game.grid(row=3*row_span, column=1, rowspan=row_span,
                        padx=10, pady=10, sticky="ew")

    def reset(self):
        """Resets the game to its initial state."""
        # Call the reset_board from the GamePlay parent class to reset the backend
        self.reset_board()
        self.board_buttons = {}

        # --- Dynamically Create the 3x3 Grid of Buttons ---
        for i in range(3):
            for j in range(3):
                pos = 3*i + j  # Calculate button position (0-8)
                # Create a button for each board position
                self.board_buttons[pos] = ctk.CTkButton(
                    self,
                    text="",  # Initially empty
                    font=("Arial", 30, 'bold'),
                    # `partial` passes the specific button's `pos` to the human_play method on click
                    command=partial(self.human_play, pos),
                    height=100,
                    corner_radius=9
                )
                # Place the button in the grid layout
                self.board_buttons[pos].grid(row=i*row_span, column=j, rowspan=row_span,
                                             padx=10, pady=10, sticky="ew")

        # --- Determine Symbols and Handle AI's First Move ---
        if self.curr_player == '0':  # AI ('0') starts the game
            self.symbols = {'0': "X", '1': "O"}  # AI is 'X', Human is 'O'
            self.ai_play()  # Let the AI make the first move
        else:  # Human ('1') starts the game
            self.symbols = {'1': "X", '0': "O"}  # Human is 'X', AI is 'O'

    def ai_play(self):
        """Handles the AI's turn."""
        pos = self.get_action_()  # Get the best move from the loaded policy
        symb = self.symbols[self.curr_player]

        # Update the button text and disable it to prevent clicks
        self.board_buttons[pos].configure(text=f"{symb}", state="disabled")
        self.board[pos] = self.curr_player  # Update the internal board state

        # Check if the AI's move ended the game
        result = self.check_winner(pos)
        if result != -1:  # -1 means the game continues
            self.declare_winner(result)

    def human_play(self, pos):
        """Handles the human player's turn when a button is clicked."""
        # Check if the chosen spot is already taken
        if pos not in self.avlbl_spaces:
            CTkMessagebox(title="Invalid Move", message="This spot is already taken!")
        else:
            symb = self.symbols[self.curr_player]
            
            # Update the button text and disable it
            self.board_buttons[pos].configure(text=f"{symb}", state="disabled")
            self.board[pos] = self.curr_player  # Update internal board state

            # Check if the human's move ended the game
            result = self.check_winner(pos)
            if result == -1:  # If the game is not over, it's the AI's turn
                self.ai_play()
            else:
                self.declare_winner(result)

    def declare_winner(self, result):
        """Displays the game over message."""
        message = ""
        if result == 0:
            message = "IT'S A DRAW!"
        elif result == 1:
            winner_symbol = self.symbols[self.curr_player]
            message = f"WINNER: {winner_symbol}!"
        
        # Show a message box with the result
        CTkMessagebox(title="Game Over", message=message, icon="check")
        
        # Disable all buttons to end the game
        for button in self.board_buttons.values():
            button.configure(state="disabled")


if __name__ == "__main__":
    # Create an instance of the App class
    app = App()
    # Start the application's main event loop
    app.mainloop()
