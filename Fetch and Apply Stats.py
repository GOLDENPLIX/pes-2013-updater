def fetch_player_stats(player_name):
    url = f"https://api.example.com/players/{player_name}/stats"
    response = requests.get(url)
    if response.status_code == 200:
        stats = response.json()
        return stats
    return None

def apply_player_stats(player_data, pes_db):
    for player in player_data:
        pes_db.loc[pes_db['PlayerName'] == player['name'], 'OverallRating'] = player['overall']
    pes_db.to_csv("updated_pes_db.csv", index=False)
