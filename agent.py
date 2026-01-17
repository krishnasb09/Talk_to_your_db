"""
Intelligent Reasoning Agent
The core agent that orchestrates schema exploration, query planning, and execution
"""
import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dataclasses import dataclass

from schema_explorer import SchemaExplorer
from sql_generator import SQLGenerator, QueryPlan
from query_executor import QueryExecutor, QueryResult
from result_formatter import ResultFormatter


@dataclass
class ReasoningStep:
    """A single step in the reasoning process"""
    step_number: int
    description: str
    action: str  # 'explore', 'plan', 'generate', 'execute', 'analyze'
    details: Optional[str] = None


class IntelligentAgent:
    """
    Intelligent database reasoning agent.
    Goes beyond naive text-to-SQL by reasoning, exploring, and self-correcting.
    """
    
    # System prompt for the LLM
    SYSTEM_PROMPT = """You are an expert database analyst and SQL engineer.

Your task: Convert natural language questions into SAFE, EFFICIENT, READ-ONLY SQL queries.

CRITICAL RULES:
1. ALWAYS reason step-by-step before generating SQL
2. Explore the schema when needed - don't assume table/column names
3. Only generate SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
4. Avoid SELECT * unless specifically needed
5. Add LIMIT clauses to prevent large result sets
6. Handle ambiguity by stating clear assumptions
7. Break complex questions into sub-problems

When responding, follow this structure:

REASONING:
<step-by-step analysis of the question>
<schema exploration if needed>
<query strategy>

STRATEGY:
<tables needed>
<joins required>
<filters/conditions>
<aggregations/grouping>

SQL:
<final SQL query>

ASSUMPTIONS:
<any assumptions made for ambiguous terms>
"""

    
    def __init__(self, connection, api_key: Optional[str] = None):
        """
        Initialize the agent.
        
        Args:
            connection: SQLite database connection
            api_key: Google Gemini API key (or set GOOGLE_API_KEY env var)
        """
        self.conn = connection
        self.explorer = SchemaExplorer(connection)
        self.generator = SQLGenerator()
        self.executor = QueryExecutor(connection)
        self.formatter = ResultFormatter()
        
        # Initialize Gemini
        self.model = None
        api_key = api_key or os.getenv('GOOGLE_API_KEY')
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini: {e}")
                
        self.max_retries = 3
        
    def _select_best_model(self):
        # Removed to improve startup speed
        pass
        
        # Reasoning trace
        self.reasoning_steps: List[ReasoningStep] = []
        self.max_retries = 3
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a natural language question about the database.
        
        Args:
            question: User's question in natural language
            
        Returns:
            Dictionary containing answer, SQL, reasoning, and metadata
        """
        self.reasoning_steps = []
        
        # Step 1: Analyze the question
        self._add_reasoning_step(
            "analyze",
            "Analyzing user question",
            f"Question: '{question}'"
        )
        
        # Step 2: Determine if this is a meta-query
        is_meta, meta_result = self._handle_meta_query(question)
        if is_meta:
            return meta_result
        
        # Step 3: Get relevant schema information
        schema_context = self._get_schema_context(question)
        
        # Step 4: Generate SQL using LLM with reasoning
        sql, reasoning_text = self._generate_sql_with_reasoning(question, schema_context)
        
        # Step 5: Validate SQL
        is_valid, error = self.generator.validate_query(sql)
        if not is_valid:
            self._add_reasoning_step(
                "validate",
                "SQL validation failed",
                error
            )
            return {
                'success': False,
                'error': error,
                'sql': sql,
                'reasoning': self._format_reasoning_trace(),
                'answer': f"Generated SQL failed safety validation: {error}"
            }
        
        # Step 6: Execute query with retry logic
        result = self._execute_with_retry(sql, question, schema_context)
        
        # Step 7: Synthesize answer using LLM
        answer = self._synthesize_answer(question, sql, result)
        
        return {
            'success': result.success,
            'answer': answer,
            'sql': sql,
            'reasoning': reasoning_text,
            'reasoning_steps': self._format_reasoning_trace(),
            'execution_time': result.execution_time,
            'row_count': result.row_count if result.success else 0
        }

    def _synthesize_answer(self, question: str, sql: str, result: QueryResult) -> str:
        """Use LLM to interpret results and generate a conversational answer"""
        self._add_reasoning_step(
            "synthesize",
            "interpreting results with LLM",
            f"Converting {result.row_count} rows to natural language"
        )
        
        # Format the data for the LLM
        data_preview = self.formatter.format_result(result, question)
        
        prompt = f"""You are a helpful data assistant.
        
USER QUESTION: {question}

SQL EXECUTED: {sql}

DATABASE RESULT:
{data_preview}

Please provide a natural, conversational answer to the user's question based on this data.
- Be concise but friendly.
- If it's a specific count or finding, state it clearly (e.g., "There are 5 customers...")
- If it's a list, summarize it (e.g., "The top artists are A, B, and C").
- Do NO mention "SQL" or "rows" or "query" in your final answer to the user. Just speak naturally.
"""
        try:
            # Use central helper for robust calling
            return self._call_llm(prompt).strip()
        except:
            # Fallback to formatter if LLM fails
            return data_preview
    
    def _handle_meta_query(self, question: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """Check if this is a meta-query and handle it"""
        q_lower = question.lower()
        
        # "What tables exist?"
        if 'what tables' in q_lower or 'show tables' in q_lower or 'list tables' in q_lower:
            self._add_reasoning_step(
                "meta",
                "Detected meta-query: list tables",
                "Using schema explorer to get table list"
            )
            tables = self.explorer.get_all_tables()
            answer = f"✓ Database contains {len(tables)} tables:\n\n"
            answer += "\n".join(f"{i}. {table}" for i, table in enumerate(tables, 1))
            
            return True, {
                'success': True,
                'answer': answer,
                'sql': 'SELECT name FROM sqlite_master WHERE type="table"',
                'reasoning': self._format_reasoning_trace(),
                'is_meta': True
            }
        
        # "Show schema of table X"
        if 'schema' in q_lower or 'describe' in q_lower or 'structure' in q_lower:
            # Extract table name
            for table in self.explorer.get_all_tables():
                if table.lower() in q_lower:
                    self._add_reasoning_step(
                        "meta",
                        f"Detected meta-query: show schema for {table}",
                        "Using PRAGMA to get table structure"
                    )
                    table_info = self.explorer.get_table_info(table)
                    if table_info:
                        answer = f"✓ Schema for table '{table}':\n\n"
                        answer += f"Rows: {table_info.row_count}\n\n"
                        answer += "Columns:\n"
                        for col in table_info.columns:
                            pk = " [PRIMARY KEY]" if col.is_primary_key else ""
                            nn = " NOT NULL" if col.not_null else ""
                            answer += f"  - {col.name}: {col.type}{nn}{pk}\n"
                        
                        if table_info.foreign_keys:
                            answer += "\nForeign Keys:\n"
                            for fk in table_info.foreign_keys:
                                answer += f"  - {fk.from_column} → {fk.to_table}.{fk.to_column}\n"
                        
                        return True, {
                            'success': True,
                            'answer': answer,
                            'sql': f'PRAGMA table_info({table})',
                            'reasoning': self._format_reasoning_trace(),
                            'is_meta': True
                        }
        
        return False, None
    
    def _get_schema_context(self, question: str) -> str:
        """Get relevant schema information based on the question"""
        self._add_reasoning_step(
            "explore",
            "Checking schema...",
            f"Found relevant tables in schema context"
        )
        
        # For now, return full compact schema
        # In a more advanced version, we could filter based on keywords in the question
        return self.explorer.get_compact_schema()
    
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with automatic fallback logic using multiple model candidates"""
        if not self.model:
            # Re-initialize if missing
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
        print(f"DEBUG: calling LLM with model {self.model._model_name}...")
        
        # Candidate models to try in order
        candidates = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
        ]
        
        # First try the current model
        try:
            response = self.model.generate_content(prompt)
            print("DEBUG: LLM response received.")
            return response.text
        except Exception as e:
            # Check if this is a 404/not found error
            is_404 = "404" in str(e) and "not found" in str(e).lower()
            
            if not is_404:
                # If it's a different error (e.g. rate limit, quota), raising it might be better,
                # but for hackathon robustness we'll try fallbacks anyway.
                print(f"DEBUG: Initial error {e}")
            
            print("DEBUG: Triggering fallback chain...")
            
            last_error = e
            
            # Try each candidate
            for model_name in candidates:
                # Skip if it's the one we just failed on (unless we want to retry same model? No.)
                if model_name == self.model._model_name:
                    continue
                    
                print(f"DEBUG: Trying fallback model: {model_name}")
                try:
                    # Switch model
                    self.model = genai.GenerativeModel(model_name)
                    response = self.model.generate_content(prompt)
                    
                    self._add_reasoning_step(
                        "warning",
                        "Model Fallback",
                        f"Switched to {model_name} after previous failure"
                    )
                    return response.text
                except Exception as fallback_error:
                    print(f"DEBUG: Failed with {model_name}: {fallback_error}")
                    last_error = fallback_error
            
            # If we get here, all failed
            self._add_reasoning_step("error", "All models failed", str(last_error))
            raise last_error

    def _generate_sql_with_reasoning(self, question: str, schema_context: str) -> tuple[str, str]:
        """Generate SQL query using LLM with reasoning"""
        self._add_reasoning_step(
            "generate",
            "Generating query...",
            "Formulating SQL based on schema and intent"
        )
        
        prompt = f"""{self.SYSTEM_PROMPT}

DATABASE SCHEMA:
{schema_context}

USER QUESTION:
{question}

Please provide your step-by-step reasoning and generate a safe, efficient SQL query.
Remember: READ-ONLY queries only, use LIMIT, avoid SELECT *.
"""
        
        try:
            # Use central helper for robust calling
            response_text = self._call_llm(prompt)
            
            # Extract SQL from response
            sql = self._extract_sql(response_text)
            
            # Extract and add detailed reasoning steps from LLM
            self._parse_llm_reasoning(response_text)
            
            return sql, response_text
            
        except Exception as e:
            self._add_reasoning_step(
                "error",
                "LLM generation failed",
                str(e)
            )
            raise

    def _parse_llm_reasoning(self, response_text: str):
        """Parse the REASONING and STRATEGY sections from LLM response"""
        import re
        
        # 1. Parse REASONING
        match = re.search(r'REASONING:(.*?)(?:STRATEGY:|SQL:)', response_text, re.DOTALL | re.IGNORECASE)
        if match:
            reasoning_text = match.group(1).strip()
            lines = [line.strip() for line in reasoning_text.split('\n') if line.strip()]
            for line in lines:
                clean_line = re.sub(r'^[\d\.\-\*]+\s+', '', line)
                if clean_line:
                    self._add_reasoning_step("plan", clean_line)
                    
        # 2. Parse STRATEGY
        match = re.search(r'STRATEGY:(.*?)(?:SQL:)', response_text, re.DOTALL | re.IGNORECASE)
        if match:
            strategy_text = match.group(1).strip()
            lines = [line.strip() for line in strategy_text.split('\n') if line.strip()]
            for line in lines:
                clean_line = re.sub(r'^[\d\.\-\*]+\s+', '', line)
                if clean_line:
                    self._add_reasoning_step("plan", f"Strategy: {clean_line}")

    def _process_response(self, response) -> tuple[str, str]:
        """Process LLM response to extract SQL"""
        # Deprecated - functionality moved to _call_llm and _generate_sql_with_reasoning
        pass
    
    def _extract_sql(self, llm_response: str) -> str:
        """Extract SQL query from LLM response"""
        # Look for SQL code block
        import re
        
        # Try to find ```sql code block
        sql_match = re.search(r'```sql\s+(.*?)\s+```', llm_response, re.DOTALL | re.IGNORECASE)
        if sql_match:
            return sql_match.group(1).strip()
        
        # Try to find SQL: section
        sql_match = re.search(r'SQL:\s+(.*?)(?:\n\n|ASSUMPTIONS:|RESULT:|$)', llm_response, re.DOTALL | re.IGNORECASE)
        if sql_match:
            return sql_match.group(1).strip()
        
        # Look for SELECT statement
        sql_match = re.search(r'(SELECT.*?;)', llm_response, re.DOTALL | re.IGNORECASE)
        if sql_match:
            return sql_match.group(1).strip()
        
        raise ValueError("Could not extract SQL from LLM response")
    
    def _execute_with_retry(self, sql: str, question: str, schema_context: str) -> QueryResult:
        """Execute query with retry logic for error recovery"""
        for attempt in range(self.max_retries):
            self._add_reasoning_step(
                "execute",
                f"Executing query (attempt {attempt + 1}/{self.max_retries})",
                sql
            )
            
            result = self.executor.execute_query(sql)
            
            if result.success:
                self._add_reasoning_step(
                    "success",
                    f"Query executed successfully ({result.row_count} rows)",
                    f"Execution time: {result.execution_time:.3f}s"
                )
                return result
            
            # Query failed - attempt recovery
            if attempt < self.max_retries - 1:
                self._add_reasoning_step(
                    "error",
                    f"Query failed: {result.error}",
                    "Attempting to generate corrected query"
                )
                
                sql = self._recover_from_error(sql, result.error, question, schema_context)
            else:
                self._add_reasoning_step(
                    "error",
                    "Max retries reached",
                    result.error
                )
        
        return result
    
    def _recover_from_error(self, failed_sql: str, error: str, question: str, schema_context: str) -> str:
        """Attempt to recover from a query error"""
        recovery_prompt = f"""{self.SYSTEM_PROMPT}

DATABASE SCHEMA:
{schema_context}

USER QUESTION:
{question}

PREVIOUS ATTEMPT (FAILED):
{failed_sql}

ERROR:
{error}

The previous query failed. Please analyze the error and generate a corrected query.
Focus on fixing the specific error while maintaining the query intent.
"""
        
        try:
            response_text = self._call_llm(recovery_prompt)
            corrected_sql = self._extract_sql(response_text)
            
            self._add_reasoning_step(
                "recover",
                "Generated corrected query",
                corrected_sql
            )
            
            return corrected_sql
        except:
            # If recovery fails, return original
            return failed_sql
    
    def _add_reasoning_step(self, action: str, description: str, details: Optional[str] = None):
        """Add a step to the reasoning trace"""
        step = ReasoningStep(
            step_number=len(self.reasoning_steps) + 1,
            description=description,
            action=action,
            details=details
        )
        self.reasoning_steps.append(step)
    
    def _format_reasoning_trace(self) -> str:
        """Format the reasoning trace for display"""
        return self.formatter.format_reasoning_trace(self.reasoning_steps)


if __name__ == "__main__":
    # Test agent
    from setup_database import get_database_connection
    
    conn = get_database_connection()
    
    # Set your API key
    # os.environ['GOOGLE_API_KEY'] = 'your-api-key-here'
    
    try:
        agent = IntelligentAgent(conn)
        
        # Test simple question
        result = agent.answer_question("What tables exist in this database?")
        print(result['answer'])
        print("\n" + "=" * 60 + "\n")
        print(result['reasoning_steps'])
        
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set GOOGLE_API_KEY environment variable.")
    
    conn.close()
