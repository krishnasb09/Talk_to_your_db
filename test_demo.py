"""
Test Demonstration Script
Demonstrates the capabilities of the intelligent NL2SQL system
Shows where naive approaches fail and how our system succeeds
"""
import os
from colorama import init, Fore, Style
from setup_database import get_database_connection
from agent import IntelligentAgent

# Initialize colorama
init()


class TestDemo:
    """Demonstration and testing of the intelligent NL2SQL system"""
    
    def __init__(self, api_key: str):
        """Initialize the demo with database and agent"""
        print(Fore.CYAN + "\n" + "=" * 70)
        print("  Intelligent NL2SQL System - Test Demonstration")
        print("=" * 70 + Style.RESET_ALL)
        
        # Setup
        print("\n" + Fore.YELLOW + "Setting up..." + Style.RESET_ALL)
        self.conn = get_database_connection("chinook.db")
        self.agent = IntelligentAgent(self.conn, api_key)
        print(Fore.GREEN + "✓ Ready!" + Style.RESET_ALL)
    
    def run_test(self, question: str, category: str, naive_failure: str = None):
        """
        Run a single test question.
        
        Args:
            question: The question to ask
            category: Category of the question (Simple, Moderate, etc.)
            naive_failure: Why a naive approach would fail (optional)
        """
        print("\n" + "=" * 70)
        print(Fore.CYAN + f"Category: {category}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"Question: {question}" + Style.RESET_ALL)
        
        if naive_failure:
            print(Fore.RED + f"\n❌ Naive Approach Fails: {naive_failure}" + Style.RESET_ALL)
        
        print(Fore.GREEN + "\n✓ Our System:" + Style.RESET_ALL)
        
        try:
            result = self.agent.answer_question(question)
            
            # Show Reasoning Trace
            if 'reasoning_steps' in result:
                print(Fore.MAGENTA + "\nReasoning:" + Style.RESET_ALL)
                print(result['reasoning_steps'])
            
            # Show SQL
            if 'sql' in result:
                print(Fore.MAGENTA + "\nGenerated SQL:" + Style.RESET_ALL)
                print(result['sql'])
            
            # Show answer
            print(Fore.GREEN + "\nAnswer:" + Style.RESET_ALL)
            print(result['answer'])
            
            # Show metadata
            if result.get('success') and not result.get('is_meta'):
                print(Fore.CYAN + f"\n⏱ Execution: {result.get('execution_time', 0):.3f}s | Rows: {result.get('row_count', 0)}" + Style.RESET_ALL)
            
            return True
            
        except Exception as e:
            print(Fore.RED + f"\n✗ Error: {str(e)}" + Style.RESET_ALL)
            return False
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        
        tests = [
            # SIMPLE
            {
                'question': 'How many customers are from Brazil?',
                'category': 'SIMPLE',
                'naive_failure': None
            },
            {
                'question': 'List all albums by AC/DC',
                'category': 'SIMPLE',
                'naive_failure': None
            },
            
            # MODERATE
            {
                'question': 'Which 5 artists have the most tracks?',
                'category': 'MODERATE',
                'naive_failure': 'May not add LIMIT, could return too many results'
            },
            {
                'question': 'Total revenue by country, sorted highest first',
                'category': 'MODERATE',
                'naive_failure': 'May struggle with JOIN across Invoice and InvoiceLine tables'
            },
            
            # REQUIRES REASONING
            {
                'question': 'Customers who purchased tracks from both Rock and Jazz genres',
                'category': 'COMPLEX - Multi-step Reasoning',
                'naive_failure': 'Single-shot approach fails - needs to find Rock buyers, Jazz buyers, then intersect'
            },
            {
                'question': 'Which artist has tracks in the most playlists?',
                'category': 'COMPLEX - Multi-step Reasoning',
                'naive_failure': 'May hallucinate table names or miss the complex JOIN chain'
            },
            
            # AMBIGUOUS
            {
                'question': 'Show me recent orders',
                'category': 'AMBIGUOUS',
                'naive_failure': 'Makes arbitrary assumptions about "recent" without stating them'
            },
            {
                'question': 'Who are our best customers?',
                'category': 'AMBIGUOUS',
                'naive_failure': 'Undefined metric for "best" - total spend? frequency? recency?'
            },
            
            # MULTI-STEP / EXPLORATION
            {
                'question': 'Are there any genres with no sales?',
                'category': 'MULTI-STEP',
                'naive_failure': 'Needs LEFT JOIN and NULL check - easy to get wrong'
            },
            {
                'question': 'Which customers have never made a purchase?',
                'category': 'MULTI-STEP',
                'naive_failure': 'Needs LEFT JOIN on Invoice, filter for NULL - often generates incorrect query'
            },
            
            # META-QUERIES
            {
                'question': 'What tables exist in this database?',
                'category': 'META-QUERY',
                'naive_failure': 'Naive approach tries to generate SQL instead of using sqlite_master'
            },
            {
                'question': 'Show me the schema of the Invoice table',
                'category': 'META-QUERY',
                'naive_failure': 'Needs PRAGMA command, not a regular SELECT'
            },
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            success = self.run_test(
                test['question'],
                test['category'],
                test.get('naive_failure')
            )
            if success:
                passed += 1
            
            # Pause between tests
            input(Fore.CYAN + "\nPress Enter to continue..." + Style.RESET_ALL)
        
        # Summary
        print("\n" + "=" * 70)
        print(Fore.CYAN + "TEST SUMMARY" + Style.RESET_ALL)
        print("=" * 70)
        print(f"Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    def cleanup(self):
        """Clean up resources"""
        if self.conn:
            self.conn.close()


def main():
    """Main entry point"""
    print(Fore.YELLOW + "\nThis demo will test the system with various query types.")
    print("Each test will show:")
    print("  1. Why a naive approach would fail")
    print("  2. How our intelligent system handles it")
    print("  3. The generated SQL and results" + Style.RESET_ALL)
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("\n" + Fore.YELLOW + "GOOGLE_API_KEY not found in environment." + Style.RESET_ALL)
        api_key = input(Fore.CYAN + "Enter your Google Gemini API key: " + Style.RESET_ALL).strip()
    
    if not api_key:
        print(Fore.RED + "✗ API key required!" + Style.RESET_ALL)
        return
    
    # Run tests
    demo = TestDemo(api_key)
    try:
        demo.run_all_tests()
    finally:
        demo.cleanup()


if __name__ == "__main__":
    main()
