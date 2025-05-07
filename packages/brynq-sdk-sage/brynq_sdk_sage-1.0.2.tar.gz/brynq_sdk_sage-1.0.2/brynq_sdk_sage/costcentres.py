import pandas as pd
import requests


class Costcentres:
    def __init__(self, headers, base_url):
        self.headers = headers
        self.base_url = base_url

    def get(self) -> pd.DataFrame:
        resp = requests.get(f"{self.base_url}costcentre/costcentre", headers=self.headers, timeout=3600)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data)

        return df

    def new(self, data) -> requests.Response:
        resp = requests.post(url=f"{self.base_url}costcentre/costcentre",
                             headers=self.headers,
                             json=data,
                             timeout=3600)
        resp.raise_for_status()

        return resp

    def edit(self, data) -> requests.Response:
        resp = requests.put(url=f"{self.base_url}costcentre/costcentre",
                            headers=self.headers,
                            json=data,
                            timeout=3600)
        resp.raise_for_status()

        return resp
