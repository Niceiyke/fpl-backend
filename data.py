import requests
# Constants
FPL_API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
FIXTURES_API_URL = "https://fantasy.premierleague.com/api/fixtures/"
TEAM_API_URL = "https://fantasy.premierleague.com/api/entry"
class FPLDataFetcher:
    @staticmethod
    def _fetch_data(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return None
        
    @staticmethod
    def _fetch_team_data(url,team_id,gameweek_id):
        headers={"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1; PRO 5 Build/LMY47D)", 'accept-language': 'en'}
        url=f"{url}/{team_id}/event/{gameweek_id}/picks/"
        print(url)
        try:
            response = requests.get(url,headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return None
    

    @staticmethod
    async def fetch_fpl_data():
        return FPLDataFetcher._fetch_data(FPL_API_URL)

    @staticmethod
    async def fetch_fixtures():
        return FPLDataFetcher._fetch_data(FIXTURES_API_URL)
    
    async def fetch_team_data(self,team_id,gameweek_id):
        return FPLDataFetcher._fetch_team_data(TEAM_API_URL,team_id,gameweek_id)
