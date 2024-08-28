import requests
import pandas as pd
import numpy as np

class FPLTransferStrategy:
    def __init__(self, team_id):
        self.team_id = team_id
        self.api_endpoint = "https://fantasy.premierleague.com/api/bootstrap-static/"
        self.players = self.get_players()
        self.teams = self.get_teams()
        self.fixtures = self.get_fixtures()

    def get_players(self):
        response = requests.get(self.api_endpoint)
        data = response.json()
        elements = data["elements"]
        players = pd.DataFrame(elements)
        return players

    def get_teams(self):
        response = requests.get(self.api_endpoint)
        data = response.json()
        teams = data["teams"]
        teams_df = pd.DataFrame(teams)
        return teams_df

    def get_fixtures(self):
        response = requests.get(self.api_endpoint)
        data = response.json()
        fixtures = data["events"]
        fixtures_df = pd.DataFrame(fixtures)
        return fixtures_df

    def calculate_expected_points(self, player_id, fixture_id):
        player_stats = requests.get(f"https://fantasy.premierleague.com/api/element-summary/{player_id}/").json()
        player_stats = pd.DataFrame(player_stats["history"])
        avg_points = player_stats["total_points"].mean()
        fixture_data = self.fixtures[self.fixtures["id"] == fixture_id]
        expected_points = avg_points * (1 - fixture_data["difficulty"].iloc[0] / 10)
        return expected_points

    def calculate_expected_clean_sheets(self, team_id, fixture_id):
        team_stats = requests.get(f"https://fantasy.premierleague.com/api/teams/{team_id}/").json()
        team_stats = pd.DataFrame(team_stats["fixtures"])
        avg_clean_sheets = team_stats["clean_sheet"].mean()
        fixture_data = self.fixtures[self.fixtures["id"] == fixture_id]
        expected_clean_sheets = avg_clean_sheets * (1 - fixture_data["difficulty"].iloc[0] / 10)
        return expected_clean_sheets

    def calculate_expected_assists(self, player_id, fixture_id):
        player_stats = requests.get(f"https://fantasy.premierleague.com/api/element-summary/{player_id}/").json()
        player_stats = pd.DataFrame(player_stats["history"])
        avg_assists = player_stats["assists"].mean()
        fixture_data = self.fixtures[self.fixtures["id"] == fixture_id]
        expected_assists = avg_assists * (1 - fixture_data["difficulty"].iloc[0] / 10)
        return expected_assists

    def calculate_expected_goals(self, player_id, fixture_id):
        player_stats = requests.get(f"https://fantasy.premierleague.com/api/element-summary/{player_id}/").json()
        player_stats = pd.DataFrame(player_stats["history"])
        avg_goals = player_stats["goals_scored"].mean()
        fixture_data = self.fixtures[self.fixtures["id"] == fixture_id]
        expected_goals = avg_goals * (1 - fixture_data["difficulty"].iloc[0] / 10)
        return expected_goals

    def get_transfer_recommendations(self):
        recommendations = []
        for player in self.players.itertuples():
            expected_points = self.calculate_expected_points(player.id, player.fixture)
            expected_clean_sheets = self.calculate_expected_clean_sheets(player.team, player.fixture)
            expected_assists = self.calculate_expected_assists(player.id, player.fixture)
            expected_goals = self.calculate_expected_goals(player.id, player.fixture)
            if expected_points > 10 or expected_clean_sheets > 0.5 or expected_assists > 1 or expected_goals > 1:
                recommendations.append((player.name, expected_points, expected_clean_sheets, expected_assists, expected_goals))
        return recommendations

# Usage
strategy = FPLTransferStrategy(123456)
recommendations = strategy.get_transfer_recommendations()
for recommendation in recommendations:
    print(f"Player: {recommendation[0]}, Expected Points: {recommendation[1]}, Expected Clean Sheets: {recommendation[2]}, Expected Assists: {recommendation[3]}, Expected Goals: {recommendation[4]}")