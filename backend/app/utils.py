import os
import json
import pandas as pd
from datetime import datetime, timedelta

CACHE_DIR = 'cache'

# 1. Data Processing Helpers

def format_player_data(players):
    formatted_data = []
    for player in players:
        formatted_data.append({
            "id": player['id'],
            "name": f"{player['first_name']} {player['second_name']}",
            "price": player['now_cost'] / 10,  # Convert price to millions
            "points_per_game": player['points_per_game'],
            "form": player['form'],
            "team": player['team'],
            "position": player['element_type'],
        })
    return pd.DataFrame(formatted_data)


# 2. Caching Helpers

def load_cache(file_name, expiry_time_minutes=60):
    cache_file = os.path.join(CACHE_DIR, file_name)
    
    if not os.path.exists(cache_file):
        return None

    with open(cache_file, 'r') as f:
        data = json.load(f)
        
    cache_time = datetime.fromisoformat(data['cache_time'])
    if datetime.now() - cache_time > timedelta(minutes=expiry_time_minutes):
        return None
    
    return data['data']

def save_cache(file_name, data):
    cache_file = os.path.join(CACHE_DIR, file_name)
    
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    cache_data = {
        'cache_time': datetime.now().isoformat(),
        'data': data,
    }
    
    with open(cache_file, 'w') as f:
        json.dump(cache_data, f)

def get_team_name(team_id):
    team_map = {
        1: 'Arsenal',
        2: 'Aston Villa',
        3: 'Bournemouth',
        4: 'Brentford',
        5: 'Chelsea',
        6: 'Crystal Palace',
        7: 'Everton',
        8: 'Fulham',
        9: 'Leeds United',
        10: 'Leicester City',
        11: 'Liverpool',
        12: 'Manchester City',
        13: 'Manchester United',
        14: 'Newcastle United',
        15: 'Nottingham Forest',
        16: 'Sheffield United',
        17: 'Southampton',
        18: 'Tottenham Hotspur',
        19: 'West Ham United',
        20: 'Wolverhampton Wanderers',
    }
    return team_map.get(team_id, 'Unknown')

def format_team(team):
    team_str = "\n".join([f"{player['name']} - {player['position']} - {player['price']}m" for player in team])
    return team_str

def filter_players_by_position(df, position):
    return df[df['position'] == position]

def filter_players_by_team(df, team):
    return df[df['team'] == team]

