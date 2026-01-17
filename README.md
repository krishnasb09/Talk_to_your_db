# Talk-to-Your-Data: Intelligent NL2SQL System

An intelligent natural language to SQL system that goes beyond naive prompt-to-SQL approaches through multi-step reasoning, schema exploration, and error recovery.

## Features

- **Multi-step Reasoning**: Breaks down complex questions into manageable sub-problems
- **Schema Exploration**: Actively explores database schema instead of hallucinating table names
- **Error Recovery**: Self-corrects when queries fail
- **Safety First**: Enforces read-only queries, prevents SELECT *, adds LIMIT clauses
- **Transparent Reasoning**: Shows complete decision-making process
- **Ambiguity Handling**: States explicit assumptions or asks for clarification

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Google Gemini API key:
```bash
# Windows PowerShell
$env:GOOGLE_API_KEY="your-api-key-here"

# Or set it when running the program
```

3. Run the CLI:
```bash
python cli.py
```

## Usage

The system will automatically download the Chinook database on first run.

### Interactive Mode

```bash
python cli.py
```

Available commands:
- `/help` - Show help message
- `/reasoning` - Toggle reasoning trace display
- `/sql` - Toggle SQL query display  
- `/schema` - Show database schema
- `/examples` - Show example questions
- `/exit` - Exit

### Example Questions

**Simple:**
- "How many customers are from Brazil?"
- "List all albums by AC/DC"

**Moderate:**
- "Which 5 artists have the most tracks?"
- "Total revenue by country, sorted highest first"

**Complex:**
- "Customers who purchased tracks from both Rock and Jazz genres"
- "Which artist has tracks in the most playlists?"

**Multi-step:**
- "Are there any genres with no sales?"
- "Which customers have never made a purchase?"

**Meta:**
- "What tables exist?"
- "Show me the schema of the Invoice table"

## Architecture

```
┌─────────────────┐
│  User Question  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Question Analyzer│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Schema Explorer  │ ◄─── Uses PRAGMA & sqlite_master
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Reasoning Engine│ ◄─── LLM-powered analysis
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQL Generator  │ ◄─── Safety validation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Query Executor  │ ◄─── With error recovery
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Result Formatter │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Human Answer    │
└─────────────────┘
```

## Key Differentiators

### vs. Naive Approaches

| Aspect | Naive Approach | Our System |
|--------|---------------|------------|
| Schema Knowledge | Hallucinates table names | Active schema exploration |
| Complex Queries | Single-shot SQL generation | Multi-step reasoning |
| Errors | Returns error to user | Self-correction with retry |
| Ambiguity | Arbitrary assumptions | Explicit assumptions or clarification |
| Safety | No validation | Strict read-only validation |
| Transparency | Black box | Full reasoning trace |

## Project Structure

```
Talk_to_your_data/
├── setup_database.py    # Database download & setup
├── schema_explorer.py   # Schema introspection
├── sql_generator.py     # SQL generation with safety
├── query_executor.py    # Query execution
├── result_formatter.py  # Human-readable output
├── agent.py            # Core reasoning agent
├── cli.py              # Interactive CLI
└── requirements.txt    # Dependencies
```

## License

MIT License
