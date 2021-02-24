import time
import requests
import pymongo
import pandas as pd
import pickle

from pymongo import MongoClient
try:
    client = MongoClient('localhost', 27017)
    print('Connected Successfully!')
except:
    print('Could not connect to MongoDB')
db = client['fraud_predictions']
entries = db['entries']


class EventAPIClient:
    """Realtime Events API Client"""

    def __init__(self, first_sequence_number=0,
                 api_url='https://hxobin8em5.execute-api.us-west-2.amazonaws.com/api/',
                 api_key='vYm9mTUuspeyAWH1v-acfoTlck-tCxwTw9YfCynC',
                 db=None,
                 interval=30):
        """Initialize the API client."""
        self.next_sequence_number = first_sequence_number
        self.api_url = api_url
        self.api_key = api_key
        self.db = db
        self.interval = 30

    def save_to_database(self, row):
        """Save a data row to the database."""
        rf = pickle.load(open('rf_2feature_model.pkl', 'rb'))
        if len(row['previous_payouts']) == 0 or len(row['ticket_types']) == 0:
            row['fraud_pred'] = 1
        else:
            d = {'previous_payouts': [len(row['previous_payouts'])], 'ticket_types': [len(row['ticket_types'])]}
            X = pd.DataFrame(data=d)
            pred = rf.predict_proba(X)
            row['fraud_pred'] = pred[0][1]
            print(type(row))
#             print(row['fraud_pred'])
            entries.insert_one(row)


    def get_data(self):
        """Fetch data from the API."""
        payload = {'api_key': self.api_key,
                   'sequence_number': self.next_sequence_number}
        response = requests.post(self.api_url, json=payload)
        data = response.json()
        self.next_sequence_number = data['_next_sequence_number']
        return data['data']

    def collect(self, interval=30):
        """Check for new data from the API periodically."""
        while True:
            print("Requesting data...")
            data = self.get_data()
            if data:
                print("Saving...")
                for row in data:
                    self.save_to_database(row)
            else:
                print("No new data received.")
            print(f"Waiting {interval} seconds...")
            time.sleep(interval)


def main():
    """Collect events every 30 seconds."""
    client = EventAPIClient()
    client.collect()


if __name__ == "__main__":
    main()
