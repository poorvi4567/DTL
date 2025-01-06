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
    }
    .title {
        color: #2a9d8f;
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .description {
        font-size: 1.6rem;
        margin-bottom: 20px;
        line-height: 1.8;
    }
    .result-box {
        border: 2px solid #2a9d8f;
        padding: 20px;
        border-radius: 10px;
        background-color: #e9f5f2;
    }
    .result-title {
        font-size: 2rem;
        color: #264653;
        margin-bottom: 10px;
    }
    .emoji {
        font-size: 2rem;
        margin-right: 10px;
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
    
    # Bias detection based on keywords
    bias_categories = {
        "government": "This article discusses politically sensitive topics. ⚖️ Be mindful of potential bias.",
        "economy": "Economic topics often reflect the author's perspective on financial policies. 💰",
        "health": "Health articles may contain strong opinions on medical advancements or policies. 🏥",
        "medicine": "Medical content can be controversial, especially regarding treatments and vaccines. 💉",
        "climate": "Discussions on climate change may reflect ideological perspectives. 🌍",
        "environment": "Environmental policies and conservation topics can be politically charged. 🌱",
        "technology": "Tech articles might reflect concerns about AI, cybersecurity, or ethics. 🤖",
        "ai": "Artificial Intelligence is a debated topic, often associated with automation fears. 🧠",
        "social": "Social issues like race, gender, or human rights are highly debated. ⚖️",
        "education": "Educational policies and reforms can generate diverse opinions. 🎓"
    }

    detected_biases = [bias_categories[key] for key in bias_categories if key in article_text.lower()]
    
    if detected_biases:
        bias_note = " ".join(detected_biases)
    else:
        bias_note = "This article appears to be neutral or covers general topics. 📖"

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
