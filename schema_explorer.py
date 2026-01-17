"""
Schema Explorer Module
Explores and caches database schema information
"""
import sqlite3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ColumnInfo:
    """Information about a database column"""
    name: str
    type: str
    not_null: bool
    default_value: Optional[str]
    is_primary_key: bool


@dataclass
class ForeignKey:
    """Information about a foreign key relationship"""
    from_table: str
    from_column: str
    to_table: str
    to_column: str


@dataclass
class TableInfo:
    """Complete information about a database table"""
    name: str
    columns: List[ColumnInfo]
    foreign_keys: List[ForeignKey]
    row_count: int


class SchemaExplorer:
    """
    Explores and manages database schema information.
    Uses sqlite_master and PRAGMA commands to introspect the database.
    """
    
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.schema_cache: Dict[str, TableInfo] = {}
        self._load_schema()
    
    def _load_schema(self):
        """Load complete schema information into cache"""
        tables = self.get_all_tables()
        for table in tables:
            self.schema_cache[table] = self._get_table_info(table)
    
    def get_all_tables(self) -> List[str]:
        """
        Get all table names in the database.
        
        Returns:
            List of table names
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
        """)
        return [row[0] for row in cursor.fetchall()]
    
    def _get_table_info(self, table_name: str) -> TableInfo:
        """
        Get complete information about a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            TableInfo object with all table details
        """
        cursor = self.conn.cursor()
        
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = []
        for row in cursor.fetchall():
            col = ColumnInfo(
                name=row[1],
                type=row[2],
                not_null=bool(row[3]),
                default_value=row[4],
                is_primary_key=bool(row[5])
            )
            columns.append(col)
        
        # Get foreign key information
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        foreign_keys = []
        for row in cursor.fetchall():
            fk = ForeignKey(
                from_table=table_name,
                from_column=row[3],
                to_table=row[2],
                to_column=row[4]
            )
            foreign_keys.append(fk)
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        
        return TableInfo(
            name=table_name,
            columns=columns,
            foreign_keys=foreign_keys,
            row_count=row_count
        )
    
    def get_table_info(self, table_name: str) -> Optional[TableInfo]:
        """
        Get cached table information.
        
        Args:
            table_name: Name of the table
            
        Returns:
            TableInfo object or None if table doesn't exist
        """
        return self.schema_cache.get(table_name)
    
    def find_tables_by_keyword(self, keyword: str) -> List[str]:
        """
        Find tables whose names contain a keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching table names
        """
        keyword = keyword.lower()
        return [
            table for table in self.schema_cache.keys()
            if keyword in table.lower()
        ]
    
    def find_columns_by_name(self, column_name: str) -> List[Tuple[str, ColumnInfo]]:
        """
        Find columns across all tables by name.
        
        Args:
            column_name: Column name to search for
            
        Returns:
            List of (table_name, ColumnInfo) tuples
        """
        results = []
        column_name = column_name.lower()
        
        for table_name, table_info in self.schema_cache.items():
            for col in table_info.columns:
                if column_name in col.name.lower():
                    results.append((table_name, col))
        
        return results
    
    def get_relationships(self, table_name: str) -> Dict[str, List[ForeignKey]]:
        """
        Get all foreign key relationships for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with 'outgoing' and 'incoming' foreign keys
        """
        outgoing = []
        incoming = []
        
        # Outgoing foreign keys (this table references others)
        table_info = self.get_table_info(table_name)
        if table_info:
            outgoing = table_info.foreign_keys
        
        # Incoming foreign keys (other tables reference this table)
        for other_table, other_info in self.schema_cache.items():
            if other_table != table_name:
                for fk in other_info.foreign_keys:
                    if fk.to_table == table_name:
                        incoming.append(fk)
        
        return {
            'outgoing': outgoing,
            'incoming': incoming
        }
    
    def get_schema_summary(self) -> str:
        """
        Get a human-readable summary of the database schema.
        
        Returns:
            Formatted schema summary
        """
        lines = ["DATABASE SCHEMA SUMMARY", "=" * 60, ""]
        
        for table_name, table_info in sorted(self.schema_cache.items()):
            lines.append(f"Table: {table_name} ({table_info.row_count} rows)")
            lines.append("-" * 60)
            
            # Primary keys
            pk_cols = [col.name for col in table_info.columns if col.is_primary_key]
            if pk_cols:
                lines.append(f"  Primary Key: {', '.join(pk_cols)}")
            
            # Columns
            lines.append("  Columns:")
            for col in table_info.columns:
                nullable = "" if col.not_null else " (nullable)"
                pk = " [PK]" if col.is_primary_key else ""
                lines.append(f"    - {col.name}: {col.type}{nullable}{pk}")
            
            # Foreign keys
            if table_info.foreign_keys:
                lines.append("  Foreign Keys:")
                for fk in table_info.foreign_keys:
                    lines.append(f"    - {fk.from_column} -> {fk.to_table}.{fk.to_column}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def get_compact_schema(self) -> str:
        """
        Get a compact, LLM-friendly schema representation.
        
        Returns:
            Compact schema string for LLM context
        """
        lines = []
        
        for table_name, table_info in sorted(self.schema_cache.items()):
            # Table header
            lines.append(f"{table_name} ({table_info.row_count} rows):")
            
            # Columns with types and constraints
            col_strs = []
            for col in table_info.columns:
                parts = [col.name, col.type]
                if col.is_primary_key:
                    parts.append("PK")
                if col.not_null and not col.is_primary_key:
                    parts.append("NOT NULL")
                col_strs.append(" ".join(parts))
            
            lines.append("  " + ", ".join(col_strs))
            
            # Foreign keys
            if table_info.foreign_keys:
                for fk in table_info.foreign_keys:
                    lines.append(f"  {fk.from_column} -> {fk.to_table}.{fk.to_column}")
            
            lines.append("")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Test schema explorer
    from setup_database import get_database_connection
    
    conn = get_database_connection()
    explorer = SchemaExplorer(conn)
    
    print(explorer.get_schema_summary())
    
    conn.close()
