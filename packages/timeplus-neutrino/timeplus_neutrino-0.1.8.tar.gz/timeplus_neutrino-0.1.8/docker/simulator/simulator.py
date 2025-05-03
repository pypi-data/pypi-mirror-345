import os
import random
import time
from faker import Faker
import pymongo
import psycopg2
import pandas as pd
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

mongo_host = os.getenv("MONGO_HOST", "mongodb")
postgres_host = os.getenv("POSTGRES_HOST", "postgres")

# MongoDB connection
mongo_client = pymongo.MongoClient(f"mongodb://{mongo_host}:27017/")
mongo_db = mongo_client["lumi_data"]
unstructured_data_collection = mongo_db["unstructured_data"]

# PostgreSQL connection
pg_conn = psycopg2.connect(
    dbname="lumi_credit",
    user="debezium",
    password="dbz",
    host=f"{postgres_host}"
)
pg_cursor = pg_conn.cursor()

# Function to generate fake customer data
def generate_customer_data():
    return {
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "address": fake.address()
    }

# Function to generate structured data (from a bank API)
def generate_structured_data(customer_id):
    return {
        "customer_id": customer_id,
        "bank_name": fake.company(),
        "credit_score": random.randint(300, 850),
        "outstanding_debt": round(random.uniform(0, 100000), 2),
        "last_updated": fake.date_between(start_date='-2y', end_date='today')
    }

# Function to generate unstructured data (from a third-party service provider)
def generate_unstructured_data(customer_id):
    return {
        "customer_id": customer_id,
        "raw_data": {
            "transaction_history": [
                {
                    "date": datetime.combine(fake.date_this_year(), datetime.min.time()),  # Convert date to datetime
                    "amount": round(random.uniform(10, 1000), 2)
                } for _ in range(random.randint(1, 10))
            ],
            "social_media_activity": {
                "platform": random.choice(["Twitter", "Facebook", "LinkedIn"]),
                "activity_score": random.randint(1, 100)
            },
            "miscellaneous": {
                "notes": fake.sentence(),
                "risk_flags": random.choice(["Low", "Medium", "High"])
            }
        }
    }

# Simulate the process
def simulate_loan_request():
    # Step 1: Generate customer data
    customer_data = generate_customer_data()
    
    # Insert into PostgreSQL Customers table
    pg_cursor.execute("""
        INSERT INTO Customers (name, email, phone, address)
        VALUES (%s, %s, %s, %s) RETURNING customer_id
    """, (customer_data["name"], customer_data["email"], customer_data["phone"], customer_data["address"]))
    customer_id = pg_cursor.fetchone()[0]
    pg_conn.commit()

    # Step 2: Generate structured data (from a bank API)
    structured_data = generate_structured_data(customer_id)
    
    # Insert into PostgreSQL Credit_History table
    pg_cursor.execute("""
        INSERT INTO Credit_History (customer_id, bank_name, credit_score, outstanding_debt, last_updated)
        VALUES (%s, %s, %s, %s, %s)
    """, (structured_data["customer_id"], structured_data["bank_name"], structured_data["credit_score"], 
          structured_data["outstanding_debt"], structured_data["last_updated"]))
    pg_conn.commit()

    # Step 3: Generate unstructured data (from a third-party service provider)
    unstructured_data = generate_unstructured_data(customer_id)
    
    # Insert into MongoDB
    unstructured_data_collection.insert_one(unstructured_data)

    print(f"Simulated loan request for customer ID {customer_id}")

# Run the simulation
'''
for _ in range(10):  # Simulate 10 loan requests
    simulate_loan_request()
'''

while True:
    simulate_loan_request()
    time.sleep(2)

# Close connections
pg_cursor.close()
pg_conn.close()
mongo_client.close()