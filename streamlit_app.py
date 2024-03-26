import os
import streamlit as st
import sqlite3
from file_checker import checkFile

# Function to create a database connection
def create_connection():
    conn = sqlite3.connect("user_database.db")
    return conn

# Function to initialize the user table if it doesn't exist
def initialize_user_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()

# Function to insert a new user into the database
def register(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# Function to check login credentials
def authenticate(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Function to check if the user is logged in
def is_logged_in():
    return "user_id" in st.session_state

# Streamlit app title and configuration
st.set_page_config(page_title="Malware Detection App", page_icon="🔒", layout="wide")
st.title("Malware Detection")

# Check if the user is logging in or registering
if st.checkbox("Register new user"):
    st.sidebar.title("Register")
    new_username = st.sidebar.text_input("New Username")
    new_password = st.sidebar.text_input("New Password", type="password")
    confirm_password = st.sidebar.text_input("Confirm Password", type="password")
    register_button = st.sidebar.button("Register")

    if register_button:
        if new_password == confirm_password:
            register(new_username, new_password)
            st.sidebar.success("Registration successful! You can now log in.")
        else:
            st.sidebar.error("Passwords do not match. Please try again.")
else:
    # Initialize the user table if it doesn't exist
    conn = create_connection()
    initialize_user_table(conn)
    conn.close()

    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        if authenticate(username, password):
            st.sidebar.success("Login successful!")
            st.session_state.user_id = 1  # Placeholder user_id; you can use the actual user ID from the database
        else:
            st.sidebar.error("Invalid credentials. Please try again.")

# Main application logic
if is_logged_in():
    st.subheader("Try yourself:-")
    file = st.file_uploader("Upload a file to check for malwares:", accept_multiple_files=True)
    
    if file:
        with st.spinner("Checking..."):
            for i in file:
                open('malwares/tempFile', 'wb').write(i.getvalue())
                legitimate = checkFile("malwares/tempFile")
                os.remove("malwares/tempFile")
                
                if legitimate:
                    st.write(f"File {i.name} seems *Malwares not detected*")
                else:
                    st.markdown(f"File {i.name} is probably a **MALWARE**!!!")
else:
    st.warning("Please log in to use the application.")
