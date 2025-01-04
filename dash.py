import streamlit as st
import pandas as pd
import requests
from textblob import TextBlob
from serpapi import GoogleSearch
import plotly.express as px

# SerpAPI API key
SERPAPI_KEY = "5a098566bfea0cfd20b0629f677b8d7fee5b6ec6a7911f991ef1c436b271e3ef"

# Custom CSS
st.markdown(
    """
    <style>
    body {
        background-color: #FF6347;
        color: #fff;
        font-family: 'Georgia', serif;
        font-size: 50px;
    }
    .stButton button {
        background-color: #B22222;
        color: #fff;
        border: none;
        padding: 15px 25px;
        font-size: 20px;
        border-radius: 5px;
        cursor: pointer;
        font-family: 'Verdana', sans-serif;
    }
    .stButton button:hover {
        background-color: #8B0000;
    }
    .positive {
        background-color: #FFFAF0;
        color: #228B22;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #228B22;
        font-size: 18px;
    }
    .negative {
        background-color: #FFF0F5;
        color: #B22222;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #B22222;
        font-size: 18px;
    }
    .title {
        color: #FFD700;
        text-align: center;
        font-size: 32px;
        font-weight: bold;
    }
    .slider-label {
        font-size: 50px;
        color: #FFE4E1;
    }
    .text-input {
        font-size: 100px;
        padding: 10px;
        border: 2px solid #fff;
        border-radius: 5px;
        background-color: #FFA07A;
        color: #fff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def fetch_articles(query, num_results=10):
    params = {
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": SERPAPI_KEY,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    articles = []
    if "organic_results" in results:
        for result in results["organic_results"]:
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            articles.append({"Title": title, "Link": link, "Snippet": snippet})
    return pd.DataFrame(articles)

def fetch_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text[:5000]
    except Exception as e:
        return f"Error fetching content: {e}"

def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

def compute_bias_rating(polarity):
    if polarity < -0.5:
        return 1
    elif polarity < -0.2:
        return 2
    elif polarity < 0.2:
        return 3
    elif polarity < 0.5:
        return 4
    else:
        return 5

def bias_reasoning(polarity, content):
    return f"Bias reasoning based on content sentiment polarity {polarity:.2f}."

# Streamlit app setup
st.markdown("<div class='title'>Interactive Article Analysis</div>", unsafe_allow_html=True)

search_query = st.text_input("Enter a search query:", key="search_input")
st.markdown("<div class='slider-label'>Number of Results:</div>", unsafe_allow_html=True)
num_results = st.slider("", min_value=1, max_value=50, value=10, step=1)

if st.button("Search and Analyze") and search_query:
    articles_df = fetch_articles(search_query, num_results)
    articles_df["Content"] = articles_df["Link"].apply(fetch_content)
    articles_df["Polarity"], articles_df["Subjectivity"] = zip(*articles_df["Content"].apply(lambda x: analyze_sentiment(x)))
    articles_df["Bias Rating"] = articles_df["Polarity"].apply(compute_bias_rating)
    articles_df["Bias Reasoning"] = articles_df.apply(lambda row: bias_reasoning(row["Polarity"], row["Content"]), axis=1)

    st.markdown("<div class='title'>Analysis Results</div>", unsafe_allow_html=True)

    # Display articles in a table
    st.dataframe(articles_df["Title": "Bias Reasoning"])

    # Create a bar chart using Plotly
    fig = px.bar(
        articles_df,
        x="Title",
        y="Polarity",
        color="Polarity",
        title="Article Sentiment",
        labels={"Title": "Article", "Polarity": "Sentiment Polarity"}
    )
    st.plotly_chart(fig)

    # Display most positive article
    if st.button("Show Most Positive Article"):
        most_positive = articles_df.loc[articles_df["Polarity"].idxmax()]
        st.markdown(f"<div class='positive'><strong>Most Positive Article:</strong><br><a href='{most_positive['Link']}' target='_blank'>{most_positive['Title']}</a></div>", unsafe_allow_html=True)

    # Display most negative article
    if st.button("Show Most Negative Article"):
        most_negative = articles_df.loc[articles_df["Polarity"].idxmin()]
        st.markdown(f"<div class='negative'><strong>Most Negative Article:</strong><br><a href='{most_negative['Link']}' target='_blank'>{most_negative['Title']}</a></div>", unsafe_allow_html=True)
