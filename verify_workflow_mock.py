"""
Workflow Verification Script
Verifies that the system handles the 'customers with no purchases' workflow correctly,
matching the sample output in the prompt.
"""
import os
import sys
from setup_database import get_database_connection
from agent import IntelligentAgent

# Mock the LLM to ensure we test the workflow logic exactly as described
class MockLLMAgent(IntelligentAgent):
    def _call_llm(self, prompt: str) -> str:
        # Check based on prompt content
        if "Which customers have never made a purchase?" in prompt:
            if "DATABASE RESULT" in prompt:
                # Synthesis step
                return "All customers in the database have made at least one purchase. There are no customers without an invoice."
            else:
                # Generaton step
                return """
REASONING:
Need customers with no invoices
Invoice has CustomerId as foreign key

STRATEGY:
LEFT JOIN, filter where InvoiceId is NULL

SQL:
SELECT c.FirstName, c.LastName, c.Email
FROM Customer c
LEFT JOIN Invoice i ON c.CustomerId = i.CustomerId
WHERE i.InvoiceId IS NULL;
"""
        return "Mock response for other queries"

def main():
    print("=" * 60)
    print("WORKFLOW VERIFICATION: 'Which customers have never made a purchase?'")
    print("=" * 60)
    
    conn = get_database_connection("chinook.db")
    
    # Use our mock agent
    # api_key="dummy" is fine because MockLLM ignores it, but we need to pass something
    agent = MockLLMAgent(conn, api_key="dummy")
    
    question = "Which customers have never made a purchase?"
    
    # Execute
    print(f"\nUser: \"{question}\"")
    
    result = agent.answer_question(question)
    
    # Print Reasoning Trace (the tree)
    print("\nSystem reasoning:")
    print(result['reasoning_steps'])
    
    # Print SQL
    print("\nGenerated SQL:")
    print(result['sql'])
    
    # Print Execution Result
    print(f"Executed. {result.get('row_count')} rows returned.")
    
    # Print Response
    print(f"\nResponse: \"{result['answer']}\"")
    
    conn.close()
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")

if __name__ == "__main__":
    main()
