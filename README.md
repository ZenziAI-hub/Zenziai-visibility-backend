# AI Visibility Search Tool - Backend API

A comprehensive Flask API that analyzes company visibility across multiple AI platforms using proprietary ranking methodologies.

## Overview

This backend service provides REST API endpoints to analyze how well companies are represented across various AI platforms including ChatGPT, Claude, Perplexity AI, Arc Search, and SearchGPT.

## Features

### AI Platforms Analyzed
- **ChatGPT** (OpenAI)
- **Claude** (Anthropic) 
- **Perplexity AI**
- **Arc Search** (The Browser Company)
- **SearchGPT** (OpenAI)

### Proprietary Ranking Methodologies

1. **CIDR (Contextual Intent-Driven Ranking)**
   - Measures how well LLMs understand the intent behind queries related to the company
   - Analyzes relevance, completeness, accuracy, and contextual understanding

2. **SCVS (Source Credibility & Verifiability Score)**
   - Evaluates company representation in verifiable, reputable, and cited sources
   - Checks domain authority, reputation, and citation quality

3. **ACSO (Adaptive Content Structure Optimization)**
   - Assesses if company's online content is structured for easy AI parsing and summarization
   - Analyzes readability, heading structure, semantic markup, and summarizability

4. **UIFL (User Interaction & Feedback Loop)**
   - Estimates positive engagement potential through AI tools
   - Evaluates response sentiment, actionability, and follow-up potential

## API Endpoints

### Analysis Endpoints
- `POST /api/analyze` - Analyze a company's AI visibility
- `GET /api/analysis/{id}` - Get specific analysis by ID
- `GET /api/analysis/company/{name}` - Get latest analysis for a company
- `GET /api/analysis` - Get all analyses with pagination

### Information Endpoints
- `GET /api/platforms` - Get list of supported AI platforms
- `GET /api/methodologies` - Get list of ranking methodologies

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ZenziAI-hub/Zenziai-visibility-backend.git
cd Zenziai-visibility-backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_API_BASE="https://api.openai.com/v1"
```

5. Run the application:
```bash
python src/main.py
```

The API will be available at `http://localhost:5000`

## Project Structure

```
├── src/
│   ├── models/          # Database models
│   │   ├── user.py      # User model
│   │   └── analysis.py  # Company analysis model
│   ├── routes/          # API route handlers
│   │   ├── user.py      # User routes
│   │   └── analysis.py  # Analysis routes
│   ├── services/        # Business logic
│   │   └── ai_analyzer.py  # AI analysis service
│   ├── static/          # Static files (frontend build)
│   ├── database/        # SQLite database
│   └── main.py          # Application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Usage Example

### Analyze a Company
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Apple"}'
```

### Get Analysis Results
```bash
curl http://localhost:5000/api/analysis/company/Apple
```

## Response Format

Analysis results include scores (0-100) for each platform and methodology:

```json
{
  "company_name": "Apple",
  "analysis_date": "2025-08-06T10:30:00",
  "chatgpt_scores": {
    "cidr": {"score": 85, "comment": "Excellent intent understanding"},
    "scvs": {"score": 92, "comment": "Strong source credibility"},
    "acso": {"score": 78, "comment": "Good content structure"},
    "uifl": {"score": 88, "comment": "High engagement potential"}
  },
  "insights": "Apple performs best in SCVS with high credibility scores..."
}
```

## Technologies Used

- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **OpenAI API** - ChatGPT integration
- **SQLite** - Database
- **Flask-CORS** - Cross-origin resource sharing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is proprietary software developed for ZenziAI.

## Contact

For questions or support, contact: hello@zenziai.com

