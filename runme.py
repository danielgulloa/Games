import random
n_sims = 1000
chance_of_playing_double=1


initial_tile = None
# Step 1: Create the tiles
def create_tiles():
    return [[i, j] for i in range(7) for j in range(i, 7)]

# Step 2: Create the Table class
class Table:
    def __init__(self):
        self.played_tiles = []
        self.play_history = []  # List of (player_name, tile) tuples
        
    def will_lock_game(self, tile, play_left):
        """Check if playing this tile will lock the game"""
        # Count occurrences of each number in played tiles
        number_counts = {}
        for t in self.played_tiles:
            number_counts[t[0]] = number_counts.get(t[0], 0) + 1
            if t[0] != t[1]:  # Don't double count doubles
                number_counts[t[1]] = number_counts.get(t[1], 0) + 1
        
        # Add the tile we're about to play
        number_counts[tile[0]] = number_counts.get(tile[0], 0) + 1
        if tile[0] != tile[1]:
            number_counts[tile[1]] = number_counts.get(tile[1], 0) + 1
            
        # Check which numbers would be available after playing
        if play_left:
            available_numbers = [tile[0], self.played_tiles[-1][1]]
        else:
            available_numbers = [self.played_tiles[0][0], tile[1]]
            
        # Game locks if all instances of available numbers are played
        # Each number appears 8 times in total (7 regular tiles + 1 double)
        return all(number_counts.get(num, 0) >= 8 for num in available_numbers)
        
    def count_points(self, player):
        """Count points in player's remaining tiles"""
        return sum(t[0] + t[1] for t in player.tiles)

    def play_tile(self, tile, player_name=None, force_left=False, force_right=False):
        # Update the played tile on the table
        if not self.played_tiles:
            self.played_tiles.append(tile)
        elif force_left or (not force_right and (tile[0] == self.played_tiles[0][0] or tile[1] == self.played_tiles[0][0])):
            if tile[0] == self.played_tiles[0][0]:
                self.played_tiles.insert(0, tile[::-1])
            else:
                self.played_tiles.insert(0, tile)
        else:  # Play on right
            if tile[0] == self.played_tiles[-1][1]:
                self.played_tiles.append(tile)
            else:
                self.played_tiles.append(tile[::-1])
        
        # Record who played what
        if player_name:
            self.play_history.append((player_name, tile.copy()))

    def get_playable_numbers(self):
        if not self.played_tiles:
            return []
        return [self.played_tiles[0][0], self.played_tiles[-1][1]]
    def print_table(self):
        return "Table:", self.played_tiles

# Step 3: Create the Player class
class Player:
    def __init__(self, name, strategy):
        self.name = name
        self.strategy = strategy
        self.tiles = []
        self.memory = {}
        self.team = "AC" if name in ["A", "C"] else "BD"
        self.all_players = None  # Will be set during game initialization
        
    def get_all_players(self):
        return self.all_players

    def play_turn(self, table):
        # Check if a double domino can be played (prioritized for all strategies)
        playable_numbers = table.get_playable_numbers()

        if self.strategy != "User":            
            double_domino = None
            for tile in self.tiles:
                if tile[0] == tile[1] and (tile[0] in playable_numbers or not playable_numbers):
                    double_domino = tile
                    break

            if double_domino and random.random() < chance_of_playing_double:
                self.tiles.remove(double_domino)
                table.play_tile(double_domino)
                print(f"Player {self.name} prioritized playing double domino {double_domino}")
                return double_domino

        if self.strategy == "Win":
            # Count occurrences of each number in player's tiles
            number_counts = {}
            for tile in self.tiles:
                for number in tile:
                    number_counts[number] = number_counts.get(number, 0) + 1

            # Sort numbers by frequency
            sorted_numbers = sorted(number_counts, key=number_counts.get, reverse=True)

            # Find the best tile to play
            playable_numbers = table.get_playable_numbers()
            best_tile = None
            best_tile_reason = ""

            if not playable_numbers:
                # No tiles on the table, play the tile with the most frequent numbers
                for tile in self.tiles:
                    if not best_tile or sum(number_counts[n] for n in tile) > sum(number_counts[n] for n in best_tile):
                        best_tile = tile
                        best_tile_reason = f"Starting with tile {tile} because it has the most frequent numbers."
                global initial_tile
                initial_tile = best_tile
            else:
                # Play to maximize the frequency of playable numbers
                for tile in self.tiles:
                    if tile[0] in playable_numbers or tile[1] in playable_numbers:
                        # Calculate the frequency of the resulting playable numbers
                        resulting_playable = set(playable_numbers)
                        if tile[0] in playable_numbers:
                            resulting_playable.add(tile[1])
                        if tile[1] in playable_numbers:
                            resulting_playable.add(tile[0])

                        resulting_frequency = sum(number_counts.get(n, 0) for n in resulting_playable)
                        if not best_tile or resulting_frequency > sum(number_counts[n] for n in best_tile):
                            best_tile = tile
                            best_tile_reason = f"Playing tile {tile} to maximize playable numbers {resulting_playable}."
            if False:
            # This handles the situation where a player has the last unique number
            # and wants to keep it open for future turns.
                unique_numbers = set()
                for tile in self.tiles:
                    for number in tile:
                        if number_counts[number] == 1:  # Only this player has this number
                            unique_numbers.add(number)

                # Adjust strategy to keep unique numbers open
                for tile in self.tiles:
                    if tile[0] in unique_numbers or tile[1] in unique_numbers:
                        other_number = tile[1] if tile[0] in unique_numbers else tile[0]
                        if other_number in playable_numbers:
                            best_tile = tile
                            best_tile_reason = f"Playing tile {tile} to keep unique number {tile[0] if tile[1] in unique_numbers else tile[1]} open."
                            break


 
            if best_tile:
                self.tiles.remove(best_tile)
                table.play_tile(best_tile, self.name)
                print(f"Player {self.name} reasoning: {best_tile_reason}")
                return best_tile

            # No playable tile, consider switching strategy with teammate
            if self.strategy == "Win":
                # Find teammate
                teammate = None
                for p in self.get_all_players():
                    if p.team == self.team and p != self:
                        teammate = p
                        break
                
                if teammate and len(self.tiles) >= len(teammate.tiles):
                    print(f"Player {self.name} switches strategy with {teammate.name} after passing")
                    self.strategy, teammate.strategy = teammate.strategy, self.strategy
            return None

        if self.strategy == "Help":
            # Assume A's initial play indicates their strong numbers
            # Get teammate's played tiles in order
            if self.team == "AC":
                if self.name == "A":
                    teammate = "C"
                else:
                    teammate = "A"
            else:
                if self.name == "B":
                    teammate = "D"
                else:                    
                    teammate = "B"
            teammate_tiles = []
            
            # First, add the initial tile if it was played by the teammate
            if initial_tile:
                teammate_tiles.append(initial_tile)
            
            # Then add all other tiles played by the teammate in order
            for player_name, tile in table.play_history:
                if player_name == teammate and tile != initial_tile:
                    teammate_tiles.append(tile)

            # Weight numbers based on when they were played (earlier tiles have stronger weight)
            strong_numbers = {}
            for i, tile in enumerate(teammate_tiles):
                weight = 1.0 / (i + 1)  # First tile gets weight 1, second 1/2, third 1/3, etc.
                for number in tile:
                    strong_numbers[number] = strong_numbers.get(number, 0) + weight

            print(f"Player {self.name} sees teammate {teammate}'s tiles played in order: {teammate_tiles}")
            print(f"Player {self.name} sees teammate {teammate}'s weighted numbers as {strong_numbers}")

            # Find a tile to keep teammate's strong numbers available
            playable_numbers = table.get_playable_numbers()
            best_tile = None
            best_tile_reason = ""

            for tile in self.tiles:
                if tile[0] in playable_numbers or tile[1] in playable_numbers:
                    # Check if playing this tile keeps strong numbers available
                    resulting_playable = set(playable_numbers)
                    if tile[0] in playable_numbers:
                        resulting_playable.add(tile[1])
                    if tile[1] in playable_numbers:
                        resulting_playable.add(tile[0])

                    # Calculate the weight of the numbers that would remain playable
                    move_value = sum(strong_numbers.get(n, 0) for n in resulting_playable)
                    if not best_tile or move_value > best_move_value:
                        best_tile = tile
                        best_move_value = move_value
                        best_tile_reason = f"Playing tile {tile} to keep teammate's strong numbers available (value: {move_value:.2f})"

            if best_tile:
                self.tiles.remove(best_tile)
                table.play_tile(best_tile, self.name)
                print(f"Player {self.name} reasoning: {best_tile_reason}")
                return best_tile

            # If no helping move found, fall back to random strategy
            print(f"Player {self.name} found no helping move, falling back to random strategy")
            random.shuffle(self.tiles)
            for tile in self.tiles:
                if tile[0] in playable_numbers or tile[1] in playable_numbers:
                    self.tiles.remove(tile)
                    table.play_tile(tile)
                    print(f"Player {self.name} played random tile {tile}")
                    return tile
            
            # No playable tile at all, skip turn
            return None

        if self.strategy == "User":
            print("\nYour turn!")
            print(f"Table: {table.played_tiles}")
            print(f"Your tiles: {self.tiles}")
            
            playable_numbers = table.get_playable_numbers()
            if not playable_numbers:
                # First play
                while True:
                    try:
                        tile_idx = int(input(f"Choose a tile (0-{len(self.tiles)-1}): "))
                        if 0 <= tile_idx < len(self.tiles):
                            tile = self.tiles.pop(tile_idx)
                            table.play_tile(tile, self.name)
                            return tile
                        else:
                            print("Invalid tile number. Try again.")
                    except ValueError:
                        print("Please enter a valid number.")
            
            # Show valid moves
            valid_moves = []
            for i, tile in enumerate(self.tiles):
                if tile[0] in playable_numbers or tile[1] in playable_numbers:
                    valid_moves.append(i)
            
            if not valid_moves:
                print("No valid moves. Your turn is skipped.")
                return None
                
            print("Valid moves:")
            for i in valid_moves:
                print(f"{i}: {self.tiles[i]}")
                
            while True:
                try:
                    tile_idx = int(input(f"Choose a tile (valid numbers are {valid_moves}): "))
                    if tile_idx in valid_moves:
                        chosen_tile = self.tiles[tile_idx]
                        
                        # Check if we need to ask which side to play on
                        can_play_left = (chosen_tile[0] == table.played_tiles[0][0] or 
                                       chosen_tile[1] == table.played_tiles[0][0])
                        can_play_right = (chosen_tile[0] == table.played_tiles[-1][1] or 
                                        chosen_tile[1] == table.played_tiles[-1][1])
                        
                        if can_play_left and can_play_right:
                            while True:
                                side = input("Where do you want to play it? (L for left, R for right): ").upper()
                                if side in ['L', 'R']:
                                    break
                                print("Please enter L or R.")
                                
                            # Manually handle the tile placement
                            tile = self.tiles.pop(tile_idx)
                            if side == 'L':
                                if tile[1] == table.played_tiles[0][0]:
                                    table.played_tiles.insert(0, tile)
                                else:
                                    table.played_tiles.insert(0, tile[::-1])
                            else:  # side == 'R'
                                if tile[0] == table.played_tiles[-1][1]:
                                    table.played_tiles.append(tile)
                                else:
                                    table.played_tiles.append(tile[::-1])
                            return tile
                        else:
                            # Normal play
                            tile = self.tiles.pop(tile_idx)
                            table.play_tile(tile, self.name)
                            return tile
                    else:
                        print("Invalid choice. Try again.")
                except ValueError:
                    print("Please enter a valid number.")
            
        if self.strategy == "AI":
            # Advanced AI strategy
            playable_numbers = table.get_playable_numbers()
            
            if not playable_numbers:
                # First play - use a balanced approach
                number_counts = {}
                for tile in self.tiles:
                    for number in tile:
                        number_counts[number] = number_counts.get(number, 0) + 1
                
                best_tile = max(self.tiles, key=lambda t: sum(number_counts.get(n, 0) for n in t))
                self.tiles.remove(best_tile)
                table.play_tile(best_tile, self.name)
                #global initial_tile
                initial_tile = best_tile
                return best_tile
            
            # Analyze played tiles to estimate remaining tiles
            played_count = {}
            for player_name, tile in table.play_history:
                played_count[tile[0]] = played_count.get(tile[0], 0) + 1
                if tile[0] != tile[1]:
                    played_count[tile[1]] = played_count.get(tile[1], 0) + 1
            
            # Find our tiles in hand
            our_count = {}
            for tile in self.tiles:
                our_count[tile[0]] = our_count.get(tile[0], 0) + 1
                if tile[0] != tile[1]:
                    our_count[tile[1]] = our_count.get(tile[1], 0) + 1
            
            # Get teammate and opponent info
            teammate = None
            opponent1 = None
            opponent2 = None
            for p in self.all_players:
                if p.team == self.team and p != self:
                    teammate = p
                elif p.team != self.team:
                    if opponent1 is None:
                        opponent1 = p
                    else:
                        opponent2 = p
            
            # Calculate how close each player is to winning
            our_tiles = len(self.tiles) - 1  # -1 for the tile we'll play
            teammate_tiles = len(teammate.tiles) if teammate else float('inf')
            opp1_tiles = len(opponent1.tiles) if opponent1 else float('inf')
            opp2_tiles = len(opponent2.tiles) if opponent2 else float('inf')
            
            # Find valid moves
            valid_moves = []
            for i, tile in enumerate(self.tiles):
                if tile[0] in playable_numbers or tile[1] in playable_numbers:
                    valid_moves.append((i, tile))
            
            if not valid_moves:
                return None
            
            best_move = None
            best_score = float('-inf')
            
            for idx, tile in valid_moves:
                score = 0
                reasoning = []
                
                # Priority 1: Does it win for us?
                if our_tiles <= 0:
                    score += 1000
                    reasoning.append("Win for us (+1000)")
                
                # Priority 2: Does it help our teammate win?
                if teammate_tiles <= 0:
                    score += 900
                    reasoning.append("Win for teammate (+900)")
                
                # Priority 3: Does it prevent opponent from winning?
                if opp1_tiles <= 0 or opp2_tiles <= 0:
                    score -= 500  # Penalize if we let them win
                    reasoning.append("Opponent close to winning (-500)")
                
                # Priority 4: Reduce variance - play numbers we have many of
                numbers_in_tile = set(tile)
                our_strength = sum(our_count.get(n, 0) for n in numbers_in_tile)
                score += our_strength * 10
                reasoning.append(f"Our strength in tile (+{our_strength * 10})")
                
                # Priority 5: Block opponent's likely strong numbers
                # Count how many unplayed tiles of each number exist
                unplayed_count = {}
                for num in range(7):
                    unplayed_count[num] = 8 - played_count.get(num, 0)
                
                # If we have a tile with rare numbers, it's less useful
                rare_bonus = 0
                for num in numbers_in_tile:
                    if unplayed_count.get(num, 0) <= 2:
                        rare_bonus += 5
                score += rare_bonus
                if rare_bonus > 0:
                    reasoning.append(f"Rare numbers bonus (+{rare_bonus})")
                
                # Priority 6: Keep control - prefer moves that don't leave too many options
                resulting_playable = set(playable_numbers)
                if tile[0] in playable_numbers:
                    resulting_playable.add(tile[1])
                if tile[1] in playable_numbers:
                    resulting_playable.add(tile[0])
                
                # Prefer having few options for opponents (fewer ways to help them)
                opponent_options = sum(unplayed_count.get(n, 0) for n in resulting_playable)
                option_penalty = opponent_options * 2
                score -= option_penalty
                reasoning.append(f"Opponent options penalty (-{option_penalty})")
                
                # Priority 7: Team strategy - help teammate if they're close to winning
                team_bonus = 0
                if teammate_tiles <= 3 and teammate_tiles < our_tiles:
                    # Check if this move helps teammate's likely strong numbers
                    if initial_tile and any(n in initial_tile for n in tile):
                        team_bonus = 50
                        score += team_bonus
                        reasoning.append(f"Support teammate (+{team_bonus})")
                
                if score > best_score:
                    best_score = score
                    best_move = (idx, tile, reasoning)
            
            if best_move:
                idx, tile, reasoning = best_move
                self.tiles.remove(tile)
                table.play_tile(tile, self.name)
                
                # Print reasoning
                if len(valid_moves) == 1:
                    print(f"Player {self.name} reasoning: No other option available")
                else:
                    reasoning_str = ", ".join(reasoning)
                    print(f"Player {self.name} reasoning: {tile} - {reasoning_str} (total: {best_score:.1f})")
                return tile
            
            return None

        if self.strategy == "Block":
            # Find the next player
            next_player = None
            for i, p in enumerate(self.all_players):
                if p == self:
                    next_player = self.all_players[(i + 1) % len(self.all_players)]
                    break
            
            # Analyze next player's strong numbers based on their plays
            next_player_tiles = []
            enemy_team_tiles = []  # Include teammate's plays too
            
            # Get the initial tile if it was from next player or their teammate
            if initial_tile:
                if self.team != next_player.team:  # They're on the opposite team
                    next_player_tiles.append(initial_tile)
                    
            # Get all plays by next player and their teammate
            for player_name, tile in table.play_history:
                player = None
                for p in self.all_players:
                    if p.name == player_name:
                        player = p
                        break
                
                if player and player.team == next_player.team:
                    enemy_team_tiles.append(tile)
                    if player == next_player:
                        next_player_tiles.append(tile)
            
            # Weight numbers based on when they were played and who played them
            enemy_numbers = {}
            for i, tile in enumerate(next_player_tiles):
                weight = 2.0 / (i + 1)  # Higher weight for next player's tiles
                for number in tile:
                    enemy_numbers[number] = enemy_numbers.get(number, 0) + weight
                    
            for i, tile in enumerate(enemy_team_tiles):
                weight = 1.0 / (i + 1)  # Lower weight for teammate's tiles
                for number in tile:
                    enemy_numbers[number] = enemy_numbers.get(number, 0) + weight
            
            print(f"Player {self.name} analyzing enemy team's numbers: {enemy_numbers}")
            
            # Try to block their strong numbers
            playable_numbers = table.get_playable_numbers()
            best_tile = None
            best_block_value = -1
            best_tile_reason = ""

            if not playable_numbers:
                # No tiles on the table, just play randomly
                tile = self.tiles.pop(0)
                table.play_tile(tile, self.name)
                return tile

            for tile in self.tiles:
                if tile[0] in playable_numbers or tile[1] in playable_numbers:
                    # Calculate which numbers would be left playable
                    resulting_playable = set()
                    placed_tile = list(tile)
                    
                    # Consider both orientations of the tile
                    if tile[0] in playable_numbers:
                        resulting_playable.add(tile[1])
                    if tile[1] in playable_numbers:
                        resulting_playable.add(tile[0])
                    
                    # If we can make both numbers the same (and low weight for enemy),
                    # that's ideal for blocking
                    if len(resulting_playable) == 1:
                        block_value = 10 - (enemy_numbers.get(list(resulting_playable)[0], 0))
                    else:
                        block_value = -sum(enemy_numbers.get(n, 0) for n in resulting_playable)
                    
                    if block_value > best_block_value:
                        best_tile = tile
                        best_block_value = block_value
                        best_tile_reason = f"Playing {tile} to force numbers {resulting_playable} (blocking value: {block_value:.2f})"
            
            if best_tile:
                self.tiles.remove(best_tile)
                table.play_tile(best_tile, self.name)
                print(f"Player {self.name} blocking: {best_tile_reason}")
                return best_tile
            
            return None

        # Default random strategy
        playable_numbers = table.get_playable_numbers()
        if not playable_numbers:
            # No tiles on the table, play any tile
            tile = self.tiles.pop(0)
            table.play_tile(tile, self.name)
            return tile

        # Find a tile that can be played
        random.shuffle(self.tiles)
        for tile in self.tiles:
            if tile[0] in playable_numbers or tile[1] in playable_numbers:
                self.tiles.remove(tile)
                table.play_tile(tile)
                return tile



        # No playable tile, skip turn
        return None
    def print_tiles(self):
        return f"Player {self.name} tiles:", self.tiles

# Step 4: Distribute tiles
def distribute_tiles(players, tiles):
    random.shuffle(tiles)
    for player in players:
        player.tiles = [tiles.pop() for _ in range(7)]

def printv(verbose, *args):
    if verbose:
        print(*args)

# Step 5: Simulate the game
def simulate_game(verbose=False):
    tiles = create_tiles()
    table = Table()
    players = [Player(name, "Random") for name in ["A", "B", "C", "D"]]
    #******************
    #Possible strategies are "Win", "Help", "Block", "Random", "AI", "User"
    players[0].strategy = "AI"  # Set player A to use the Win strategy
    players[1].strategy = "AI"  # Set player B to use Random strategy
    players[2].strategy = "AI"  # Set player C to use the Help strategy
    players[3].strategy = "AI"  # Set player D to use Random strategy
    
    # Give each player access to all players for strategy switching
    for player in players:
        player.all_players = players
    
    distribute_tiles(players, tiles)
    for i in range(4):
        printv(verbose, f"Player {i} tiles: {players[i].tiles}")
    passes = 0
    winner = None
    current_player_index = 0
    while True:
        current_player = players[current_player_index]
        played_tile = current_player.play_turn(table)
        if played_tile:
            passes = 0
            printv(verbose, f"Player {current_player.name} played {played_tile}")
            printv(verbose, table.print_table())
        else:
            passes += 1
            printv(verbose, f"Player {current_player.name} skipped their turn")

        if not current_player.tiles:
            print(f"Player {current_player.name} wins!")
            winner = current_player
            break
        if passes >= len(players):
            printv(verbose, "Game locked.")
            # Count points for each team
            team_ac_points = sum(table.count_points(p) for p in players if p.team == "AC")
            team_bd_points = sum(table.count_points(p) for p in players if p.team == "BD")
            printv(verbose, f"Team AC points: {team_ac_points}")
            printv(verbose, f"Team BD points: {team_bd_points}")
            # Give victory to A or B depending on which team has fewer points
            if team_ac_points < team_bd_points:
                winner = next(p for p in players if p.name == "A")
                print(f"Player A wins (Team AC: {team_ac_points} points vs Team BD: {team_bd_points} points)")
            else:
                winner = next(p for p in players if p.name == "B")
                print(f"Player B wins (Team BD: {team_bd_points} points vs Team AC: {team_ac_points} points)")
            break

        current_player_index = (current_player_index + 1) % len(players)
    return winner

if __name__ == "__main__":
    results = {}
    for player in ["A", "B", "C", "D", "TIE", 'TEAM_AC', 'TEAM_BD']:
        results[player] = 0
    
    for _ in range(n_sims):
        winner = simulate_game(False)
        if winner:
            results[winner.name] += 1
            results['TEAM_' + winner.team] += 1
        else:
            results["TIE"] += 1
    print(f"Results after {n_sims} games:")
    for player, wins in results.items():
        print(f"Player {player}: {wins} ({wins/n_sims*100:.2f}%) wins")
