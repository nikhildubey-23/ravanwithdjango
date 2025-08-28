from django.shortcuts import render, redirect
from django.http import JsonResponse
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import re
import logging

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Use /tmp directory for the database on Vercel, otherwise use local file for development
if os.environ.get('VERCEL'):
    DATABASE_PATH = os.path.join('/tmp', 'database.db')
else:
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def create_database():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 question TEXT, 
                 answer TEXT, 
                 timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_to_history(question, answer):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO user_history (question, answer, timestamp) VALUES (?, ?, ?)", (question, answer, timestamp))
    conn.commit()
    conn.close()

def view_history():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM user_history")
    rows = c.fetchall()
    conn.close()
    return rows

def clear_history():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM user_history")
    conn.commit()
    conn.close()

def index(request):
    if not os.path.exists(DATABASE_PATH):
        create_database()

    output = None
    output_language = "plaintext"  # Default language
    if request.method == 'POST':
        try:
            user_input = request.POST['user_input']
            llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=GEMINI_API_KEY,
                temperature=0
            )
            prompt_template = create_prompt()
            chain_extract = prompt_template | llm 
            res = chain_extract.invoke(user_input)
            output = re.sub(r'<think>.*?</think>', '', res.content, flags=re.DOTALL).strip()  # Remove <think> tags and their content

            # Preprocess the output to replace ** with <h2> tags only outside of code blocks
            def replace_double_asterisks(match):
                text = match.group(0)
                return re.sub(r'\*\*(.*?)\*\*', r'<h2>\1</h2>', text)

            output = re.sub(r'(?s)(```.*?```|[^`]+)', replace_double_asterisks, output)
            output = re.sub(r'```(\w+)\n(.*?)```', r'<pre><code class="language-\1">\2</code></pre>', output, flags=re.DOTALL)  # Wrap code blocks in <pre><code> tags

            save_to_history(user_input, output)
            return render(request, 'index.html', {'history': view_history(), 'output': output, 'output_language': output_language})
        except Exception as e:
            logging.error(f"Error processing request: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, 'index.html', {'history': view_history(), 'output': output, 'output_language': output_language})

def view_history_page(request):
    rows = view_history()
    history = [
        {'id': row[0], 'question': row[1], 'answer': row[2], 'timestamp': row[3]}
        for row in rows
    ]
    return render(request, 'history.html', {'history': history})

def clear(request):
    clear_history()
    return redirect('index')

def about(request):
    return render(request, 'about.html')

def reachout(request):
    return render(request, 'reachout.html')

def create_prompt():
    prompt_template = """
Ravan Offensive Security AI Assistant:
You are an expert in cybersecurity and web development.
When you answer, ONLY provide the final, user-facing answer. Do NOT include your internal thoughts, reasoning, or planning. Do NOT explain what you are about to do. Just answer the user's question directly and concisely.
If the answer is best presented in a table, output the table in valid HTML <table> format (with <table>, <thead>, <tbody>, <tr>, <th>, <td> tags). Do not use markdown for tables. Only use HTML for tables.

Please respond to the following prompt:
{input}
"""
    return PromptTemplate.from_template(prompt_template)