import os
import sqlite3
import threading
from datetime import datetime
from app.core.config import Config
from app.core.logger import db_logger

DATABASE_DIR = Config.DATABASE_DIR
DATABASE_PATH = Config.DATABASE_PATH
SCHEMA_PATH = Config.SCHEMA_PATH

local_storage = threading.local()

def init_db():
    """Initializes the database using schema.sql and seeds default customer data if empty."""
    db_logger.info(f"Initializing database at path: {Config.DATABASE_PATH}")
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    os.makedirs(Config.UPLOADS_DIR, exist_ok=True)
    os.makedirs(Config.EXPORTS_DIR, exist_ok=True)
    
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        
        with open(Config.SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Safely execute DDL statements individually to avoid executescript thread locks or OperationalError on Streamlit Cloud
        for statement in schema_sql.split(';'):
            stmt_clean = statement.strip()
            if stmt_clean:
                lines = [l for l in stmt_clean.split('\n') if not l.strip().startswith('--')]
                cleaned_stmt = '\n'.join(lines).strip()
                if cleaned_stmt:
                    try:
                        conn.execute(cleaned_stmt)
                    except sqlite3.OperationalError as op_err:
                        if 'already exists' not in str(op_err).lower():
                            db_logger.warning(f"Ignored DDL operational notice: {op_err}")
        
        # Run migrations for INVENTORY table if new columns are missing
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(INVENTORY)")
        columns = [col[1] for col in cursor.fetchall()]
        
        new_cols = {
            "purc_orders_pending": "REAL DEFAULT 0",
            "sale_orders_due": "REAL DEFAULT 0",
            "nett_available": "REAL DEFAULT 0",
            "reorder_level": "REAL DEFAULT 0",
            "short_fall": "REAL DEFAULT 0",
            "min_reorder_qty": "REAL DEFAULT 0",
            "order_to_be_placed": "REAL DEFAULT 0"
        }
        
        for col_name, col_type in new_cols.items():
            if col_name not in columns:
                db_logger.info(f"Applying migration: ALTER TABLE INVENTORY ADD COLUMN {col_name}")
                cursor.execute(f"ALTER TABLE INVENTORY ADD COLUMN {col_name} {col_type};")
        
        # Seed 1 Demo Customer
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM CUSTOMERS")
        if cursor.fetchone()[0] == 0:
            now_str = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO CUSTOMERS (name, discount_percentage, gst_number, payment_terms, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                ("Demo1", 10.0, "27DEMO11234A1Z1", Config.DEFAULT_PAYMENT_TERMS, now_str, now_str)
            )
            db_logger.info("Seeded initial default Demo1 customer profile.")
            
        # Check if PRODUCT_COSTS is empty or incomplete, and reseed catalog if needed
        cursor.execute("SELECT COUNT(*) FROM PRODUCT_COSTS")
        cost_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM PRODUCTS")
        prod_count = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        
        if prod_count == 0 or cost_count == 0:
            reseed_database_from_excel()
            return
            
        db_logger.info("Database initialization completed successfully.")
    except Exception as ex:
        db_logger.error(f"Failed to initialize database: {ex}", exc_info=True)
        raise ex

def reseed_database_from_excel():
    """Clears stale products, costs, and inventory, then re-imports fresh from group order status.xlsx."""
    if not os.path.exists(Config.STOCK_SOURCE_PATH):
        db_logger.warning(f"Stock source path '{Config.STOCK_SOURCE_PATH}' not found for reseeding.")
        return False
    try:
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = OFF;")
        conn.execute("DELETE FROM PRODUCT_COSTS;")
        conn.execute("DELETE FROM INVENTORY;")
        conn.execute("DELETE FROM PRODUCTS;")
        conn.commit()
        conn.close()
        
        from app.services.import_service import ImportService
        db_logger.info(f"Seeding catalog costs & stock from {Config.STOCK_SOURCE_PATH}...")
        ImportService.import_costs(Config.STOCK_SOURCE_PATH, sheet_name="PRICE LIST", imported_by="System Initializer")
        ImportService.import_inventory(Config.STOCK_SOURCE_PATH, sheet_name="Stock Group Reorder Status", imported_by="System Initializer")
        db_logger.info("Catalog re-seeded successfully.")
        return True
    except Exception as e:
        db_logger.error(f"Failed to reseed database from Excel: {e}", exc_info=True)
        return False

def get_db_connection():
    """Gets a raw sqlite3 connection with standard settings."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    """Gets database connection using thread-local storage."""
    db = getattr(local_storage, 'database', None)
    if db is None:
        db = local_storage.database = get_db_connection()
    return db

def close_connection(exception=None):
    """Closes the context connection if active."""
    db = getattr(local_storage, 'database', None)
    if db is not None:
        db.close()
        local_storage.database = None

def query_db(query, args=(), one=False):
    """Utility to query the database and return dictionary rows."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Utility to execute a modifying command and commit it, returns lastrowid."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id

def execute_transaction(queries_with_args):
    """Executes a list of (query, args) tuples inside a single transaction."""
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN IMMEDIATE TRANSACTION;")
        for query, args in queries_with_args:
            cur.execute(query, args)
        conn.commit()
        db_logger.debug(f"Executed transaction containing {len(queries_with_args)} queries.")
    except Exception as e:
        conn.rollback()
        db_logger.error(f"Transaction failed, changes rolled back: {e}", exc_info=True)
        raise e
    finally:
        cur.close()
