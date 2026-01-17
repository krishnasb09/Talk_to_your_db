# Quick Start Guide

## Installation

1. **Clone/Navigate to the project directory**:
```bash
cd Talk_to_your_data
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up Gemini API key**:

Get your free API key from: https://aistudio.google.com/app/apikey

**Windows PowerShell**:
```powershell
$env:GOOGLE_API_KEY="your-api-key-here"
```

**Windows Command Prompt**:
```cmd
set GOOGLE_API_KEY=your-api-key-here
```

**Linux/Mac**:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

## Running the System

### Interactive CLI Mode

```bash
python cli.py
```

The system will:
1. Download the Chinook database (if not already present)
2. Initialize the reasoning agent
3. Open an interactive prompt

### Available Commands

- `/help` - Show help and commands
- `/examples` - See example questions
- `/schema` - Display database schema
- `/sql` - Toggle SQL display on/off
- `/reasoning` - Toggle reasoning trace on/off
- `/exit` - Exit the program

### Example Session

```
❯ What tables exist?

Answer:
✓ Database contains 11 tables:
1. Album
2. Artist
3. Customer
...

❯ How many customers are from Brazil?

Generated SQL:
SELECT COUNT(*) as total FROM Customer WHERE Country = 'Brazil';

Answer:
✓ Found 5 result(s).

⏱ Execution time: 0.003s | Rows: 1

❯ Which 5 artists have the most tracks?

Generated SQL:
SELECT ar.Name, COUNT(t.TrackId) as TrackCount
FROM Artist ar
JOIN Album al ON ar.ArtistId = al.ArtistId
JOIN Track t ON al.AlbumId = t.AlbumId
GROUP BY ar.ArtistId
ORDER BY TrackCount DESC
LIMIT 5;

Answer:
✓ Found 5 result(s):

Name               | TrackCount
-------------------|------------
Iron Maiden        | 213
U2                 | 135
Led Zeppelin       | 114
Metallica          | 112
Deep Purple        | 92
```

## Running Tests

Run the comprehensive test demonstration:

```bash
python test_demo.py
```

This will run 12 test queries across different complexity levels:
- Simple queries
- Moderate complexity
- Multi-step reasoning
- Ambiguous questions
- Meta-queries

For each test, you'll see:
1. Why a naive approach would fail
2. How our system handles it
3. The generated SQL
4. The results

## Troubleshooting

### "GOOGLE_API_KEY not set"
Set the environment variable as shown above.

### "No module named 'google.generativeai'"
Run: `pip install -r requirements.txt`

### Database download fails
Manually download from: https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite
Save as `chinook.db` in the project directory.

## System Capabilities

✅ **Simple queries**: Direct lookups and counts
✅ **Complex joins**: Multi-table queries with aggregations
✅ **Multi-step reasoning**: Break down complex questions
✅ **Ambiguity handling**: Explicit assumptions or clarification
✅ **Error recovery**: Self-correction when queries fail
✅ **Meta-queries**: Schema introspection
✅ **Safety**: Read-only validation, no dangerous operations
✅ **Transparency**: Full reasoning traces

## What Makes This Different?

Unlike naive text-to-SQL approaches, our system:
- **Explores** the schema instead of hallucinating table names
- **Reasons** through complex questions step-by-step
- **Recovers** from errors automatically
- **Validates** all queries for safety
- **Explains** its decision-making process

See [COMPARISON.md](COMPARISON.md) for detailed analysis.

## Example Questions to Try

**Simple**:
- "How many customers are from Brazil?"
- "List all albums by AC/DC"

**Moderate**:
- "Which 5 artists have the most tracks?"
- "Total revenue by country, sorted highest first"

**Complex**:
- "Customers who purchased tracks from both Rock and Jazz genres"
- "Which artist has tracks in the most playlists?"

**Ambiguous** (system will state assumptions):
- "Show me recent orders"
- "Who are our best customers?"

**Multi-step**:
- "Are there any genres with no sales?"
- "Which customers have never made a purchase?"

**Meta**:
- "What tables exist?"
- "Show me the schema of the Invoice table"

Enjoy exploring your data! 🚀
