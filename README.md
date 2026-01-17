<<<<<<< HEAD
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
=======
# Talk_to_your_db
Overview

Talk to Your DB is an intelligent natural language interface for databases that allows users to ask questions in plain English and receive accurate, safe, and explainable answers from a SQL database.
Unlike naive text-to-SQL systems, this solution reasons about the schema, handles ambiguity, validates queries, and explains its decision process.

The system is built and demonstrated using the Chinook SQLite database.

🎯 Problem Statement

Writing SQL requires knowledge of table names, relationships, joins, and syntax. Business users and analysts often struggle to translate questions into correct queries.
Naive LLM-based approaches fail due to schema hallucination, ambiguity, unsafe queries, and lack of reasoning.

✅ Solution Highlights

Natural Language → SQL → Human-readable Answer

Schema-aware reasoning (no hardcoded queries)

Safe, read-only SQL execution

Handles ambiguous, multi-step, and meta queries

Shows reasoning trace for transparency

Graceful handling of empty results and errors

🧠 System Architecture
User Question
   ↓
Intent Understanding & Reasoning
   ↓
Schema Exploration (if required)
   ↓
SQL Generation (Safe & Optimized)
   ↓
Query Validation
   ↓
Execution on SQLite DB
   ↓
Answer + Explanation

🗂 Project Structure
Talk_to_your_data/
│
├── app/
│   └── app.py              # Streamlit UI
│
├── model/
│   ├── train.py            # (Optional) Model training
│   ├── infer.py            # SQL generation logic
│   └── nl2sql_model/       # Fine-tuned model files
│
├── data/
│   └── chinook.db          # SQLite database (read-only)
│
├── utils/
│   ├── schema_reader.py    # Schema exploration
│   ├── sql_validator.py    # Safety checks
│   └── executor.py         # Query execution
│
├── requirements.txt
└── README.md

🧾 Database

Database: Chinook (SQLite)

Tables: Artists, Albums, Tracks, Customers, Invoices, Employees, Playlists, etc.

Source: https://github.com/lerocha/chinook-database

⚙️ Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/your-username/Talk_to_your_data.git
cd Talk_to_your_data

2️⃣ Create Virtual Environment
python -m venv venv


Activate:

Windows

venv\Scripts\activate


Linux / Mac

source venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

▶️ How to Run the Application
Run Streamlit App
streamlit run app/app.py


If port is busy:

streamlit run app/app.py --server.port 8502


Open in browser:

http://localhost:8501

🧪 Sample Queries Supported
Simple

How many customers are from Brazil?

List all albums by AC/DC

Moderate

Which 5 artists have the most tracks?

Total revenue by country, sorted highest first

Multi-Step Reasoning

Customers who purchased tracks from both Rock and Jazz

Which artist has tracks in the most playlists?

Ambiguous (Handled Gracefully)

Show me recent orders

Who are our best customers?

Meta / Introspection

What tables exist in this database?

Show me the schema of the Invoice table

🔐 Safety Guarantees

Read-only SQL queries only

No INSERT, UPDATE, DELETE, DROP

Avoids SELECT *

Limits large result sets

Prevents runaway queries

💡 What Makes This Better Than Naive Approaches
Naive Text-to-SQL	This System
Hallucinates schema	Explores schema
No reasoning	Step-by-step reasoning
Unsafe queries	Read-only validated SQL
Fails silently	Explains failures
No transparency	Shows reasoning trace
⚠️ Limitations

Accuracy depends on schema clarity

Highly ambiguous questions may require clarification

Large databases may require further optimization

🚀 Future Enhancements

Automatic self-correction on failed queries

Query cost estimation

Multi-database support

Voice-based input

Role-based access control

👨‍💻 Author

Krish
Department of Computer Science and Engineering
Specialization: Big Data Analytics & Cloud Computing
>>>>>>> 56c05e3d3667ea23412e0b4f073afaecda3d3b53
