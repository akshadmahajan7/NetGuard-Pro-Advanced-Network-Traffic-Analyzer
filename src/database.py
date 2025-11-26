import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load credentials
load_dotenv()

class DBManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Establishes connection to MySQL with Auto-Reconnect"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASS', ''),
                database=os.getenv('DB_NAME', 'netguard_db'),
                autocommit=True  # <--- CRITICAL: Ensures data is saved immediately
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                self.create_table()
        except Error as e:
            print(f"[!] Database Connection Error: {e}")

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS packet_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            src_ip VARCHAR(45),
            dst_ip VARCHAR(45),
            protocol VARCHAR(10),
            length INT,
            flags VARCHAR(20),
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            self.cursor.execute(query)
        except Error as e:
            print(f"[!] Table Creation Error: {e}")

    def log_packet(self, src, dst, proto, length, flags=""):
        # FIX: We removed 'timestamp' from Python. 
        # We use NOW() in SQL so the DB time is always perfectly synced.
        query = """
        INSERT INTO packet_logs (src_ip, dst_ip, protocol, length, flags, captured_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        """
        # Force Clean Protocol String (Remove spaces/newlines)
        clean_proto = str(proto).strip().upper()
        
        args = (src, dst, clean_proto, length, str(flags))
        
        try:
            if not self.connection.is_connected():
                self.connect()
            self.cursor.execute(query, args)
        except Error as e:
            print(f"[!] Insert Error: {e}")

    def close(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
