import requests
import pandas as pd

BASE_URL = "https://fantasy.premierleague.com/api/"

r = requests.get(BASE_URL+'bootstrap-static/').json()

def fetch_player_data():
    # Extract player elements from the data
    players = r['elements']
    
    # Convert to DataFrame
    players_df = pd.DataFrame(players)
    
    # Add position and team data to the DataFrame (assuming teams and positions are already fetched)
    # Convert the DataFrame to a list of dictionaries (instead of DataFrame)
    players_list = players_df.to_dict(orient='records')
    
    # Fetch team and position data (assuming already defined or fetched previously)
    teams = r['teams']  # Teams data from API
    positions = r['element_types']  # Position data from API
    
    return players_list, teams, positions

def fetch_fixtures():
    """Fetch all fixtures for the season."""
    response = requests.get(f"{BASE_URL}/fixtures/")
    return response.json()

def fetch_player_summary(eid):
    """Fetch a player's remaining fixtures."""
    response = requests.get(f"{BASE_URL}/element-summary/{eid}/")
    return response.json()

def fetch_gameweek_stats(gw):
    """Fetch stats of all players in a given gameweek."""
    response = requests.get(f"{BASE_URL}/event/{gw}/live/")
    return response.json()

def fetch_manager_info(tid):
    """Fetch basic info about an FPL manager."""
    response = requests.get(f"{BASE_URL}/entry/{tid}/")
    return response.json()

def fetch_manager_history(tid):
    """Fetch FPL manager's history and chips."""
    response = requests.get(f"{BASE_URL}/entry/{tid}/history/")
    return response.json()

def fetch_manager_transfers(tid):
    """Fetch all transfers made by an FPL manager."""
    response = requests.get(f"{BASE_URL}/entry/{tid}/transfers/")
    return response.json()

def fetch_manager_picks(tid, gw):
    """Fetch squad picks of a manager for a specific gameweek."""
    response = requests.get(f"{BASE_URL}/entry/{tid}/event/{gw}/picks/")
    return response.json()

def fetch_league_standings(tid, page=1):
    """Fetch standings of a league, with pagination."""
    response = requests.get(f"{BASE_URL}/leagues-classic/{tid}/standings/", params={"page_standings": page})
    return response.json()

def get_gameweek_history(playerid):
    r = requests.get(BASE_URL + 'element-summary/' + str(player_id) + '/').json()
    
    # extract 'history' data from response into dataframe
    df = pd.json_normalize(r['history'])
    return df

def get_season_history(player_id):
    r = requests.get(BASE_URL + 'element-summary/' + str(player_id) + '/').json()
    
    # extract 'history_past' data from response into dataframe
    df = pd.json_normalize(r['history_past'])
    return df
