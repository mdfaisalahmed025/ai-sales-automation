import mysql.connector
from mysql.connector import Error
from config import config   # <-- your config module

def get_db_connection():
    """Create and return a MySQL connection object."""
    return mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
    )

def test_connection():
    """Try to connect, ping the server, and close cleanly."""
    try:
        conn = get_db_connection()
        # `is_connected()` returns True only after a successful handshake.
        if conn.is_connected():
            # `ping()` forces a round‑trip to the server – good sanity check.
            conn.ping(reconnect=False, attempts=3, delay=2)
            print("✅ Connection succeeded!")
            print(f"  Server version : {conn.get_server_info()}")
            print(f"  Current schema : {conn.database}")
        else:
            print("❌ `is_connected()` returned False – something went wrong.")
    except Error as e:
        # `Error` is the base class for all mysql‑connector‑python exceptions.
        print("❌ Could NOT connect to MySQL.")
        print(f"   Error type   : {type(e).__name__}")
        print(f"   Error code   : {e.errno if hasattr(e, 'errno') else 'N/A'}")
        print(f"   Error msg    : {e.msg if hasattr(e, 'msg') else str(e)}")
    finally:
        # Always close the connection if it was created.
        try:
            if conn.is_connected():
                conn.close()
                print("🔌 Connection closed.")
        except NameError:
            # `conn` was never assigned because the `try` block failed early.
            pass

if __name__ == "__main__":
    test_connection()