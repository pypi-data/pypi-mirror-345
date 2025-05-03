class Game:
    codes = [
        '''
import random

payoffs = {
    ("C", "C"): (3, 3),
    ("C", "D"): (0, 5),
    ("D", "C"): (5, 0),
    ("D", "D"): (1, 1)
}

def strategy(name, my_hist, opp_hist):
    if name == "Cooperate": return "C"
    if name == "Defect": return "D"
    if name == "TitForTat": return "C" if not opp_hist else opp_hist[-1]
    if name == "Grim": return "D" if "D" in opp_hist else "C"
    if name == "Random": return random.choice(["C", "D"])

def play(s1, s2, rounds=10):
    h1, h2, score1, score2 = [], [], 0, 0
    for _ in range(rounds):
        m1, m2 = strategy(s1, h1, h2), strategy(s2, h2, h1)
        h1.append(m1), h2.append(m2)
        p1, p2 = payoffs[(m1, m2)]
        score1 += p1; score2 += p2
        print(f"P1: {m1}, P2: {m2} → {p1}, {p2}")
    print(f"Total: P1={score1}, P2={score2}")

def find_nash_equilibria():
    strategies = ["C", "D"]
    nash_equilibria = []

    for s1 in strategies:
        for s2 in strategies:
            p1, p2 = payoffs[(s1, s2)]

            best_response_p1 = max([payoffs[(alt, s2)][0] for alt in strategies])
            p1_is_best = p1 == best_response_p1

            best_response_p2 = max([payoffs[(s1, alt)][1] for alt in strategies])
            p2_is_best = p2 == best_response_p2

            if p1_is_best and p2_is_best:
                nash_equilibria.append(((s1, s2), (p1, p2)))

    print("Nash Equilibrium(s):")
    for (s1, s2), (p1, p2) in nash_equilibria:
        print(f"Strategy: P1={s1}, P2={s2} → Payoff: ({p1}, {p2})")

play("TitForTat", "Grim", 10)
print("\nAnalyzing Nash Equilibrium in payoff matrix:")
find_nash_equilibria()
        ''',
        '''
import random
import math

class TicTacToe:
    def __init__(self, size=3):
        self.size = size
        self.board = [[" " for _ in range(size)] for _ in range(size)]
        self.current_winner = None

    def print_board(self):
        for row in self.board:
            print("| " + " | ".join(row) + " |")
        print()

    def available_moves(self):
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.board[r][c] == " "]

    def make_move(self, row, col, player):
        if self.board[row][col] == " ":
            self.board[row][col] = player
            if self.check_winner(row, col, player):
                self.current_winner = player
            return True
        return False

    def check_winner(self, row, col, player):
        line = [player] * self.size
        return (
            all(self.board[row][i] == player for i in range(self.size)) or
            all(self.board[i][col] == player for i in range(self.size)) or
            all(self.board[i][i] == player for i in range(self.size)) or
            all(self.board[i][self.size - 1 - i] == player for i in range(self.size))
        )

    def is_full(self):
        return not any(" " in row for row in self.board)

# --- AI strategies ---

def minimax(game, player, depth=0, max_player="X", min_player="O"):
    if game.current_winner == max_player:
        return 1
    elif game.current_winner == min_player:
        return -1
    elif game.is_full():
        return 0

    if player == max_player:
        best = -math.inf
        for (r, c) in game.available_moves():
            game.make_move(r, c, player)
            score = minimax(game, min_player, depth+1, max_player, min_player)
            game.board[r][c] = " "
            game.current_winner = None
            best = max(best, score)
        return best
    else:
        best = math.inf
        for (r, c) in game.available_moves():
            game.make_move(r, c, player)
            score = minimax(game, max_player, depth+1, max_player, min_player)
            game.board[r][c] = " "
            game.current_winner = None
            best = min(best, score)
        return best

def best_move(game, player):
    if game.size == 3:
        best_score = -math.inf
        move = None
        for (r, c) in game.available_moves():
            game.make_move(r, c, player)
            score = minimax(game, "O" if player == "X" else "X")
            game.board[r][c] = " "
            game.current_winner = None
            if score > best_score:
                best_score = score
                move = (r, c)
        return move
    else:
        return random.choice(game.available_moves())

def play_game(size=3):
    game = TicTacToe(size)
    player_turn = "X"

    while True:
        game.print_board()
        if player_turn == "X":
            r, c = best_move(game, "X")
        else:
            moves = game.available_moves()
            print(f"Available: {moves}")
            r, c = map(int, input("Enter row col (e.g. 1 1): ").split())

        if game.make_move(r, c, player_turn):
            if game.current_winner:
                game.print_board()
                print(f"{player_turn} wins!")
                break
            elif game.is_full():
                game.print_board()
                print("Draw!")
                break
            player_turn = "O" if player_turn == "X" else "X"
        else:
            print("Invalid move. Try again.")

play_game(size=3)
        ''',
        '''
import numpy as np
import pandas as pd

def create_rps():
    A = np.array([[ 0, -1,  1],
                  [ 1,  0, -1],
                  [-1, 1,  0]])
    B = -A
    return A, B

def find_psne(matrix_A, matrix_B):
    psne = []
    for i in range(matrix_A.shape[0]):
        for j in range(matrix_A.shape[1]):
            a_best = matrix_A[i, j] >= max(matrix_A[i, :])
            b_best = matrix_B[i, j] >= max(matrix_B[:, j])
            if a_best and b_best:
                psne.append((i, j))
    return psne

A, B = create_rps()
psne = find_psne(A, B)
print("Rock-Paper-Scissors PSNE:", psne if psne else "No PSNE found")

def check_psne(matrix_A, matrix_B):
    psne = []
    for i in range(matrix_A.shape[0]):
        for j in range(matrix_A.shape[1]):
            a_best = matrix_A[i, j] >= max(matrix_A[i, :])
            b_best = matrix_B[i, j] >= max(matrix_B[:, j])
            if a_best and b_best:
                psne.append((i, j))
    return psne

def modify_payoff_matrix():
    modified_A = np.array([[3, 1], [0, 2]])
    modified_B = np.array([[3, 0], [1, 2]])
    return modified_A, modified_B

A_mod, B_mod = modify_payoff_matrix()
psne_mod = check_psne(A_mod, B_mod)
print("Modified Matrix PSNE(s):", psne_mod if psne_mod else "No PSNE Found")

def load_dataset():
    data = pd.DataFrame({
        'Strategy_A': ['High', 'Low', 'Medium', 'High'],
        'Strategy_B': ['Low', 'High', 'Medium', 'Low'],
        'Payoff_A': [5, 2, 3, 4],
        'Payoff_B': [3, 4, 2, 5]
    })
    return data

def find_psne_from_dataset(df):
    psne_list = []

    unique_A = df['Strategy_A'].unique()
    unique_B = df['Strategy_B'].unique()

    for a in unique_A:
        for b in unique_B:
            sub_df = df[(df['Strategy_A'] == a) & (df['Strategy_B'] == b)]
            if sub_df.empty:
                continue
            print("\n",sub_df)

            payoff_a = sub_df['Payoff_A'].values[0]
            payoff_b = sub_df['Payoff_B'].values[0]

            a_row = df[df['Strategy_A'] == a]
            b_col = df[df['Strategy_B'] == b]

            best_a = payoff_a >= a_row['Payoff_A'].max()
            best_b = payoff_b >= b_col['Payoff_B'].max()

            if best_a and best_b:
                psne_list.append((a, b))

    return psne_list

dataset = load_dataset()
print("\nDataset:\n", dataset)

psne_dataset = find_psne_from_dataset(dataset)
print("Dataset PSNE(s):", psne_dataset if psne_dataset else "No PSNE found in dataset")
        ''',
        '''
import numpy as np
import sympy as sp

U_p1 = np.array([[3,1],[4,2]])
U_p2 = np.array([[2,4],[1,3]])

p, q = sp.symbols('p q')

p1_A = q*U_p1[0,0]+(1-q)*U_p2[0,1]
p1_B = q*U_p1[1,0]+(1-q)*U_p1[1,1]

p2_A = p*U_p2[0,0]+(1-p)*U_p2[1,0]
p2_B = p*U_p1[0,1]+(1-p)*U_p1[1,1]

sol = sp.solve([p1_A - p1_B, p2_A - p2_B], (p,q))
print('Mixed strategy nash equi:', sol)
        ''',
        '''
import numpy as np

payoff_A = np.array([[3, 1], [0, 2]])
payoff_B = np.array([[2, 4], [1, 3]])

maxmin_A = np.max(np.min(payoff_A, axis=1))

minmax_B = np.min(np.max(payoff_B, axis=0))

saddle_point = maxmin_A if maxmin_A == minmax_B else None

print(f"Maxmin (Player A): {maxmin_A}")
print(f"Minmax (Player B): {minmax_B}")

if saddle_point is not None:
    print(f"Saddle Point: {saddle_point}")
else:
    print("No Saddle Point")
        ''',
        '''
import numpy as np

payoff_A_reliable = np.array([5, 1])
payoff_A_unreliable = np.array([2, 4])

payoff_B = np.array([[6, 2], [3, 1]])

belief_A_reliable = 0.7
belief_A_unreliable = 0.3

belief_B_reliable = 0.7
belief_B_unreliable = 0.3

def expected_payoff_A(strategy_A, strategy_B):
    payoff_A = belief_A_reliable * payoff_A_reliable[strategy_A] + belief_A_unreliable * payoff_A_unreliable[strategy_A]
    payoff_B_val = payoff_B[strategy_B, strategy_A]
    return payoff_A - payoff_B_val

def expected_payoff_B(strategy_A, strategy_B):
    return payoff_B[strategy_B, strategy_A]

strategies = ["Work Hard", "Slack"]
payoffs_A = np.zeros((2, 2))
payoffs_B = np.zeros((2, 2))

for strategy_A in range(2):
    for strategy_B in range(2):
        payoffs_A[strategy_A, strategy_B] = expected_payoff_A(strategy_A, strategy_B)
        payoffs_B[strategy_B, strategy_A] = expected_payoff_B(strategy_A, strategy_B)

print("Player A's expected payoffs:")
print(payoffs_A)

print("\nPlayer B's expected payoffs:")
print(payoffs_B)
        ''',
        '''
def run_game(game_name, items, actual_values):
    print(f"\n--- {game_name} ---")
    players = ['p1', 'p2']
    scores = {p: 0 for p in players}

    for item in items:
        actual = actual_values[item]
        for p in players:
            guess = int(input(f"{p} guess for {item}: "))
            diff = abs(guess - actual)
            if diff == 0:
                scores[p] += 100
            elif diff <= 0.05 * actual:
                scores[p] += 75
            elif diff <= 0.1 * actual:
                scores[p] += 50
            elif diff <= 0.2 * actual:
                scores[p] += 25
    for p in players:
        print(f"{p}: {scores[p]} points")

run_game("Flight Fare Estimation",
         ['Mumbai-Delhi', 'NY-LA', 'Tokyo-Kyoto'],
         {'Mumbai-Delhi': 4000, 'NY-LA': 20000, 'Tokyo-Kyoto': 10000})

run_game("Salary Estimation",
         ['Software Dev', 'Data Scientist', 'UX Designer'],
         {'Software Dev': 1200000, 'Data Scientist': 1500000, 'UX Designer': 1000000})

run_game("Product Value Estimation",
         ['Smartphone', 'Electric Car', 'Fashion Brand'],
         {'Smartphone': 799, 'Electric Car': 35000, 'Fashion Brand': 1000})
        ''',
    ]

    @staticmethod
    def text(index):
        """Fetch a specific code based on the index."""
        try:
            return Game.codes[index - 1]
        except IndexError:
            return f"Invalid code index. Please choose a number between 1 and {len(Game.codes)}."
