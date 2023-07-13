from flask import Flask, jsonify, request
import requests
import openai
import os
from dotenv import load_dotenv


load_dotenv()

# API Token for News API
api_token = os.getenv('NEWSDATA_IO_API_TOKEN')

# Openai API setup
openai.api_type = "azure"
openai.api_base = "https://dbhackathonai9-openai.openai.azure.com/"
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_version = "2023-03-15-preview"


app = Flask(__name__)


def call_api(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print('Error occurred while fetching data')
        return None


# Function to ping the API to get news feed
def fetch_financial_data(keywords, from_date, to_date):
    newsData = []
    url = f"https://newsdata.io/api/1/news?apikey={api_token}&from_date={from_date}&to_date={to_date}&language=en&q="
    url_dup = url
    for keyword in keywords:
        url += keyword
        data = call_api(url)
        if data:
            newsData.append(data)
        url = url_dup

    articlesContent = []
    for news in newsData:
        contents = news['results']
        for cont in contents:
            articlesContent.append(cont['content'])

    return articlesContent


# Endpoint for fetching data from keywords
@app.route('/fetchDataFromKeywords', methods=['POST'])
def fetch_data_from_keywords():
    data = request.get_json()
    keywords = data.get('keywords')
    from_date = data.get('from_date')
    to_date = data.get('to_date')
    fetchedNewsArticles = fetch_financial_data(keywords, from_date, to_date)
    return jsonify(fetchedNewsArticles)


# Endpoint for fetching summary from keywords
@app.route('/summaryFromKeywords', methods=['POST'])
def fetch_summary_from_keywords():
    openai.api_version = "2023-03-15-preview"
    data = request.get_json()
    keywords = data.get('keywords')
    from_date = data.get('from_date')
    to_date = data.get('to_date')
    fetchedNewsArticles = fetch_financial_data(keywords, from_date, to_date)
    finalResult = ""
    for fetchedNewsArticle in fetchedNewsArticles:
        response = openai.ChatCompletion.create(
            engine="gpt-35-turbo",
            messages=[{"role": "system", "content": "You are an AI assistant that helps people find information."},
                      {"role": "user",
                       "content": f"Summarize the article: '{fetchedNewsArticle}'"}],
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None)
        finalResult += response.choices[0].message.content.strip() + "\n\n"
    return {"summary": finalResult}


# Endpoint for getting a summary for an article
@app.route('/getSummaryForArticle', methods=['POST'])
def get_summary_for_article():
    data = request.get_json()
    article_text = data.get('text')
    openai.api_version = "2023-03-15-preview"
    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages=[{"role": "system", "content": "You are an AI assistant that helps people find information."},
                  {"role": "user",
                   "content": f"Summarize the article: '{article_text}'"}],
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    return {"summary": response.choices[0].message.content.strip()}


# Endpoint for paraphrasing text
@app.route('/paraphraseText', methods=['POST'])
def paraphrase_text():
    data = request.get_json()
    text = data.get('text')
    openai.api_version = "2023-03-15-preview"
    if "tone" in data:
        content = f"Paraphrase the following text and generate 5 versions of the same. Give this list as an answer, nothing else: '{text}'"
    else:
        tone = data.get('tone')
        content = f"Paraphrase the following text in a {tone} and generate 5 versions of the same. Give this list as an answer, nothing else: '{text}'"
    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages=[{"role": "system", "content": "You are an AI assistant that helps people find information."},
                  {"role": "user",
                   "content": content}],
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    responseList = response.choices[0].message.content.strip().split('\n')
    return {"paraphrases": responseList}


# Endpoint for analysing text tone
@app.route('/analyseTone', methods=['POST'])
def analyse_tone():
    data = request.get_json()
    text = data.get('text')
    openai.api_version = "2023-03-15-preview"
    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages=[{"role": "system", "content": "You are an AI assistant that helps people find information."},
                  {"role": "user",
                   "content": f"Classify the tone of the text into one of the following sentiment - Formal,Informal,"
                              f"Optimistic,Worried,Friendly,Curious,Assertive,Encouraging,Romantic,Harsh,"
                              f"Abusive. Give answer in one word:: {text}"}
                  ],
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)

    return {"tone": response.choices[0].message.content.strip()}


# Endpoint for correcting grammar and spelling
@app.route('/correctGrammarAndSpellings', methods=['POST'])
def correct_grammar_and_spellings():
    data = request.get_json()
    text = data.get('text')
    openai.api_version = "2023-03-15-preview"
    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages=[{"role": "system", "content": "You are an AI assistant that helps people find information."},
                  {"role": "user",
                   "content": f"Correct the grammar, spellings and punctuation in the statement. Only give the corrected text, nothing else: '{text}'"}
                  ],
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    return {"corrected": response.choices[0].message.content.strip()}


# Endpoint for giving synonyms of the word
@app.route('/giveSynonyms', methods=['POST'])
def give_synonyms():
    data = request.get_json()
    text = data.get('text')
    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages=[{"role": "system", "content": "You are an AI assistant that helps people find information."},
                  {"role": "user", "content": f"Give 5 synonyms of the word. Give this numbered list as an answer, nothing else: '{text}'"}
                  ],
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    responseList = response.choices[0].message.content.strip().split('\n')
    return {"synonyms": responseList}


if __name__ == '__main__':
    app.run(debug=True)
