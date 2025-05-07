import pandas as pd
import requests


class Payments:
    def __init__(self, headers, base_url):
        self.headers = headers
        self.base_url = base_url

    def get(self) -> pd.DataFrame:
        resp = requests.get(f"{self.base_url}employeepayment/payments", headers=self.headers, timeout=3600)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data)

        resp = requests.get(f"{self.base_url}payment/payments", headers=self.headers, timeout=3600)
        data = resp.json()
        df_payment_types = pd.DataFrame(data)
        df = pd.merge(df, df_payment_types, how='left', left_on='paymentReference', right_on='reference', suffixes=('', '_payment_type'))

        return df

    def get_types(self) -> pd.DataFrame:
        resp = requests.get(f"{self.base_url}payment/payments", headers=self.headers, timeout=3600)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data)

        return df

    def new(self, data) -> requests.Response:
        resp = requests.post(url=f"{self.base_url}employeepayment/payments",
                             headers=self.headers,
                             json=data,
                             timeout=3600)
        resp.raise_for_status()

        return resp

    def edit(self, data) -> requests.Response:
        resp = requests.put(url=f"{self.base_url}employeepayment/payments",
                            headers=self.headers,
                            json=data,
                            timeout=3600)
        resp.raise_for_status()

        return resp