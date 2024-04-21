# ➗⚙️ Polymath AI

## 🗒️ Introduction

Welcome to Polymath AI, your cutting-edge RAG (Retriever-Reader-Generator) question answering bot tailored for the Gen AI documentation landscape. Polymath AI integrates the power of various knowledge bases including Vectara, Langchain, OpenAI, Meta, and more, serving as your indispensable resource hub for navigating the vast terrain of generative AI technologies.

## 🌟 Key Features

- **Comprehensive Knowledge Access**: Gain unparalleled access to a wealth of information and insights from diverse knowledge bases.
- **Seamless Comparison**: Compare tools and resources across multiple platforms effortlessly.
- **Up-to-Date Information**: Access the most relevant and current information available, sourced from both internal and external knowledge bases.
- **Factual Consistency Evaluation**: Evaluate the factual accuracy of AI-generated summaries with the Factual Consistency Score.
- **Integration with LLm**: Seamless integration with LLm for additional responses when factual consistency score falls below a certain threshold.

## Instructions

### Setup

1. Clone the Polymath AI repository from GitHub.

```bash
git clone https://github.com/your_username/polymath-ai.git
```

2. Navigate to the project directory.

```bash
cd polymath-ai
```

3. Install the required dependencies.

```bash
pip install -r requirements.txt
```

4. Set up environment variables by creating a `.env` file and adding the necessary variables:

```
corpus_api_key=YOUR_CORPUS_API_KEY
together_api_key=YOUR_TOGETHER_API_KEY
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

### Usage

1. Run the Flask application.

```bash
flask run
```

2. Access Polymath AI through your web browser at `http://localhost:5000`.

3. Enter your query in the provided input field and click the "Ask" button.

4. Optionally, check the "Search Internet" checkbox to include internet search results.

5. Explore the informative responses provided by Polymath AI, including AI-generated summaries and additional LLm responses when factual consistency score is below the threshold.

## Feedback

If you have any feedback, suggestions, or issues regarding Polymath AI, please don't hesitate to [contact us](mailto:mohammad.agwan@somaiya.edu). Your input is valuable to us as we strive to improve and evolve our product.


Polymath AI - Your Ultimate Guide in the Dynamic World of Generative AI Documentation
