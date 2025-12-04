# AI Research & Presentation Generator

An intelligent Flask-based web application that performs automated online research, analyzes extracted content using AI, and generates a structured presentation in Markdown format. It combines web scraping, AI-powered analysis, and automated report creation into one powerful tool.

## Features

### 1. Automated Online Research
- Searches the internet using DuckDuckGo.
- Identifies reliable sources (IEEE, MIT, arXiv, Wikipedia, etc.).
- Extracts content using BeautifulSoup.

### 2. AI-Powered Content Analysis
- Uses OpenAI GPT (if API key exists) to extract key points, challenges, developments, and future outlook.
- Produces structured JSON output.

### 3. Offline Fallback Mode
- Keyword-based analysis when OpenAI key is missing.
- Generates mock research data.

### 4. Presentation Generation
- Creates Markdown-based reports:
  - Executive summary
  - Key findings
  - Challenges
  - Future outlook
  - Sources

### 5. Background Processing
- Runs research tasks in background threads.

### 6. Flask Web Interface
- /research – Start research
- /research/<id> – Track progress
- /download/<id> – Download Markdown file

## Installation

```bash
pip install -r requirements.txt
```

Generate .env file:
```bash
python generate_keys.py
```

Run app:
```bash
python app.py
```

## Project Structure

```
app.py
research_agent.py
presentation_generator.py
generate_keys.py
main.py
requirements.txt
uploads/
```

## License
MIT License
