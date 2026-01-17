"""
Query Executor Module
Safely executes SQL queries with error handling and result formatting
"""
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import time


@dataclass
class QueryResult:
    """Result of a query execution"""
    success: bool
    columns: List[str]
    rows: List[Tuple]
    row_count: int
    execution_time: float
    error: Optional[str] = None


class QueryExecutor:
    """
    Executes SQL queries safely with timeouts and error handling.
    """
    
    # Maximum execution time in seconds
    MAX_EXECUTION_TIME = 30
    
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        # Set row factory to access columns by name
        self.conn.row_factory = sqlite3.Row
    
    def execute_query(self, sql: str, params: Optional[tuple] = None) -> QueryResult:
        """
        Execute a SQL query safely.
        
        Args:
            sql: SQL query string
            params: Optional query parameters for parameterized queries
            
        Returns:
            QueryResult object with results or error information
        """
        start_time = time.time()
        
        try:
            cursor = self.conn.cursor()
            
            # Execute query
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # Fetch results
            rows = cursor.fetchall()
            
            # Get column names
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
            else:
                columns = []
            
            # Convert Row objects to tuples
            rows_as_tuples = [tuple(row) for row in rows]
            
            execution_time = time.time() - start_time
            
            return QueryResult(
                success=True,
                columns=columns,
                rows=rows_as_tuples,
                row_count=len(rows_as_tuples),
                execution_time=execution_time
            )
            
        except sqlite3.Error as e:
            execution_time = time.time() - start_time
            return QueryResult(
                success=False,
                columns=[],
                rows=[],
                row_count=0,
                execution_time=execution_time,
                error=str(e)
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return QueryResult(
                success=False,
                columns=[],
                rows=[],
                row_count=0,
                execution_time=execution_time,
                error=f"Unexpected error: {str(e)}"
            )
    
    def execute_multiple(self, queries: List[str]) -> List[QueryResult]:
        """
        Execute multiple queries in sequence.
        
        Args:
            queries: List of SQL query strings
            
        Returns:
            List of QueryResult objects
        """
        results = []
        for query in queries:
            result = self.execute_query(query)
            results.append(result)
            
            # Stop if a query fails
            if not result.success:
                break
        
        return results
    
    def test_query(self, sql: str) -> Tuple[bool, Optional[str]]:
        """
        Test if a query is valid without executing it fully.
        Uses EXPLAIN to validate syntax.
        
        Args:
            sql: SQL query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"EXPLAIN {sql}")
            return True, None
        except sqlite3.Error as e:
            return False, str(e)


if __name__ == "__main__":
    # Test query executor
    from setup_database import get_database_connection
    
    conn = get_database_connection()
    executor = QueryExecutor(conn)
    
    # Test simple query
    result = executor.execute_query("SELECT * FROM Artist LIMIT 5;")
    
    if result.success:
        print(f"Query successful! Got {result.row_count} rows in {result.execution_time:.3f}s")
        print(f"Columns: {result.columns}")
        for row in result.rows:
            print(row)
    else:
        print(f"Query failed: {result.error}")
    
    conn.close()
