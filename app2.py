import streamlit as st
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import re

# Custom CSS for styling
custom_css = """
<style>
    body {
        font-family: 'Arial', sans-serif;
        color: #333;
        background-color: #f0f8ff; /* Light blue background */
        margin: 0;
        padding: 0;
    }
    .title {
        color: #2a9d8f;
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    .description {
        font-size: 1.6rem;
        line-height: 1.8;
        color: #264653;
        margin-bottom: 20px;
    }
    .result-box {
        border: 2px solid #2a9d8f;
        padding: 30px;
        border-radius: 12px;
        background-color: #e9f5f2;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    }
    .result-title {
        font-size: 2.5rem;
        color: #264653;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .emoji {
        font-size: 2.5rem;
        margin-right: 10px;
    }
    input[type="text"] {
        font-size: 1.6rem;
        padding: 15px;
        width: 70%;
        margin: 20px auto;
        border-radius: 8px;
        border: 2px solid #2a9d8f;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    button {
        font-size: 1.6rem;
        padding: 15px 30px;
        background-color: #2a9d8f;
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
    }
    button:hover {
        background-color: #264653;
    }
    footer {
        font-size: 1.4rem;
        text-align: center;
        margin-top: 40px;
        color: #264653;
    }
</style>
"""

# Function to extract article text from a URL
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs])
        return re.sub(r'\s+', ' ', text.strip())
    except Exception as e:
        return None

# Function to detect potential bias and analyze sentiment
def detect_bias_and_sentiment(article_text):
    blob = TextBlob(article_text)
    
    # Sentiment analysis
    sentiment_polarity = blob.sentiment.polarity  # Range from -1 (negative) to 1 (positive)
    sentiment_subjectivity = blob.sentiment.subjectivity  # Range from 0 (objective) to 1 (subjective)
    
    sentiment_desc = (
        "Positive 😄" if sentiment_polarity > 0 
        else "Negative 😢" if sentiment_polarity < 0 
        else "Neutral 😐"
    )
    
    # Basic bias detection
    if 'government' in article_text.lower() or 'politics' in article_text.lower():
        bias_note = "This article discusses topics that are often politically charged. ⚖️ Be mindful of potential bias."
    elif 'economy' in article_text.lower():
        bias_note = "Economic articles can reflect the author's perspective on financial policies. 💰"
    else:
        bias_note = "This article may have subjective viewpoints based on its content. 📖"

    return sentiment_desc, sentiment_polarity, sentiment_subjectivity, bias_note

# Streamlit UI
st.set_page_config(page_title="Bias Detection and Sentiment Analysis", layout="centered")
st.markdown(custom_css, unsafe_allow_html=True)

# Title with emoji
st.markdown("<div class='title'>📰 Bias Detection & Sentiment Analysis</div>", unsafe_allow_html=True)

url = st.text_input("Enter the article URL:", "", placeholder="https://example.com/news-article")

if st.button("Analyze"):
    if url:
        article_text = extract_text_from_url(url)
        if article_text:
            sentiment_desc, sentiment_polarity, sentiment_subjectivity, bias_note = detect_bias_and_sentiment(article_text)

            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.markdown(f"<div class='result-title'><span class='emoji'>🔍</span> Sentiment: {sentiment_desc}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='description'>Polarity: {sentiment_polarity:.2f}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='description'>Subjectivity: {sentiment_subjectivity:.2f}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='description'>{bias_note}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("❌ Failed to extract text from the provided URL. Please try another link.")
    else:
        st.error("⚠️ Please enter a valid URL.")

# Footer section
st.markdown("<footer>Powered by NewsLens & BiasAlias</footer>", unsafe_allow_html=True)
