# 🚀 Running the Chatbot

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Key
```powershell
# Windows PowerShell
$env:GOOGLE_API_KEY="your-api-key-here"
```

### 3. Run the Chatbot
```bash
streamlit run streamlit_app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Features

✅ **Chat Interface** - Natural conversation with your database  
✅ **SQL Display** - See the generated queries (toggle in sidebar)  
✅ **Reasoning Traces** - Understand the AI's thinking (toggle in sidebar)  
✅ **Example Questions** - Click to try different complexity levels  
✅ **Clean UI** - Professional Streamlit interface  

## Example Questions

**Simple:**
- "How many customers are from Brazil?"
- "List all albums by AC/DC"

**Moderate:**
- "Which 5 artists have the most tracks?"
- "Total revenue by country"

**Complex:**
- "Customers who bought both Rock and Jazz"
- "Which artist has tracks in the most playlists?"

**Meta:**
- "What tables exist?"
- "Show schema of Invoice table"

## Troubleshooting

**API Key Error?**
Make sure you've set the `GOOGLE_API_KEY` environment variable:
```powershell
$env:GOOGLE_API_KEY="your-actual-key"
```

**Port Already in Use?**
Run on a different port:
```bash
streamlit run streamlit_app.py --server.port 8502
```

**Database Not Found?**
The app will automatically download the Chinook database on first run.

## For Hackathon Demo

1. Open the app
2. Show example questions in sidebar
3. Ask a simple question first
4. Toggle SQL display to show the query
5. Ask a complex question to show reasoning
6. Highlight the error recovery if a query fails

Enjoy! 🎉
