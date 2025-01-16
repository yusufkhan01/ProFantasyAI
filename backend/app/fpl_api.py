import requests

BASE_URL = "https://fantasy.premierleague.com/api"

def fetch_all_players():
    """Fetch all players, teams, and global gameweek summaries."""
    response = requests.get(f"{BASE_URL}/bootstrap-static/")
    return response.json()

def fetch_player_data():
    data = fetch_all_players()
    players = []
    
    for player in data['elements']:
        players.append({
            "id": player["id"],
            "name": player["web_name"],
            "team": player["team"],
            "position": player["element_type"],  # 1 = GK, 2 = DEF, 3 = MID, 4 = FWD
            "price": player["now_cost"] / 10.0,  # price in millions
            "form": player["form"],  # Current form
            "total_points": player["total_points"],  # Total points scored
        })
    
    return players


def fetch_fixtures():
    """Fetch all fixtures for the season."""
    response = requests.get(f"{BASE_URL}/fixtures/")
    return response.json()

def fetch_player_summary(eid):
    """Fetch a player's remaining and past fixtures."""
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
