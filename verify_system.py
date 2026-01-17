"""
Simple verification test
Tests basic functionality without requiring API key interaction
"""
from setup_database import get_database_connection, download_chinook_database, verify_database
from schema_explorer import SchemaExplorer
from sql_generator import SQLGenerator, QueryPlan
from query_executor import QueryExecutor
from result_formatter import ResultFormatter

print("=" * 70)
print("VERIFICATION TEST - Basic System Functionality")
print("=" * 70)

# Test 1: Database Setup
print("\n[Test 1] Database Setup...")
try:
    download_chinook_database("chinook.db")
    print("✓ Database download/verification passed")
except Exception as e:
    print(f"✗ Database setup failed: {e}")
    exit(1)

# Test 2: Schema Explorer
print("\n[Test 2] Schema Explorer...")
try:
    conn = get_database_connection("chinook.db")
    explorer = SchemaExplorer(conn)
    tables = explorer.get_all_tables()
    assert len(tables) > 0, "No tables found"
    print(f"✓ Found {len(tables)} tables: {', '.join(tables[:5])}...")
    
    # Test table info
    customer_info = explorer.get_table_info("Customer")
    assert customer_info is not None, "Could not get Customer table info"
    print(f"✓ Customer table has {len(customer_info.columns)} columns")
except Exception as e:
    print(f"✗ Schema explorer failed: {e}")
    exit(1)

# Test 3: SQL Generator
print("\n[Test 3] SQL Generator...")
try:
    generator = SQLGenerator()
    
    # Test validation
    valid, error = generator.validate_query("SELECT * FROM Customer LIMIT 10;")
    assert valid, f"Valid query rejected: {error}"
    print("✓ Valid query accepted")
    
    # Test forbidden operation
    valid, error = generator.validate_query("DELETE FROM Customer;")
    assert not valid, "Forbidden query accepted!"
    print("✓ Forbidden query blocked")
    
    # Test query building
    plan = QueryPlan(
        intent="Test query",
        tables=["Customer"],
        columns=["FirstName", "LastName"],
        joins=[],
        filters=["Country = 'Brazil'"],
        grouping=None,
        ordering="LastName",
        limit=5
    )
    sql = generator.build_query_from_plan(plan)
    print(f"✓ Generated query: {sql[:50]}...")
except Exception as e:
    print(f"✗ SQL generator failed: {e}")
    exit(1)

# Test 4: Query Executor
print("\n[Test 4] Query Executor...")
try:
    executor = QueryExecutor(conn)
    
    # Simple test query
    result = executor.execute_query("SELECT COUNT(*) as total FROM Artist;")
    assert result.success, f"Query failed: {result.error}"
    assert result.row_count == 1, "Expected 1 row"
    print(f"✓ Found {result.rows[0][0]} artists in database")
    
    # Test error handling
    result = executor.execute_query("SELECT * FROM NonExistentTable;")
    assert not result.success, "Invalid query succeeded!"
    print("✓ Error handling works")
except Exception as e:
    print(f"✗ Query executor failed: {e}")
    exit(1)

# Test 5: Result Formatter
print("\n[Test 5] Result Formatter...")
try:
    formatter = ResultFormatter()
    
    # Test single value
    result = executor.execute_query("SELECT COUNT(*) as total FROM Customer;")
    formatted = formatter.format_result(result)
    assert "✓" in formatted, "Result formatting failed"
    print("✓ Single value formatting works")
    
    # Test table
    result = executor.execute_query("SELECT Name FROM Genre LIMIT 3;")
    formatted = formatter.format_result(result)
    assert "found" in formatted.lower(), "List formatting failed"
    print("✓ List formatting works")
except Exception as e:
    print(f"✗ Result formatter failed: {e}")
    exit(1)

# Test 6: Meta-queries
print("\n[Test 6] Meta-query Support...")
try:
    meta_sql = generator.generate_meta_query('tables')
    result = executor.execute_query(meta_sql)
    assert result.success, "Meta-query failed"
    print(f"✓ Meta-query found {result.row_count} tables")
except Exception as e:
    print(f"✗ Meta-query failed: {e}")
    exit(1)

# Cleanup
conn.close()

print("\n" + "=" * 70)
print("ALL TESTS PASSED ✓")
print("=" * 70)
print("\nCore system components are working correctly!")
print("To test the full intelligent agent, run: python cli.py")
print("(Requires GOOGLE_API_KEY environment variable)")
