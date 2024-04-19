import sys
import toml
from omegaconf import OmegaConf
from query import VectaraQuery
import os
from flask import Flask, render_template, request

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

app = Flask(__name__)
api_key = config.corpus_api_key

customer_id = 2977603074
corpus_ids = [7]
vq = VectaraQuery(api_key, customer_id, corpus_ids)

def query_web(query):
    openai_api_key = config.openai_api_key
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
        
        # Try getting response from VectaraQuery
        response = vq.submit_query(query_str)
        factual_consistency_score = get_factual_consistency_score(response)
        
        # If checkbox is clicked or response is not satisfactory, query the web
        if search_internet or factual_consistency_score < 0.30:
            response = query_web(query_str)
        
        return render_template("index.html", query=query_str, response=response, search_internet=search_internet)
    
    return render_template("index.html", query="", response="", search_internet=False)

def get_factual_consistency_score(response):
    factual_consistency_score = 0
    # Extract factual consistency score from response
    match = re.search(r'Factual Consistency Score: (\d+\.\d+)', response)
    if match:
        factual_consistency_score = float(match.group(1))
    return factual_consistency_score

if __name__ == "__main__":
    app.run(debug=True)
