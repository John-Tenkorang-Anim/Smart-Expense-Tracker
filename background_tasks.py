import time
from db import get_transactions
from ml_model import train_model

def retrain_if_needed():
    while True:
        transactions = get_transactions()
        
        if len(transactions) % 100 == 0 and len(transactions) > 0:
            print("Retraining model with new transactions...")
            train_model()
        
        time.sleep(3600)  
