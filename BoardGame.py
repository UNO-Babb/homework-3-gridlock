from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

SAVE_FILE = 'save.json'
game_state = {}

def initialize_game():
    game_state["board_size"] = (5, 5)
    game_state["players"] = [
        {"name": "Player 1", "color": "black"},
        {"name": "Player 2", "color": "yellow"}
    ]
    game_state["pieces"] = []
    game_state["scores"] = [0, 0]
    game_state["turn"] = 0
    game_state["winner"] = None

def get_board():
    w, h = game_state["board_size"]
    board = [[None for _ in range(w)] for _ in range(h)]
    for p in game_state["pieces"]:
        board[p["y"]][p["x"]] = p["player_id"]
    return board

def is_taken(x, y):
    return any(p["x"] == x and p["y"] == y for p in game_state["pieces"])

def check_winner():
    board = get_board()
    w, h = game_state["board_size"]
    dirs = [(1,0), (0,1), (1,1), (1,-1)]

    for y in range(h):
        for x in range(w):
            current = board[y][x]
            if current is None:
                continue
            for dx, dy in dirs:
                count = 1
                nx, ny = x + dx, y + dy
                while 0 <= nx < w and 0 <= ny < h and board[ny][nx] == current:
                    count += 1
                    if count == 4:
                        return current
                    nx += dx
                    ny += dy
    return None

def make_move(x, y):
    if game_state["winner"] or is_taken(x, y):
        return
    player = game_state["turn"]
    game_state["pieces"].append({"x": x, "y": y, "player_id": player})
    game_state["scores"][player] += 1
    winner = check_winner()
    if winner is not None:
        game_state["winner"] = winner
    else:
        game_state["turn"] = 1 - game_state["turn"]
    save_game()

def save_game():
    with open(SAVE_FILE, 'w') as f:
        json.dump(game_state, f)

def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            saved = json.load(f)
            game_state.clear()
            game_state.update(saved)

def reset_game():
    initialize_game()
    save_game()

@app.route('/')
def index():
    return render_template('board.html', state=game_state)

@app.route('/move', methods=['POST'])
def move():
    x = int(request.form['x'])
    y = int(request.form['y'])
    make_move(x, y)
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    reset_game()
    return redirect(url_for('index'))

@app.route('/load')
def load():
    load_game()
    return redirect(url_for('index'))

if __name__ == '__main__':
    initialize_game()
    app.run(debug=True)


  