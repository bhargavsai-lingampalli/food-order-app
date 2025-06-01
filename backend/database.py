from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection details
MONGODB_URI = os.getenv("MONGODB_URI")  # Replace with your MongoDB URI
DATABASE_NAME = "food_order_db"

# Create a MongoDB client
client = MongoClient(MONGODB_URI)

# Access the database
database = client[DATABASE_NAME]
