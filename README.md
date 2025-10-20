# Tic-Tac-Toe AI Player

Challenge an unbeatable Tic-Tac-Toe opponent! This project features a sleek graphical user interface (GUI) where you can play against an AI trained using a classical Reinforcement Learning (RL) algorithm.

## 🌟 Features

* **Unbeatable AI**: The agent is trained using a Policy Iteration approach, making it an optimal player.

* **Sleek GUI**: A modern and responsive interface built with the `customtkinter` library.

* **Dynamic Gameplay**: The starting player (AI or Human) is chosen randomly for each new game.

* **Clear Feedback**: Receive instant notifications for invalid moves and game outcomes (win, lose, or draw).

## ⚙️ How It Works

The project is split into two main components:

1. **The RL Agent (`ttc.py`)**: This script contains the core `GamePlay` class, which handles the game logic. It includes the `train()` method where the agent learns by playing against itself for hundreds of thousands of episodes. The learned strategy, a dictionary mapping every possible board state to a value, is saved to a `weights_ttc.bin` file.

2. **The GUI (`tictactoe_gui.py`)**: This script creates the user interface. When launched, it loads the pre-trained `weights_ttc.bin` file. During gameplay, it uses this loaded policy to determine the AI's optimal move in any given situation.

## 🚀 Getting Started

Follow these steps to get the game up and running on your local machine.

### Prerequisites

Make sure you have Python installed. Then, install the required libraries:

```

pip install customtkinter CTkMessagebox tqdm

```

### Usage

1. **Train the Agent**:
   First, you must train the AI to generate the weights file. Run the training script from your terminal:

```

python ttc.py

```

This will create a `weights_ttc.bin` file in the same directory.

2. **Launch the Game**:
Once the training is complete, run the GUI script:

```

python tictactoe\_gui.py

```

The game window will now appear, ready for you to play!

## 📂 File Structure

```

.
├── ttc.py              \# Core game logic and RL training script
├── tictactoe\_gui.py    \# The GUI application for playing the game
└── weights\_ttc.bin     \# (Generated after training) The saved policy for the AI

```

Enjoy the challenge!
