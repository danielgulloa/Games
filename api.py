from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from runme import Player, Table, create_tiles, distribute_tiles
import json

app = Flask(__name__)

# Simple CORS configuration
CORS(app)

# Add after_request handler to ensure CORS headers are always present
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

# Global game state
game_state = {
    "table": None,
    "players": None,
    "current_player_index": 0,
    "turn_count": 0,
    "passes": 0,
    "game_over": False,
    "winner": None,
    "game_locked": False,
    "game_history": []
}

def serialize_tile(tile):
    """Convert a tile to a JSON-serializable format"""
    return tile if isinstance(tile, list) else list(tile)

def get_game_state_json():
    """Get the current game state as JSON"""
    if not game_state["table"]:
        return None
    
    players_data = []
    for i, player in enumerate(game_state["players"]):
        players_data.append({
            "name": player.name,
            "strategy": player.strategy,
            "tiles": [serialize_tile(t) for t in player.tiles],
            "tile_count": len(player.tiles),
            "team": player.team,
            "is_current": i == game_state["current_player_index"]
        })
    
    # Calculate team points for locked games
    team_ac_points = sum(game_state["table"].count_points(p) for p in game_state["players"] if p.team == "AC")
    team_bd_points = sum(game_state["table"].count_points(p) for p in game_state["players"] if p.team == "BD")
    
    return {
        "table": [serialize_tile(t) for t in game_state["table"].played_tiles],
        "playable_numbers": game_state["table"].get_playable_numbers(),
        "players": players_data,
        "current_player": game_state["players"][game_state["current_player_index"]].name,
        "current_player_index": game_state["current_player_index"],
        "turn_count": game_state["turn_count"],
        "passes": game_state["passes"],
        "game_over": game_state["game_over"],
        "winner": game_state["winner"],
        "game_locked": game_state["game_locked"],
        "team_ac_points": team_ac_points,
        "team_bd_points": team_bd_points,
        "play_history": [(name, serialize_tile(tile)) for name, tile in game_state["table"].play_history],
        "game_history": game_state["game_history"][-3:]  # Return only last 3 moves
    }

@app.before_request
def log_request():
    print(f"Request: {request.method} {request.path}")
    print(f"Host: {request.host}")
    print(f"Remote Addr: {request.remote_addr}")
    print(f"Content-Type: {request.content_type}")

@app.route('/api/game/start', methods=['POST', 'OPTIONS'])
def start_game():
    """Initialize a new game"""
    print(f"start_game called with method {request.method}")
    data = request.json or {}
    player_position = data.get('player_position', 0)  # 0, 1, 2, or 3
    
    print(f"Starting game with player position {player_position}")
    
    # Reset game state
    tiles = create_tiles()
    table = Table()
    players = [Player(name, "AI") for name in ["A", "B", "C", "D"]]
    
    # Set human player
    players[player_position].strategy = "User"
    
    # Set all other players to AI strategy
    for i, player in enumerate(players):
        if i != player_position:
            player.strategy = "AI"
    
    # Give each player access to all players
    for player in players:
        player.all_players = players
    
    distribute_tiles(players, tiles)
    
    game_state["table"] = table
    game_state["players"] = players
    game_state["current_player_index"] = 0
    game_state["turn_count"] = 0
    game_state["passes"] = 0
    game_state["game_over"] = False
    game_state["winner"] = None
    game_state["game_locked"] = False
    game_state["game_history"] = []
    
    return jsonify(get_game_state_json())

@app.route('/api/game/state', methods=['GET', 'OPTIONS'])
def get_state():
    """Get current game state"""
    if not game_state["table"]:
        return jsonify({"error": "No game in progress"}), 400
    return jsonify(get_game_state_json())

@app.route('/api/game/play', methods=['POST', 'OPTIONS'])
def play_turn():
    """Play a tile for the current player"""
    if game_state["game_over"]:
        return jsonify({"error": "Game is over"}), 400
    
    data = request.json
    tile_index = data.get('tile_index')
    side = data.get('side', None)  # 'L' or 'R' for ambiguous placements
    
    current_player = game_state["players"][game_state["current_player_index"]]
    
    if tile_index is not None and 0 <= tile_index < len(current_player.tiles):
        tile = current_player.tiles[tile_index]
        current_player.tiles.pop(tile_index)
        
        # Log the move to game history
        game_state["game_history"].append({
            "player": current_player.name,
            "action": "played",
            "tile": list(tile),
            "reasoning": f"Player {current_player.name} played tile {list(tile)}"
        })
        
        # Handle tile placement
        if side:
            if side == 'L':
                if tile[1] == game_state["table"].played_tiles[0][0]:
                    game_state["table"].played_tiles.insert(0, tile)
                else:
                    game_state["table"].played_tiles.insert(0, tile[::-1])
            else:  # side == 'R'
                if tile[0] == game_state["table"].played_tiles[-1][1]:
                    game_state["table"].played_tiles.append(tile)
                else:
                    game_state["table"].played_tiles.append(tile[::-1])
        else:
            game_state["table"].play_tile(tile, current_player.name)
        
        # Check if player won
        if not current_player.tiles:
            game_state["game_over"] = True
            game_state["winner"] = current_player.name
            return jsonify({
                "success": True,
                "message": f"Player {current_player.name} played {tile}",
                "game_state": get_game_state_json()
            })
        
        # Move to next player
        game_state["passes"] = 0
        game_state["turn_count"] += 1
        game_state["current_player_index"] = (game_state["current_player_index"] + 1) % len(game_state["players"])
        
        # Play AI turns until it's human's turn or game ends
        while True:
            current_player = game_state["players"][game_state["current_player_index"]]
            
            # Skip if it's the human player (strategy == "User")
            if current_player.strategy == "User":
                break
            
            played_tile = current_player.play_turn(game_state["table"])
            
            if not played_tile:
                game_state["passes"] += 1
                # Log the pass
                game_state["game_history"].append({
                    "player": current_player.name,
                    "action": "passed",
                    "tile": None,
                    "reasoning": f"Player {current_player.name} has no valid moves"
                })
            else:
                game_state["passes"] = 0
                # Log the AI move
                game_state["game_history"].append({
                    "player": current_player.name,
                    "action": "played",
                    "tile": list(played_tile),
                    "reasoning": f"AI Player {current_player.name} played tile {list(played_tile)}"
                })
            
            if not current_player.tiles:
                game_state["game_over"] = True
                game_state["winner"] = current_player.name
                break
            
            if game_state["passes"] >= len(game_state["players"]):
                game_state["game_over"] = True
                game_state["game_locked"] = True
                # Calculate winner based on points
                team_ac_points = sum(game_state["table"].count_points(p) for p in game_state["players"] if p.team == "AC")
                team_bd_points = sum(game_state["table"].count_points(p) for p in game_state["players"] if p.team == "BD")
                if team_ac_points < team_bd_points:
                    game_state["winner"] = "A"
                else:
                    game_state["winner"] = "B"
                break
            
            game_state["turn_count"] += 1
            game_state["current_player_index"] = (game_state["current_player_index"] + 1) % len(game_state["players"])
        
        return jsonify({
            "success": True,
            "message": f"Player played successfully",
            "game_state": get_game_state_json()
        })
    else:
        return jsonify({"error": "Invalid tile index"}), 400

@app.route('/api/game/get-valid-moves', methods=['GET', 'OPTIONS'])
def get_valid_moves():
    """Get valid moves for the current player"""
    if not game_state["table"]:
        return jsonify({"error": "No game in progress"}), 400
    
    current_player = game_state["players"][game_state["current_player_index"]]
    playable_numbers = game_state["table"].get_playable_numbers()
    
    valid_moves = []
    ambiguous = []
    
    for i, tile in enumerate(current_player.tiles):
        if not playable_numbers:
            # First move - any tile is valid
            valid_moves.append(i)
        else:
            # Check if tile can play on left end
            left_playable = tile[0] == game_state["table"].played_tiles[0][0] or tile[1] == game_state["table"].played_tiles[0][0]
            # Check if tile can play on right end
            right_playable = tile[0] == game_state["table"].played_tiles[-1][1] or tile[1] == game_state["table"].played_tiles[-1][1]
            
            if left_playable or right_playable:
                valid_moves.append(i)
                # If playable on both sides, mark as ambiguous
                if left_playable and right_playable:
                    ambiguous.append(i)
    
    return jsonify({
        "valid_moves": valid_moves,
        "ambiguous_tiles": ambiguous
    })

@app.route('/api/game/skip', methods=['POST', 'OPTIONS'])
def skip_turn():
    """Skip the current player's turn (no valid moves)"""
    if game_state["game_over"]:
        return jsonify({"error": "Game is over"}), 400
    
    current_player = game_state["players"][game_state["current_player_index"]]
    
    # Log the pass
    game_state["game_history"].append({
        "player": current_player.name,
        "action": "passed",
        "tile": None,
        "reasoning": f"Player {current_player.name} has no valid moves"
    })
    
    game_state["passes"] += 1
    
    # Check if all 4 players have passed (game locked)
    if game_state["passes"] >= len(game_state["players"]):
        game_state["game_over"] = True
        game_state["game_locked"] = True
        # Calculate winner based on points
        team_ac_points = sum(game_state["table"].count_points(p) for p in game_state["players"] if p.team == "AC")
        team_bd_points = sum(game_state["table"].count_points(p) for p in game_state["players"] if p.team == "BD")
        if team_ac_points < team_bd_points:
            game_state["winner"] = "A"
        else:
            game_state["winner"] = "B"
        return jsonify({
            "success": True,
            "message": "Game locked - all players passed",
            "game_state": get_game_state_json()
        })
    
    # Move to next player
    game_state["turn_count"] += 1
    game_state["current_player_index"] = (game_state["current_player_index"] + 1) % len(game_state["players"])
    
    # Play AI turns until it's human's turn or game ends
    while True:
        current_player = game_state["players"][game_state["current_player_index"]]
        
        # Skip if it's the human player (strategy == "User")
        if current_player.strategy == "User":
            break
        
        played_tile = current_player.play_turn(game_state["table"])
        
        if not played_tile:
            game_state["passes"] += 1
            # Log the pass
            game_state["game_history"].append({
                "player": current_player.name,
                "action": "passed",
                "tile": None,
                "reasoning": f"Player {current_player.name} has no valid moves"
            })
        else:
            game_state["passes"] = 0
            # Log the AI move
            game_state["game_history"].append({
                "player": current_player.name,
                "action": "played",
                "tile": list(played_tile),
                "reasoning": f"AI Player {current_player.name} played tile {list(played_tile)}"
            })
        
        if not current_player.tiles:
            game_state["game_over"] = True
            game_state["winner"] = current_player.name
            break
        
        if game_state["passes"] >= len(game_state["players"]):
            game_state["game_over"] = True
            game_state["game_locked"] = True
            # Calculate winner based on points
            team_ac_points = sum(game_state["table"].count_points(p) for p in game_state["players"] if p.team == "AC")
            team_bd_points = sum(game_state["table"].count_points(p) for p in game_state["players"] if p.team == "BD")
            if team_ac_points < team_bd_points:
                game_state["winner"] = "A"
            else:
                game_state["winner"] = "B"
            break
        
        game_state["turn_count"] += 1
        game_state["current_player_index"] = (game_state["current_player_index"] + 1) % len(game_state["players"])
    
    return jsonify({
        "success": True,
        "message": f"Player {current_player.name} skipped",
        "game_state": get_game_state_json()
    })

@app.route('/api/game/reset', methods=['POST', 'OPTIONS'])
def reset_game():
    """Reset the game"""
    game_state["table"] = None
    game_state["players"] = None
    game_state["current_player_index"] = 0
    game_state["turn_count"] = 0
    game_state["passes"] = 0
    game_state["game_over"] = False
    game_state["winner"] = None
    game_state["game_locked"] = False
    game_state["game_history"] = []
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001, threaded=True)
