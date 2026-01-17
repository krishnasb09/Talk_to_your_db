"""
CLI Interface for Talk-to-Your-Data
Interactive command-line interface for querying the database
"""
import os
import sys
from colorama import init, Fore, Style
from setup_database import download_chinook_database, get_database_connection, verify_database
from agent import IntelligentAgent


# Initialize colorama for Windows support
init()


class CLI:
    """Command-line interface for the intelligent NL2SQL system"""
    
    def __init__(self):
        self.agent = None
        self.conn = None
        self.show_reasoning = True
        self.show_sql = True
    
    def setup(self):
        """Set up database and agent"""
        print(Fore.CYAN + "\n" + "=" * 70)
        print("  Talk-to-Your-Data: Intelligent NL2SQL System")
        print("=" * 70 + Style.RESET_ALL)
        
        # Download and verify database
        print("\n" + Fore.YELLOW + "Setting up database..." + Style.RESET_ALL)
        db_path = "chinook.db"
        download_chinook_database(db_path)
        
        if not verify_database(db_path):
            print(Fore.RED + "✗ Database verification failed!" + Style.RESET_ALL)
            sys.exit(1)
        
        # Get API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("\n" + Fore.YELLOW + "GOOGLE_API_KEY not found in environment." + Style.RESET_ALL)
            api_key = input(Fore.CYAN + "Enter your Google Gemini API key: " + Style.RESET_ALL).strip()
            if not api_key:
                print(Fore.RED + "✗ API key required!" + Style.RESET_ALL)
                sys.exit(1)
        
        # Initialize agent
        print("\n" + Fore.YELLOW + "Initializing intelligent agent..." + Style.RESET_ALL)
        self.conn = get_database_connection(db_path)
        self.agent = IntelligentAgent(self.conn, api_key)
        
        print(Fore.GREEN + "✓ System ready!" + Style.RESET_ALL)
    
    def print_help(self):
        """Print help information"""
        print(Fore.CYAN + "\nAvailable Commands:" + Style.RESET_ALL)
        print("  " + Fore.YELLOW + "/help" + Style.RESET_ALL + "      - Show this help message")
        print("  " + Fore.YELLOW + "/reasoning" + Style.RESET_ALL + " - Toggle reasoning trace display")
        print("  " + Fore.YELLOW + "/sql" + Style.RESET_ALL + "       - Toggle SQL query display")
        print("  " + Fore.YELLOW + "/schema" + Style.RESET_ALL + "    - Show database schema")
        print("  " + Fore.YELLOW + "/examples" + Style.RESET_ALL + "  - Show example questions")
        print("  " + Fore.YELLOW + "/exit" + Style.RESET_ALL + "      - Exit the program")
        print("\nOr just type your question in natural language!")
    
    def print_examples(self):
        """Print example questions"""
        examples = {
            "Simple": [
                "How many customers are from Brazil?",
                "List all albums by AC/DC"
            ],
            "Moderate": [
                "Which 5 artists have the most tracks?",
                "Total revenue by country, sorted highest first"
            ],
            "Complex": [
                "Customers who purchased tracks from both Rock and Jazz genres",
                "Which artist has tracks in the most playlists?"
            ],
            "Ambiguous": [
                "Show me recent orders",
                "Who are our best customers?"
            ],
            "Multi-step": [
                "Are there any genres with no sales?",
                "Which customers have never made a purchase?"
            ],
            "Meta": [
                "What tables exist?",
                "Show me the schema of the Invoice table"
            ]
        }
        
        print(Fore.CYAN + "\nExample Questions:" + Style.RESET_ALL)
        for category, questions in examples.items():
            print(f"\n{Fore.YELLOW}{category}:{Style.RESET_ALL}")
            for q in questions:
                print(f"  • {q}")
    
    def show_schema(self):
        """Display database schema"""
        print(Fore.CYAN + "\nDatabase Schema:" + Style.RESET_ALL)
        print(self.agent.explorer.get_schema_summary())
    
    def process_question(self, question: str):
        """Process a user question"""
        print("\n" + Fore.CYAN + "Processing your question..." + Style.RESET_ALL)
        
        try:
            result = self.agent.answer_question(question)
            
            # Show SQL if enabled
            if self.show_sql and 'sql' in result:
                print("\n" + Fore.YELLOW + "Generated SQL:" + Style.RESET_ALL)
                print(Fore.WHITE + result['sql'] + Style.RESET_ALL)
            
            # Show reasoning if enabled
            if self.show_reasoning and 'reasoning' in result:
                print("\n" + Fore.MAGENTA + result.get('reasoning_steps', result['reasoning']) + Style.RESET_ALL)
            
            # Show answer
            print("\n" + Fore.GREEN + "Answer:" + Style.RESET_ALL)
            print(result['answer'])
            
            # Show metadata
            if result.get('success') and not result.get('is_meta'):
                print(Fore.CYAN + f"\n⏱ Execution time: {result.get('execution_time', 0):.3f}s | Rows: {result.get('row_count', 0)}" + Style.RESET_ALL)
            
        except Exception as e:
            print(Fore.RED + f"\n✗ Error: {str(e)}" + Style.RESET_ALL)
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Main interactive loop"""
        self.setup()
        self.print_help()
        
        print("\n" + Fore.CYAN + "Ready for questions! Type /help for commands or /exit to quit." + Style.RESET_ALL)
        
        while True:
            try:
                # Get user input
                user_input = input(Fore.GREEN + "\n❯ " + Style.RESET_ALL).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() == '/exit':
                    print(Fore.YELLOW + "\nGoodbye! 👋" + Style.RESET_ALL)
                    break
                
                elif user_input.lower() == '/help':
                    self.print_help()
                
                elif user_input.lower() == '/examples':
                    self.print_examples()
                
                elif user_input.lower() == '/schema':
                    self.show_schema()
                
                elif user_input.lower() == '/reasoning':
                    self.show_reasoning = not self.show_reasoning
                    status = "enabled" if self.show_reasoning else "disabled"
                    print(Fore.YELLOW + f"Reasoning trace {status}" + Style.RESET_ALL)
                
                elif user_input.lower() == '/sql':
                    self.show_sql = not self.show_sql
                    status = "enabled" if self.show_sql else "disabled"
                    print(Fore.YELLOW + f"SQL display {status}" + Style.RESET_ALL)
                
                else:
                    # Process as question
                    self.process_question(user_input)
            
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\n\nInterrupted. Type /exit to quit." + Style.RESET_ALL)
            
            except Exception as e:
                print(Fore.RED + f"\nUnexpected error: {e}" + Style.RESET_ALL)
    
    def cleanup(self):
        """Clean up resources"""
        if self.conn:
            self.conn.close()


def main():
    """Main entry point"""
    cli = CLI()
    try:
        cli.run()
    finally:
        cli.cleanup()


if __name__ == "__main__":
    main()
