import os
import sys
from runme import simulate_game, Player, Table, create_tiles, distribute_tiles

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    """Print the game header"""
    print("=" * 60)
    print("DOMINO GAME - Interactive Player Mode")
    print("=" * 60)

def print_menu():
    """Print the main menu"""
    clear_screen()
    print_header()
    print("\nSelect game mode:")
    print("1. Play against AI opponents (You as Player A)")
    print("2. Play against different AI opponents (You as Player C)")
    print("3. Simulate games (no human players)")
    print("4. Exit")
    print("-" * 60)

def get_valid_input(prompt, valid_options):
    """Get valid input from user"""
    while True:
        user_input = input(prompt).strip()
        if user_input in valid_options:
            return user_input
        print(f"Invalid input. Please choose from: {', '.join(valid_options)}")

def play_with_human_player(player_position):
    """Play a game with a human player at the specified position"""
    clear_screen()
    print_header()
    
    tiles = create_tiles()
    table = Table()
    players = [Player(name, "AI") for name in ["A", "B", "C", "D"]]
    
    # Set player position to User
    players[player_position].strategy = "User"
    player_name = players[player_position].name
    
    # Set strategies for other AI players
    if player_position == 0:  # Human is A
        players[1].strategy = "Block"   # B blocks
        players[2].strategy = "Help"    # C helps
        players[3].strategy = "Block"   # D blocks
    else:  # Human is C
        players[0].strategy = "Win"     # A wins
        players[1].strategy = "Block"   # B blocks
        players[3].strategy = "Block"   # D blocks
    
    # Give each player access to all players for strategy switching
    for player in players:
        player.all_players = players
    
    distribute_tiles(players, tiles)
    
    print(f"\nYou are playing as Player {player_name}")
    print(f"Your teammate is Player {'C' if player_position == 0 else 'A'}")
    print(f"Your opponents are Players {'B and D' if player_position == 0 else 'B and D'}")
    print("\nPress Enter to start the game...")
    input()
    
    passes = 0
    winner = None
    current_player_index = 0
    turn_count = 0
    
    while True:
        turn_count += 1
        current_player = players[current_player_index]
        
        # Clear screen and show game state
        clear_screen()
        print_header()
        print(f"\nTurn {turn_count} - Player {current_player.name}'s turn")
        print("-" * 60)
        print(f"Table: {table.played_tiles}")
        print(f"\nTile counts: A={len(players[0].tiles)}, B={len(players[1].tiles)}, "
              f"C={len(players[2].tiles)}, D={len(players[3].tiles)}")
        
        # Show playable numbers
        playable = table.get_playable_numbers()
        if playable:
            print(f"Playable numbers: {playable}")
        else:
            print("First play - any tile is playable")
        
        played_tile = current_player.play_turn(table)
        
        if played_tile:
            passes = 0
            print(f"Player {current_player.name} played {played_tile}")
        else:
            passes += 1
            print(f"Player {current_player.name} passed their turn")
        
        if not current_player.tiles:
            print(f"\n{'=' * 60}")
            print(f"PLAYER {current_player.name} WINS!")
            print(f"{'=' * 60}")
            winner = current_player
            break
        
        if passes >= len(players):
            print(f"\n{'=' * 60}")
            print("GAME LOCKED!")
            # Count points for each team
            team_ac_points = sum(table.count_points(p) for p in players if p.team == "AC")
            team_bd_points = sum(table.count_points(p) for p in players if p.team == "BD")
            print(f"Team AC points: {team_ac_points}")
            print(f"Team BD points: {team_bd_points}")
            # Give victory to A or B depending on which team has fewer points
            if team_ac_points < team_bd_points:
                winner = next(p for p in players if p.name == "A")
                print(f"TEAM AC WINS! (Player A awarded victory)")
            else:
                winner = next(p for p in players if p.name == "B")
                print(f"TEAM BD WINS! (Player B awarded victory)")
            print(f"{'=' * 60}")
            break
        
        current_player_index = (current_player_index + 1) % len(players)
        
        if current_player != players[player_position]:
            input("Press Enter to continue...")
    
    print("\nGame Over!")
    input("Press Enter to return to menu...")

def simulate_games_no_humans():
    """Run automated simulations"""
    clear_screen()
    print_header()
    
    try:
        num_games = int(input("\nHow many games to simulate? (default 10): ") or "10")
    except ValueError:
        num_games = 10
    
    print(f"\nSimulating {num_games} games...")
    print("-" * 60)
    
    results = {}
    for player in ["A", "B", "C", "D", "TIE"]:
        results[player] = 0
    
    for i in range(num_games):
        print(f"Game {i+1}...", end=" ", flush=True)
        winner = simulate_game(verbose=False)
        if winner:
            results[winner.name] += 1
        else:
            results["TIE"] += 1
        print("done")
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for player, wins in results.items():
        percentage = (wins / num_games * 100) if num_games > 0 else 0
        print(f"Player {player}: {wins} ({percentage:.1f}%) wins")
    print("=" * 60)
    
    input("\nPress Enter to return to menu...")

def main():
    """Main UI loop"""
    while True:
        print_menu()
        choice = get_valid_input("Enter your choice (1-4): ", ["1", "2", "3", "4"])
        
        if choice == "1":
            play_with_human_player(0)  # Player A
        elif choice == "2":
            play_with_human_player(2)  # Player C
        elif choice == "3":
            simulate_games_no_humans()
        elif choice == "4":
            print("\nGoodbye!")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user. Goodbye!")
        sys.exit(0)
