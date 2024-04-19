import os
import requests
import json
import re
from urllib.parse import quote
from together import Together
from markdown import markdown
import config


# Load environment variables from .env file

# Access the value of ai_key
together_api_key = config.together_api_key
# Set your Together.io API key


# Initialize Together client
client = Together(api_key=together_api_key)

# Function to extract text between specified tags
def extract_between_tags(text, start_tag, end_tag):
    start_index = text.find(start_tag)
    end_index = text.find(end_tag, start_index)
    return text[start_index + len(start_tag):end_index - len(end_tag)]

class VectaraQuery():
    def __init__(self, api_key: str, customer_id: int, corpus_ids: list):
        self.customer_id = customer_id
        self.corpus_ids = corpus_ids
        self.api_key = api_key

    def submit_query(self, query_str: str):
        corpora_key_list = [{
            'customer_id': str(self.customer_id), 'corpus_id': str(corpus_id), 'lexical_interpolation_config': {'lambda': 0.025}
        } for corpus_id in self.corpus_ids]

        endpoint = f"https://api.vectara.io/v1/query"
        start_tag = "%START_SNIPPET%"
        end_tag = "%END_SNIPPET%"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "customer-id": str(self.customer_id),
            "x-api-key": self.api_key,
            "grpc-timeout": "60S"
        }
        body = {
            'query': [
                {
                    'query': query_str,
                    'start': 0,
                    'numResults': 7,
                    'corpusKey': corpora_key_list,
                    'context_config': {
                        'sentences_before': 3,
                        'sentences_after': 3,
                        'start_tag': start_tag,
                        'end_tag': end_tag,
                    },
                    'summary': [
                        {
                            'responseLang': 'eng',
                            'maxSummarizedResults': 7,
                            'factual_consistency_score': True
                        }
                    ]
                }
            ]
        }

        response = requests.post(endpoint, data=json.dumps(body), verify=True, headers=headers)
        if response.status_code != 200:
            print(f"Query failed with code {response.status_code}, reason {response.reason}, text {response.text}")
            return "Sorry, something went wrong in my brain. Please try again later."

        res = response.json()

        summary = res['responseSet'][0]['summary'][0]['text']
        factual_consistency_score = res['responseSet'][0]['summary'][0]['factualConsistency']['score']
        responses = res['responseSet'][0]['response']
        docs = res['responseSet'][0]['document']
        pattern = r'\[\d{1,2}\]'
        matches = [match.span() for match in re.finditer(pattern, summary)]

        # figure out unique list of references
        refs = []
        for match in matches:
            start, end = match
            response_num = int(summary[start + 1:end - 1])
            doc_num = responses[response_num - 1]['documentIndex']
            metadata = {item['name']: item['value'] for item in docs[doc_num]['metadata']}
            text = extract_between_tags(responses[response_num - 1]['text'], start_tag, end_tag)
            url = f"{metadata['url']}#:~:text={quote(text)}"
            if url not in refs:
                refs.append(url)

        # replace references with markdown links
        refs_dict = {url: (inx + 1) for inx, url in enumerate(refs)}
        for match in reversed(matches):
            start, end = match
            response_num = int(summary[start + 1:end - 1])
            doc_num = responses[response_num - 1]['documentIndex']
            metadata = {item['name']: item['value'] for item in docs[doc_num]['metadata']}
            text = extract_between_tags(responses[response_num - 1]['text'], start_tag, end_tag)
            url = f"{metadata['url']}#:~:text={quote(text)}"
            citation_inx = refs_dict[url]
            summary = summary[:start] + f'[[{citation_inx}]]({url})' + summary[end:]

        # Format the response with factual consistency score
        formatted_response = f"{summary}\n\nFactual Consistency Score: {factual_consistency_score}"
       

        # Check if the factual consistency score is below 0.20
        if factual_consistency_score < 0.30:
            # Use Together.io to generate a response
            try:
                response = client.chat.completions.create(
                    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    messages=[{"role": "user", "content": query_str}],
                )
                together_response = response.choices[0].message.content
                formatted_response = f"LLm's response since query not in corpus: {together_response}\n\nFactual Consistency Score for corpus provided reponse: {factual_consistency_score}"
            except Exception as e:
                print(f"Error occurred with Together.io: {e}")

        html_response = markdown(formatted_response, extensions=['fenced_code'])


        return html_response

