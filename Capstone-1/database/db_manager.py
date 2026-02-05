"""
Database Manager - Handles SQLite database operations and CSV data ingestion
"""
import sqlite3
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from config import DATABASE_PATH, CSV_DATA_PATH
from database.safety_validator import SafetyValidator


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.validator = SafetyValidator()
        self.logger = logging.getLogger(__name__)
        
        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database and load data from CSV if needed"""
        db_exists = Path(self.db_path).exists()
        
        if not db_exists:
            self.logger.info("Database not found. Creating new database from CSV...")
            self._load_csv_to_database()
        else:
            self.logger.info(f"Database found at {self.db_path}")
    
    def _load_csv_to_database(self):
        """Load car_prices.csv into SQLite database"""
        try:
            # Check if CSV exists
            if not CSV_DATA_PATH.exists():
                raise FileNotFoundError(f"CSV file not found: {CSV_DATA_PATH}")
            
            self.logger.info(f"Loading data from {CSV_DATA_PATH}...")
            
            # Read CSV with pandas
            df = pd.read_csv(CSV_DATA_PATH)
            
            # Clean column names (remove spaces, lowercase)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            
            # Write to SQLite
            df.to_sql('cars', conn, if_exists='replace', index=False)
            
            # Create indexes for common queries
            cursor = conn.cursor()
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_make ON cars(make)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_model ON cars(model)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_year ON cars(year)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_state ON cars(state)")
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Successfully loaded {len(df)} records into database")
            
        except Exception as e:
            self.logger.error(f"Error loading CSV to database: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Execute a SQL query with safety validation
        
        Args:
            query: SQL query to execute
            params: Optional parameters for parameterized queries
            
        Returns:
            Dictionary with 'success', 'data', 'error', and 'row_count' keys
        """
        # Validate query safety
        is_valid, error_msg = self.validator.validate_query(query)
        
        if not is_valid:
            self.logger.warning(f"Blocked unsafe query: {query}")
            return {
                'success': False,
                'data': None,
                'error': error_msg,
                'row_count': 0
            }
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            # Execute query
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Fetch results
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            data = [dict(row) for row in rows]
            
            conn.close()
            
            self.logger.info(f"Query executed successfully. Returned {len(data)} rows.")
            
            return {
                'success': True,
                'data': data,
                'error': None,
                'row_count': len(data)
            }
            
        except Exception as e:
            error_msg = f"Database error: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'data': None,
                'error': error_msg,
                'row_count': 0
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregated statistics about the database"""
        try:
            stats = {}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total records
            cursor.execute("SELECT COUNT(*) FROM cars")
            stats['total_records'] = cursor.fetchone()[0]
            
            # Price statistics
            cursor.execute("""
                SELECT 
                    AVG(sellingprice) as avg_price,
                    MIN(sellingprice) as min_price,
                    MAX(sellingprice) as max_price
                FROM cars
                WHERE sellingprice IS NOT NULL AND sellingprice > 0
            """)
            price_stats = cursor.fetchone()
            stats['avg_price'] = round(price_stats[0], 2) if price_stats[0] else 0
            stats['min_price'] = price_stats[1] if price_stats[1] else 0
            stats['max_price'] = price_stats[2] if price_stats[2] else 0
            
            # Top 5 makes by count
            cursor.execute("""
                SELECT make, COUNT(*) as count
                FROM cars
                GROUP BY make
                ORDER BY count DESC
                LIMIT 5
            """)
            stats['top_makes'] = [
                {'make': row[0], 'count': row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Top 5 models by count
            cursor.execute("""
                SELECT model, COUNT(*) as count
                FROM cars
                GROUP BY model
                ORDER BY count DESC
                LIMIT 5
            """)
            stats['top_models'] = [
                {'model': row[0], 'count': row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Condition distribution
            cursor.execute("""
                SELECT condition, COUNT(*) as count
                FROM cars
                WHERE condition IS NOT NULL
                GROUP BY condition
                ORDER BY count DESC
            """)
            stats['condition_distribution'] = [
                {'condition': row[0], 'count': row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Year range
            cursor.execute("SELECT MIN(year), MAX(year) FROM cars")
            year_range = cursor.fetchone()
            stats['year_range'] = {
                'min': year_range[0],
                'max': year_range[1]
            }
            
            conn.close()
            
            self.logger.info("Statistics retrieved successfully")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
    
    def get_table_info(self) -> Dict[str, Any]:
        """Get information about the database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get column information
            cursor.execute("PRAGMA table_info(cars)")
            columns = [
                {'name': row[1], 'type': row[2]} 
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            return {
                'table_name': 'cars',
                'columns': columns
            }
            
        except Exception as e:
            self.logger.error(f"Error getting table info: {e}")
            return {}
