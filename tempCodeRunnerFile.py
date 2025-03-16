
# Connect to SQLite database
DB_FILE = "earnlink.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
