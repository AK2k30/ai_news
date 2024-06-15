import os
from flask import Flask #type: ignore
from dotenv import load_dotenv #type: ignore
import google.generativeai as genai #type: ignore

load_dotenv()

app = Flask(__name__)

from news_service import news_service_bp
from research_paper_service import research_papers_service_bp

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

app.register_blueprint(news_service_bp)
app.register_blueprint(research_papers_service_bp)

if __name__ == '__main__':
    app.run(debug=True)
