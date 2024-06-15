# research_papers_service.py

from flask import Blueprint, jsonify, current_app #type: ignore
import requests #type: ignore
import google.generativeai as genai #type: ignore
import xml.etree.ElementTree as ET
import os

research_papers_service_bp = Blueprint('research_papers_service', __name__)

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

@research_papers_service_bp.route('/api/research_papers', methods=['GET'])
def research_papers():
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # Example usage, adjust as needed
    url = 'http://export.arxiv.org/api/query'
    params = {
        'search_query': 'cat:cs.AI',  # Search query for AI category
        'sortBy': 'submittedDate',
        'sortOrder': 'descending',
        'max_results': 10,  # Limiting to 10 papers for example
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        research_papers_data = response.content
        summarized_papers = parse_and_summarize_research_papers(research_papers_data)
        return jsonify(summarized_papers)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching research papers: {e}")
        return jsonify({"error": "Failed to fetch research papers"}), 500

def parse_and_summarize_research_papers(xml_data):
    try:
        root = ET.fromstring(xml_data)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        for entry in root.findall('atom:entry', namespace):
            title = entry.find('atom:title', namespace).text
            summary = entry.find('atom:summary', namespace).text
            link = entry.find('atom:link[@rel="alternate"]', namespace).attrib['href']
            
            # Summarize the abstract
            summary = summarize_text(summary)
            
            papers.append({
                'title': title,
                'summary': summary,
                'url': link
            })
        
        return papers
    
    except Exception as e:
        print(f"Error parsing and summarizing papers: {e}")
        return []
