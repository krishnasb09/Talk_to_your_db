"""
Result Formatter Module
Converts SQL query results into human-readable text
"""
from typing import List, Tuple, Any
from query_executor import QueryResult


class ResultFormatter:
    """
    Formats query results into human-readable output.
    """
    
    def format_result(self, result: QueryResult, question: str = "") -> str:
        """
        Format a query result into human-readable text.
        
        Args:
            result: QueryResult object
            question: Original question asked by user (for context)
            
        Returns:
            Formatted string
        """
        if not result.success:
            return self._format_error(result)
        
        if result.row_count == 0:
            return self._format_empty_result(question)
        
        # Determine best formatting based on result shape
        if result.row_count == 1 and len(result.columns) == 1:
            # Single value result
            return self._format_single_value(result, question)
        elif len(result.columns) == 1:
            # Single column list
            return self._format_list(result)
        elif result.row_count <= 20:
            # Small result set - show as table
            return self._format_table(result)
        else:
            # Large result set - show summary + sample
            return self._format_summary(result)
    
    def _format_error(self, result: QueryResult) -> str:
        """Format an error result"""
        return f"❌ Query failed: {result.error}"
    
    def _format_empty_result(self, question: str) -> str:
        """Format an empty result set"""
        return "✓ Query executed successfully, but returned no results.\n\nThis could mean:\n- No data matches the criteria\n- The condition excludes all rows"
    
    def _format_single_value(self, result: QueryResult, question: str) -> str:
        """Format a single value result (e.g., COUNT queries)"""
        value = result.rows[0][0]
        column = result.columns[0]
        
        # Simple extraction of subject from "How many [subject] ..."
        subject = "result(s)"
        q_lower = question.lower()
        
        if "how many" in q_lower:
            try:
                # Extract words between "how many" and "are/have/do/in/from"
                import re
                match = re.search(r'how many\s+(.*?)\s+(?:are|have|do|does|did|in|from|there)', q_lower)
                if match:
                    subject = match.group(1)
                else:
                    # Fallback: take next word
                    match = re.search(r'how many\s+(\w+)', q_lower)
                    if match:
                        subject = match.group(1)
            except:
                pass
        
        # Format based on column type
        if 'count' in column.lower():
            return f"✓ There are **{value} {subject}**."
        elif 'sum' in column.lower() or 'total' in column.lower():
             return f"✓ The total is **{value}**."
        elif 'avg' in column.lower() or 'average' in column.lower():
             return f"✓ The average is **{value}**."
        else:
            return f"✓ The answer is **{value}**."
    
    def _format_list(self, result: QueryResult) -> str:
        """Format a single-column result as a list"""
        column = result.columns[0]
        values = [row[0] for row in result.rows]
        
        lines = [f"✓ Here are the **{len(values)} {column}s** found:", ""]
        
        for i, value in enumerate(values, 1):
            lines.append(f"{i}. {value}")
        
        return "\n".join(lines)
    
    def _format_table(self, result: QueryResult) -> str:
        """Format result as a text table"""
        lines = [f"✓ Found **{result.row_count} results**:", ""]
        
        # Calculate column widths
        col_widths = []
        for i, col in enumerate(result.columns):
            max_width = len(col)
            for row in result.rows:
                max_width = max(max_width, len(str(row[i])))
            col_widths.append(min(max_width, 50))  # Cap at 50 chars
        
        # Header row
        header = " | ".join(
            col.ljust(width) 
            for col, width in zip(result.columns, col_widths)
        )
        lines.append(header)
        lines.append("-" * len(header))
        
        # Data rows
        for row in result.rows:
            row_str = " | ".join(
                str(val).ljust(width)[:width]  # Truncate if too long
                for val, width in zip(row, col_widths)
            )
            lines.append(row_str)
        
        return "\n".join(lines)
    
    def _format_summary(self, result: QueryResult) -> str:
        """Format large result set with summary + sample"""
        lines = [
            f"✓ Found {result.row_count} result(s).",
            "",
            "Showing first 10 rows:",
            ""
        ]
        
        # Create smaller result for table formatting
        sample_result = QueryResult(
            success=True,
            columns=result.columns,
            rows=result.rows[:10],
            row_count=10,
            execution_time=result.execution_time
        )
        
        table = self._format_table(sample_result)
        lines.append(table)
        lines.append("")
        lines.append(f"... and {result.row_count - 10} more rows.")
        
        return "\n".join(lines)
    
    def format_reasoning_trace(self, steps: List[Any]) -> str:
        """
        Format a reasoning trace with tree-style visualization.
        
        Args:
            steps: List of ReasoningStep objects
            
        Returns:
            Formatted reasoning trace
        """
        if not steps:
            return ""
            
        lines = []
        total_steps = len(steps)
        
        for i, step in enumerate(steps):
            is_last = (i == total_steps - 1)
            prefix = "└── " if is_last else "├── "
            
            lines.append(f"{prefix}{step.description}")
            
            if step.details:
                # Indent details
                detail_prefix = "    " if is_last else "│   "
                for detail_line in step.details.split('\n'):
                    lines.append(f"{detail_prefix}{detail_line}")
                    
        return "\n".join(lines)


if __name__ == "__main__":
    # Test formatter
    from setup_database import get_database_connection
    from query_executor import QueryExecutor
    
    conn = get_database_connection()
    executor = QueryExecutor(conn)
    formatter = ResultFormatter()
    
    # Test different result types
    
    # Single value
    result = executor.execute_query("SELECT COUNT(*) as total FROM Artist;")
    print(formatter.format_result(result, "How many artists?"))
    print("\n" + "=" * 60 + "\n")
    
    # List
    result = executor.execute_query("SELECT Name FROM Genre LIMIT 10;")
    print(formatter.format_result(result))
    print("\n" + "=" * 60 + "\n")
    
    # Table
    result = executor.execute_query("SELECT FirstName, LastName, Country FROM Customer LIMIT 5;")
    print(formatter.format_result(result))
    
    conn.close()
