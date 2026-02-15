import pymongo
import sys

def test_connection():
    uri = "mongodb+srv://harshithpharshithp438_db_user:0pTOCZlWbnxs4ank@voters.h7rktd3.mongodb.net/college_voting_db?appName=Voters"
    print(f"Attempting to connect to MongoDB Atlas...")
    
    try:
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        print("SUCCESS: Connection to MongoDB Atlas established!")
        
        db = client.college_voting_db
        print(f"Connected to database: {db.name}")
        
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(f"FAILURE: Could not connect to MongoDB (Timeout): {e}")
    except Exception as e:
        print(f"FAILURE: An error occurred: {e}")

if __name__ == "__main__":
    test_connection()
