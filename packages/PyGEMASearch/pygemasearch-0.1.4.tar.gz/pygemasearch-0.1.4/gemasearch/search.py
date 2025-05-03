import requests

from gemasearch.data import Werk


class GemaMusicSearch:
    def __init__(self):
        self.session = None
        self.api_url = "https://www.gema.de/portal/api/public/cloud/v1/main/repertoiresuche/suche"
        self.init_url = "https://www.gema.de/portal/config/frontend"

        if not self._initialize_session():
            print('Could not initialize session. This package might need some updating.')

    def _initialize_session(self):

        if self.session is None:
            self.session = requests.Session()
            # Load initial page to get session data

            cookie_headers = {
                "Host": "www.gema.de",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:136.0) Gecko/20100101 Firefox/136.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "DNT": "1",
                "Sec-GPC": "1",
                "Connection": "keep-alive",
                "Referer": "https://www.gema.de/portal/app/repertoiresuche/werksuche",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers"
            }

            r = self.session.get(self.init_url, headers=cookie_headers)
            if r.status_code == 200:
                api_key = r.json().get('apiKey', None)

                self.session.headers.update({
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:136.0) Gecko/20100101 Firefox/136.0",
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
                    "Content-Language": "de",
                    "API_KEY": api_key,
                    "Active-Role": "OPAL_NUTZER",
                    "Content-Type": "application/json",
                    "Origin": "https://www.gema.de",
                    "Referer": "https://www.gema.de/portal/app/repertoiresuche/werksuche",
                    "Connection": "keep-alive"
                })
                return True
            else:
                print('Could not fetch api key. Aborting!')
                self.session = None
                return False

        # Session is initialized and active
        return True

    def search(self, search_string: str, page: int = 0, page_size: int = 50, fuzzy_search=True):
        if not self._initialize_session():
            print('No active session!')
            return None

        payload = {
            "queryCriteria": [{
                "field": "WERK_TITEL",
                "matchOperator": "FUZZY" if fuzzy_search else 'EXACTLY',
                "value": search_string
            }],
            "filters": {},
            "pagination": {
                "page": page,
                "pageSize": page_size
            }
        }
        try:
            response = self.session.post(self.api_url, json=payload)
            response.raise_for_status()
            ret_list = list()
            for titel in response.json().get('titel', []):
                ret_list.append(Werk(titel))
            return ret_list
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def search_werknummer(self, number_string: str, page: int = 0, page_size: int = 50):
        if not self._initialize_session():
            print('No active session!')
            return None

        if '-' in number_string:
            field = 'WERK_FASSUNGSNUMMER'
        else:
            field = 'WERK_NUMMER'

        payload = {
            "queryCriteria": [
                {
                    "field": field,
                    "matchOperator": "EXACTLY",
                    "value": number_string
                }
            ],
            "filters": {},
            "pagination": {
                "page": page,
                "pageSize": page_size
            }
        }
        try:
            response = self.session.post(self.api_url, json=payload)
            response.raise_for_status()
            ret_list = list()
            for titel in response.json().get('titel', []):
                ret_list.append(Werk(titel))
            return ret_list
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def search_isrc(self, isrc: str, page: int = 0, page_size: int = 50):
        if not self._initialize_session():
            print('No active session!')
            return None

        payload = {
            "queryCriteria": [
                {
                    "field": "WERK_ISRC",
                    "matchOperator": "EXACTLY",
                    "value": isrc
                }
            ],
            "filters": {},
            "pagination": {
                "page": page,
                "pageSize": page_size
            }
        }
        try:
            response = self.session.post(self.api_url, json=payload)
            response.raise_for_status()
            ret_list = list()
            for titel in response.json().get('titel', []):
                ret_list.append(Werk(titel))
            return ret_list
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
