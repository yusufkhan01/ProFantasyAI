from fpl_api import fetch_player_summary

def calculate_value_score(player):

    total_points = player["total_points"]
    now_cost = player["now_cost"] / 100.0  # Convert cost to millions
    form = float(player["form"])
    ict_index = float(player["ict_index"])


    points_per_game = float(player["points_per_game"]) if player["points_per_game"] != "0.0" else 0
    points_per_cost = total_points / now_cost

    """ summary = fetch_player_summary(player['id'])
    difficulty = get_fixtures_difficulties(summary) """


    # Combine weighted components
    value_score = (0.35 * points_per_cost) +(0.3 * form) + (0.25 * points_per_game) + (0.1 * ict_index)

    return value_score
