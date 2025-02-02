# Ravanai

Ravanai is a Django-based AI assistant designed for cybersecurity and web development tasks. It leverages Langchain and Groq API to process user queries and provide responses.

## Features
- **Cybersecurity Expert**: Provides security-related solutions.
- **Web Development Assistance**: Helps in coding and designing.
- **Natural Language Processing**: Understands English queries.
- **SQLite Database Integration**: Stores user query history.
- **Interactive Web Interface**: Frontend powered by Django templates.

## Installation

### Prerequisites
- Python 3.8+
- Django 5.1.5
- SQLite (included with Python)
- A Groq API key

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/ravanai.git
   cd ravanai
   ```
2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   Create a `.env` file in the project root and add:
   ```env
   SECRET_KEY=your_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   GROQ_API_KEY=your_groq_api_key
   ```
5. Apply database migrations:
   ```sh
   python manage.py migrate
   ```
6. Run the development server:
   ```sh
   python manage.py runserver
   ```

## Project Structure
```
Ravanai/
│-- myapp/
│   │-- views.py
│   │-- templates/
│-- Ravanai/
│   │-- settings.py
│-- static/
│-- .env
│-- manage.py
```

## Usage
1. Open `http://127.0.0.1:8000/` in a browser.
2. Enter your question related to cybersecurity or web development.
3. View the AI-generated response.
4. Check query history on the history page.

## Deployment
### Deploying on Vercel
1. Install the Vercel CLI:
   ```sh
   npm install -g vercel
   ```
2. Login to Vercel:
   ```sh
   vercel login
   ```
3. Deploy the project:
   ```sh
   vercel
   ```
4. Set environment variables on Vercel dashboard.
---
Enjoy using Ravanai! 🚀

