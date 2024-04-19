import sys
import toml
from omegaconf import OmegaConf
from query import VectaraQuery
import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from PIL import Image
from functools import partial
import openai 
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.tools import DuckDuckGoSearchRun
import json
import requests
import re
from urllib.parse import quote
import config
load_dotenv()
app = Flask(__name__)
ai_key = os.getenv("corpus_key")

customer_id = 2977603074
corpus_ids = [7]
vq = VectaraQuery(api_key, customer_id, corpus_ids)

def query_web(query):
    openai_api_key = os.getenv("openai_key")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True)
    search = DuckDuckGoSearchRun(name="Search")
    search_agent = initialize_agent([search], llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True)
    response = search_agent.run(query)
    return response

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        query_str = request.form["query"]
        
        # Try getting response from VectaraQuery
        response = vq.submit_query(query_str)
        factual_consistency_score = get_factual_consistency_score(response)
        
        # If response is not satisfactory (score < 0.30), query the web
        if factual_consistency_score > 0.30:
            response = query_web(query_str)
        
        return render_template("index.html", query=query_str, response=response)
    
    return render_template("index.html", query="", response="")

def get_factual_consistency_score(response):
    factual_consistency_score = 0
    # Extract factual consistency score from response
    match = re.search(r'Factual Consistency Score: (\d+\.\d+)', response)
    if match:
        factual_consistency_score = float(match.group(1))
    return factual_consistency_score

if __name__ == "__main__":
    app.run(debug=True)
