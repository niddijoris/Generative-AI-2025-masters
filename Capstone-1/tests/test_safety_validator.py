"""
Tests for Safety Validator
"""
import pytest
from database.safety_validator import SafetyValidator


class TestSafetyValidator:
    """Test cases for SQL safety validation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.validator = SafetyValidator()
    
    def test_valid_select_query(self):
        """Test that valid SELECT queries pass validation"""
        query = "SELECT * FROM cars WHERE make = 'BMW'"
        is_valid, error = self.validator.validate_query(query)
        assert is_valid is True
        assert error == ""
    
    def test_delete_query_blocked(self):
        """Test that DELETE queries are blocked"""
        query = "DELETE FROM cars WHERE id = 1"
        is_valid, error = self.validator.validate_query(query)
        assert is_valid is False
        assert "DELETE" in error
    
    def test_drop_query_blocked(self):
        """Test that DROP queries are blocked"""
        query = "DROP TABLE cars"
        is_valid, error = self.validator.validate_query(query)
        assert is_valid is False
        assert "DROP" in error
    
    def test_update_query_blocked(self):
        """Test that UPDATE queries are blocked"""
        query = "UPDATE cars SET price = 0"
        is_valid, error = self.validator.validate_query(query)
        assert is_valid is False
        assert "UPDATE" in error
    
    def test_insert_query_blocked(self):
        """Test that INSERT queries are blocked"""
        query = "INSERT INTO cars VALUES (1, 'test')"
        is_valid, error = self.validator.validate_query(query)
        assert is_valid is False
        assert "INSERT" in error
    
    def test_truncate_query_blocked(self):
        """Test that TRUNCATE queries are blocked"""
        query = "TRUNCATE TABLE cars"
        is_valid, error = self.validator.validate_query(query)
        assert is_valid is False
        assert "TRUNCATE" in error
    
    def test_alter_query_blocked(self):
        """Test that ALTER queries are blocked"""
        query = "ALTER TABLE cars ADD COLUMN test VARCHAR(50)"
        is_valid, error = self.validator.validate_query(query)
        assert is_valid is False
        assert "ALTER" in error
    
    def test_empty_query(self):
        """Test that empty queries are rejected"""
        query = ""
        is_valid, error = self.validator.validate_query(query)
        assert is_valid is False
        assert "Empty query" in error
    
    def test_non_select_query(self):
        """Test that non-SELECT queries are rejected"""
        query = "SHOW TABLES"
        is_valid, error = self.validator.validate_query(query)
        assert is_valid is False
        assert "Only SELECT" in error
    
    def test_sql_injection_attempt(self):
        """Test that SQL injection patterns are detected"""
        query = "SELECT * FROM cars; DELETE FROM cars"
        is_valid, error = self.validator.validate_query(query)
        assert is_valid is False
    
    def test_complex_select_query(self):
        """Test that complex SELECT queries pass"""
        query = """
            SELECT make, model, AVG(sellingprice) as avg_price
            FROM cars
            WHERE year > 2010
            GROUP BY make, model
            ORDER BY avg_price DESC
            LIMIT 10
        """
        is_valid, error = self.validator.validate_query(query)
        assert is_valid is True
        assert error == ""
    
    def test_case_insensitive_blocking(self):
        """Test that dangerous keywords are blocked regardless of case"""
        queries = [
            "delete from cars",
            "DELETE FROM cars",
            "DeLeTe FrOm cars"
        ]
        
        for query in queries:
            is_valid, error = self.validator.validate_query(query)
            assert is_valid is False
            assert "DELETE" in error.upper()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
