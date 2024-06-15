# news_service.py

from flask import Blueprint, jsonify, current_app #type: ignore
import requests #type: ignore
import google.generativeai as genai #type: ignore
import xml.etree.ElementTree as ET 
import os

news_service_bp = Blueprint('news_service', __name__)

# Function to summarize text using Gemini API
def summarize_text(text):
    if not text:
        return "Summary not available due to empty content."
    try:
        with current_app.app_context():
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 1,
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 8192,
                    "response_mime_type": "text/plain",
                },
            )
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(text)
            return response.text
    except genai.types.generation_types.StopCandidateException as e:
        # Handle the exception gracefully
        print(f"StopCandidateException occurred: {e}")
        return "Summary not available due to content restrictions."

@news_service_bp.route('/api/news', methods=['GET'])
def news():
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    url = f'https://newsapi.org/v2/top-headlines'
    params = {
        'category': 'technology',
        'apiKey': NEWS_API_KEY,
        'language': 'en'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        news_data = response.json()
        if 'articles' not in news_data:
            return jsonify({"error": "Failed to fetch news articles"}), 500

        summarized_news = []

        for article in news_data['articles']:
            content = article.get('content')
            summary = summarize_text(content)
            summarized_news.append({
                'title': article['title'],
                'summary': summary,
                'url': article['url']
            })

        return jsonify(summarized_news)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news articles: {e}")
        return jsonify({"error": "Failed to fetch news articles"}), 500
