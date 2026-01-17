"""
SQL Generation Module with Safety Validation
Generates safe, efficient SQL queries with built-in validation
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import re


@dataclass
class QueryPlan:
    """Represents a planned SQL query with metadata"""
    intent: str  # What the query is trying to accomplish
    tables: List[str]  # Tables involved
    columns: List[str]  # Columns to select
    joins: List[str]  # JOIN conditions
    filters: List[str]  # WHERE conditions
    grouping: Optional[str]  # GROUP BY clause
    ordering: Optional[str]  # ORDER BY clause
    limit: Optional[int]  # LIMIT value


class SQLGenerator:
    """
    Generates safe, efficient SQL queries.
    Enforces read-only operations and resource-conscious practices.
    """
    
    # Forbidden SQL keywords (write operations)
    FORBIDDEN_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE',
        'TRUNCATE', 'REPLACE', 'PRAGMA', 'ATTACH', 'DETACH'
    }
    
    # Default LIMIT for queries without explicit limits
    DEFAULT_LIMIT = 100
    
    def __init__(self):
        pass
    
    def validate_query(self, sql: str) -> tuple[bool, Optional[str]]:
        """
        Validate that a SQL query is safe to execute.
        
        Args:
            sql: SQL query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        sql_upper = sql.upper()
        
        # Check for forbidden keywords
        for keyword in self.FORBIDDEN_KEYWORDS:
            if re.search(rf'\b{keyword}\b', sql_upper):
                return False, f"Forbidden operation detected: {keyword}. Only SELECT queries are allowed."
        
        # Check for SELECT * without LIMIT
        if 'SELECT *' in sql_upper:
            if 'LIMIT' not in sql_upper:
                return False, "SELECT * must include a LIMIT clause to prevent large result sets."
        
        # Ensure it's a SELECT query
        if not sql_upper.strip().startswith('SELECT') and not sql_upper.strip().startswith('WITH'):
            return False, "Only SELECT queries (including CTEs with WITH) are allowed."
        
        return True, None
    
    def build_query_from_plan(self, plan: QueryPlan) -> str:
        """
        Build a SQL query from a query plan.
        
        Args:
            plan: QueryPlan object
            
        Returns:
            SQL query string
        """
        query_parts = []
        
        # SELECT clause
        if plan.columns:
            columns_str = ", ".join(plan.columns)
        else:
            columns_str = "*"
        
        # FROM clause - start with first table
        if not plan.tables:
            raise ValueError("Query plan must specify at least one table")
        
        query_parts.append(f"SELECT {columns_str}")
        query_parts.append(f"FROM {plan.tables[0]}")
        
        # JOIN clauses
        if plan.joins:
            query_parts.extend(plan.joins)
        
        # WHERE clause
        if plan.filters:
            filters_str = " AND ".join(plan.filters)
            query_parts.append(f"WHERE {filters_str}")
        
        # GROUP BY clause
        if plan.grouping:
            query_parts.append(f"GROUP BY {plan.grouping}")
        
        # ORDER BY clause
        if plan.ordering:
            query_parts.append(f"ORDER BY {plan.ordering}")
        
        # LIMIT clause (add default if not specified and no grouping)
        if plan.limit is not None:
            query_parts.append(f"LIMIT {plan.limit}")
        elif not plan.grouping and "COUNT" not in columns_str.upper():
            # Add default limit for non-aggregated queries
            query_parts.append(f"LIMIT {self.DEFAULT_LIMIT}")
        
        query = "\n".join(query_parts) + ";"
        
        # Validate the generated query
        is_valid, error = self.validate_query(query)
        if not is_valid:
            raise ValueError(f"Generated query failed validation: {error}")
        
        return query
    
    def optimize_query(self, sql: str) -> str:
        """
        Optimize a SQL query for safety and efficiency.
        
        Args:
            sql: Original SQL query
            
        Returns:
            Optimized SQL query
        """
        # Remove extra whitespace
        sql = re.sub(r'\s+', ' ', sql).strip()
        
        # Ensure semicolon at end
        if not sql.endswith(';'):
            sql += ';'
        
        # Add LIMIT if missing and it's a simple SELECT
        if 'LIMIT' not in sql.upper() and 'GROUP BY' not in sql.upper():
            sql = sql.rstrip(';')
            sql += f' LIMIT {self.DEFAULT_LIMIT};'
        
        return sql
    
    def generate_meta_query(self, query_type: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate meta-queries for schema introspection.
        
        Args:
            query_type: Type of meta query ('tables', 'schema', 'row_count', etc.)
            params: Additional parameters for the query
            
        Returns:
            SQL query string
        """
        params = params or {}
        
        if query_type == 'tables':
            return """
                SELECT name as table_name, type
                FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name;
            """
        
        elif query_type == 'schema':
            table_name = params.get('table_name')
            if not table_name:
                raise ValueError("table_name required for schema query")
            return f"PRAGMA table_info({table_name});"
        
        elif query_type == 'foreign_keys':
            table_name = params.get('table_name')
            if not table_name:
                raise ValueError("table_name required for foreign_keys query")
            return f"PRAGMA foreign_key_list({table_name});"
        
        elif query_type == 'row_count':
            table_name = params.get('table_name')
            if not table_name:
                raise ValueError("table_name required for row_count query")
            return f"SELECT COUNT(*) as row_count FROM {table_name};"
        
        elif query_type == 'sample_values':
            table_name = params.get('table_name')
            column_name = params.get('column_name')
            limit = params.get('limit', 10)
            if not table_name or not column_name:
                raise ValueError("table_name and column_name required for sample_values query")
            return f"""
                SELECT DISTINCT {column_name}
                FROM {table_name}
                WHERE {column_name} IS NOT NULL
                LIMIT {limit};
            """
        
        else:
            raise ValueError(f"Unknown meta query type: {query_type}")


if __name__ == "__main__":
    # Test SQL generator
    generator = SQLGenerator()
    
    # Test validation
    print("Testing validation...")
    
    valid_query = "SELECT * FROM Customer LIMIT 10;"
    is_valid, error = generator.validate_query(valid_query)
    print(f"Valid query: {is_valid} - {valid_query}")
    
    invalid_query = "DELETE FROM Customer WHERE CustomerId = 1;"
    is_valid, error = generator.validate_query(invalid_query)
    print(f"Invalid query: {is_valid} - {error}")
    
    # Test query generation
    print("\nTesting query generation...")
    plan = QueryPlan(
        intent="Get top 5 customers by country",
        tables=["Customer"],
        columns=["FirstName", "LastName", "Country"],
        joins=[],
        filters=["Country = 'Brazil'"],
        grouping=None,
        ordering="LastName ASC",
        limit=5
    )
    
    query = generator.build_query_from_plan(plan)
    print(query)
