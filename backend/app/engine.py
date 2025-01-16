def build_best_team(players, max_budget=100, max_players_per_team=3):
    team = []
    budget = 0
    team_count = {}
    position_count = {'GK': 0, 'DEF': 0, 'MID': 0, 'FWD': 0}

    for player in players:
        # Ensure player data is valid before performing calculations
        if 'total_points' in player and 'form' in player and 'price' in player:
            # Convert 'form' and 'total_points' to float if they are not already
            player['form'] = float(player['form'])  # Convert form to float
            player['price'] = float(player['price'])  # Ensure price is float
            player['total_points'] = float(player['total_points'])  # Ensure total_points is float

            # Prevent division by zero
            if player['price'] != 0:
                value_score = (player['total_points'] + player['form']) / player['price']
            else:
                value_score = 0  # Default value if price is 0

            player['value_score'] = value_score
            players.append(player)
        else:
            # Handle players with missing data
            print(f"Player data missing for: {player}")
    
    # Sort players by value score (highest value first)
    players = sorted(players, key=lambda x: x['value_score'], reverse=True)
    
    # Assign players to positions
    positions = {
        'GK': 2,
        'DEF': 5,
        'MID': 5,
        'FWD': 3
    }
    
    for player in players:
        # Skip if budget exceeds
        if budget + player['price'] > max_budget:
            continue
        
        # Max players from one team
        team_count[player['team']] = team_count.get(player['team'], 0) + 1
        if team_count[player['team']] > max_players_per_team:
            continue
        
        # Check if the position has reached its required count
        position_name = get_player_position(player['position'])
        if position_count[position_name] >= positions[position_name]:
            continue
        
        # Add player to the team
        team.append(player)
        budget += player['price']
        position_count[position_name] += 1
        
        # If all positions are filled, stop the process
        if len(team) == 15:
            break
    
    return team, budget

def get_player_position(position_id):
    # Map element_type to position
    position_mapping = {
        1: 'GK',
        2: 'DEF',
        3: 'MID',
        4: 'FWD'
    }
    return position_mapping.get(position_id, 'Unknown')
