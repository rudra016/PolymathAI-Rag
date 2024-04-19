import os
import requests
import json
import re
from urllib.parse import quote
from together import Together
from markdown import markdown
from flask import Flask, render_template, request
from query import VectaraQuery
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize VectaraQuery instance
api_key = os.getenv("API_KEY")  # Assuming the API key is stored in an environment variable
customer_id = 2977603074
corpus_ids = [7]
vq = VectaraQuery(api_key, customer_id, corpus_ids)

# Initialize Together client
together_api_key = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=together_api_key)

def query_web(query):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True)
    search = DuckDuckGoSearchRun(name="Search")
    search_agent = initialize_agent([search], llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True)
    response = search_agent.run(query)
    return response

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        query_str = request.form["query"]
        search_internet = "search_internet" in request.form  # Check if the checkbox is clicked
        
        # Submit query to Vectara
        response = vq.submit_query(query_str)
        
        # If internet search option is selected, include internet search results
        if search_internet:
            response += "\n\nInternet Search Results:\n"
            internet_response = query_web(query_str)
            response += internet_response
        
        return render_template("index.html", query=query_str, response=response, search_internet=search_internet)
    
    return render_template("index.html", query="", response="", search_internet=False)

if __name__ == "__main__":
    app.run(debug=True)
