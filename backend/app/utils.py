def get_player_position(position_id):
    # Map element_type to position
    position_mapping = {
        1: 'GK',
        2: 'DEF',
        3: 'MID',
        4: 'FWD'
    }
    return position_mapping.get(position_id, 'Unknown')


def get_team_name(team_id):
    team_map = {
        1: 'Arsenal',
        2: 'Aston Villa',
        3: 'Bournemouth',
        4: 'Brentford',
        5: 'Brighton',
        6: 'Chelsea',
        7: 'Crystal Palace',
        8: 'Everton',
        9: 'Fulham',
        10: 'Ipswich',
        11: 'Leicester City',
        12: 'Liverpool',
        13: 'Manchester City',
        14: 'Manchester United',
        15: 'Newcastle United',
        16: 'Nottingham Forest',
        17: 'Southampton',
        18: 'Tottenham Hotspur',
        19: 'West Ham United',
        20: 'Wolverhampton Wanderers',
    }
    return team_map.get(team_id, 'Unknown')
