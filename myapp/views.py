from django.shortcuts import render, redirect
from django.http import JsonResponse
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import re
import logging

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Use /tmp directory for the database on Vercel
DATABASE_PATH = os.path.join('/tmp', 'database.db')

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
            llm = ChatGroq(
                temperature=0, 
                groq_api_key=GROQ_API_KEY, 
                model_name="deepseek-r1-distill-llama-70b"
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
    return render(request, 'history.html', {'history': view_history()})

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
You are an expert in cybersecurity and can provide security solutions to users.
You can write code in Python and other languages.
You can understand English languages.
You are a very good web developer and code designer.
Your goal is to assist users with their cybersecurity needs.
You provide answer only for the asked question no need of extra information.
Your developer name is Ravan
Please respond to the following prompt:
{input}
"""
    return PromptTemplate.from_template(prompt_template)