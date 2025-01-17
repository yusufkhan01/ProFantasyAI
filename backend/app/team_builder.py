from utils import get_player_position
from algorithm import calculate_value_score

def build_best_team(players):
    team = []
    total_budget = 0.0
    team_count = {}
    position_count = {'GK': 0, 'DEF': 0, 'MID': 0, 'FWD': 0}

    for player in players:
        player['value'] = calculate_value_score(player)
    
    
    # Sort players by value score (highest value first)
    sorted_players = sorted(players, key=lambda x: x['value'], reverse=True)
    
    # Assign players to positions
    positions = {
        'GK': 2,
        'DEF': 5,
        'MID': 5,
        'FWD': 3
    }
    
    for player in sorted_players:
        # Skip if budget exceeds
        if total_budget + player['now_cost'] > 1000.0:
            continue
        
        # Max players from one team
        team_count[player['team']] = team_count.get(player['team'], 0) + 1
        if team_count[player['team']] > 3:
            continue
        
        # Check if the position has reached its required count
        position_name = get_player_position(player['element_type'])
        if position_count[position_name] >= positions[position_name]:
            continue
        
        # Add player to the team
        team.append(player)
        total_budget += player['now_cost']
        position_count[position_name] += 1
        
        # If all positions are filled, stop the process
        if len(team) == 15:
            break
        
        budget = 1000.0 - total_budget
    return team, budget


