import sqlite3
import json
from datetime import datetime

def init_db():
    connection = sqlite3.connect('data/sqlite3/user_interactions.db')
    cursor = connection.cursor()

    # Create a new table for user interactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            user_message TEXT,
            user_message_rephrased TEXT,
            bot_response TEXT,
            top_k_docs TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    connection.commit()
    connection.close()

def save_to_db(user_id, user_message, user_message_rephrased, bot_response, top_k_docs):
    connection = sqlite3.connect('data/sqlite3/user_interactions.db')
    cursor = connection.cursor()
    
    # Serialize the top_k_docs data to a JSON string
    # If top_k_docs is None, set top_k_docs_json to a representation of an empty list, otherwise serialize top_k_docs
    top_k_docs_json = json.dumps([]) if top_k_docs is None else json.dumps([doc.__dict__ for doc in top_k_docs])


    cursor.execute('''
        INSERT INTO interactions (user_id, user_message, user_message_rephrased, bot_response, top_k_docs)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, user_message, user_message_rephrased, bot_response, top_k_docs_json))

    connection.commit()
    connection.close()

def query_todays_chat_history(user_id):
    connection = sqlite3.connect('data/sqlite3/user_interactions.db')
    cursor = connection.cursor()

    # Get today's date as string in the format 'YYYY-MM-DD'
    today_str = datetime.now().strftime('%Y-%m-%d')

    cursor.execute('''
        SELECT user_message_rephrased, bot_response FROM interactions 
        WHERE user_id = ? AND date(timestamp) = ?
    ''', (user_id, today_str))

    chat_history = cursor.fetchall()
    connection.close()

    return chat_history
