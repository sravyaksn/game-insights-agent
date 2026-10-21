# Game Insights Agent

An AI-powered game review analysis agent that combines **Retrieval-Augmented Generation (RAG)**, **SQL analytics**, and **LLM tool calling** to answer questions about Steam games using evidence from real player reviews.

## Project Overview

The Game Insights Agent allows users to ask natural-language questions about games, player sentiment, and review trends.

It uses two complementary approaches:

- **SQL analytics:** Calculates structured metrics such as positive review percentages and game rankings.
- **RAG:** Searches player reviews for relevant feedback and examples.

The agent uses Anthropic Claude to select tools, interpret results, and generate structured answers.

## Technologies

- Python
- Anthropic Claude API
- SQLite
- ChromaDB
- Retrieval-Augmented Generation (RAG)
- Steam API
- Python unittest

## Architecture

```text
User Question
      |
      v
Anthropic Claude Agent
      |
      +--------------------+
      |                    |
      v                    v
  run_sql()         search_reviews()
      |                    |
      v                    v
 SQLite Database       ChromaDB
      |                    |
      +---------+----------+
                |
                v
       Evidence Verification
                |
                v
       Structured JSON Answer
```

## Features

### 1. Natural-Language Game Analytics

Users can ask questions such as:

- Which games have the highest positive review percentage?
- What are the most common complaints about Apex Legends?
- Compare player sentiment for Cyberpunk 2077 and Battlefield 2042.
- Find two positive reviews for the highest-rated game.

### 2. SQL Analytics

The agent executes guarded, read-only SQL queries to analyze structured game and review data.

### 3. Semantic Review Search

ChromaDB enables retrieval of player reviews relevant to a question, including sentiment-based filtering.

### 4. Evidence Verification

The project includes verification mechanisms for:

- Review ID existence
- Exact quotation matching
- Structured SQL evidence values
- Requested quotation counts
- Answer formatting

Answers that fail these verification checks are rejected.

**Limitations:** Verification checks the evidence fields supplied by the agent. It does not independently prove every statement in the generated answer or the correctness of every SQL query.

### 5. Automated Testing

The project includes 13 automated tests covering SQL values, review validation, quotations, answer formatting, and evidence enforcement.

## Dataset

The project analyzes Steam reviews for six games:

1. Apex Legends
2. Battlefield 2042
3. Cyberpunk 2077
4. Elden Ring
5. Baldur's Gate 3
6. It Takes Two

The local dataset currently contains approximately 1,468 reviews.

## Installation

### 1. Clone the repository

```bash
git clone <YOUR-REPOSITORY-URL>
cd game-rag-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows CMD:

```cmd
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Anthropic API key

In Windows CMD:

```cmd
set ANTHROPIC_API_KEY=your_api_key_here
```

Never commit API keys to GitHub.

### 5. Ingest game reviews

```bash
python ingest.py
```

This populates the local SQLite and ChromaDB databases.

### 6. Run the agent

```bash
python agent.py
```

## Testing

Run the automated test suite:

```bash
python -m unittest test_agent.py -v
```

The current suite contains 13 tests. Some tests require the Steam review database to have been populated by the ingestion script.

## Example Questions

**SQL analytics**

> Which three games have the highest positive review percentages?

**Review search**

> Find two negative Apex Legends reviews mentioning matchmaking.

**Combined SQL + RAG**

> Which game has the highest positive review percentage? Include two positive player quotations.

## Future Improvements

- Add isolated test fixtures and mocked LLM responses.
- Improve natural-language query handling.
- Add a Streamlit web interface.
- Expand the number of supported games.
- Improve citation and numerical claim verification.
- Add automated evaluation of answer quality.

## Security Considerations

The agent restricts SQL tool usage to read-only queries and treats retrieved review text as untrusted input.

Additional production security measures, including stronger SQL parsing and sandboxing, would be required before deploying the system to untrusted users.