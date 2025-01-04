import streamlit as st
import pandas as pd
import requests
from textblob import TextBlob
import matplotlib.pyplot as plt
import random

# MediaStack API key
API_KEY = "3c71546e61d7ab164a0e3e92ecd868bf "

def fetch_articles(query, num_results=10):
    """Fetch articles using MediaStack API."""
    url = f"https://api.mediastack.com/v1/news?access_key={API_KEY}&countries=in&limit=1%27"
    params = {
        "access_key": API_KEY,
        "keywords": query,
        "limit": num_results,
        "languages": "en",
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if "data" not in data or not data["data"]:
        return []
    
    return [
        {"Title": article["title"], "Description": article.get("description", ""), "URL": article["url"]}
        for article in data["data"]
    ]

def fetch_content(url):
    """Fetch the main content of an article."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text[:5000]  # Return up to 5000 characters for simplicity
    except Exception as e:
        return f"Error fetching content: {e}"

def analyze_sentiment(text):
    """Perform sentiment analysis and return polarity, subjectivity, and TextBlob object."""
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity, blob

def compute_bias_rating(polarity):
    """Compute bias rating based on sentiment polarity."""
    if polarity < -0.5:
        return 1  # Strong negative bias
    elif polarity < -0.2:
        return 2  # Moderate negative bias
    elif polarity < 0.2:
        return 3  # Neutral
    elif polarity < 0.5:
        return 4  # Moderate positive bias
    else:
        return 5  # Strong positive bias

def bias_percentage(bias_rating):
    """Convert bias rating to percentage."""
    return (bias_rating / 5) * 100

def find_bias_reason(blob):
    """Identify reasons for bias based on extreme sentiment words."""
    sentiment_words = []
    for sentence in blob.sentences:
        for word in sentence.words:
            word_sentiment = TextBlob(word).sentiment.polarity
            if abs(word_sentiment) > 0.3:  # Consider words with significant sentiment
                sentiment_words.append((word, word_sentiment))
    return sorted(sentiment_words, key=lambda x: abs(x[1]), reverse=True)

def visualize_bias_meter(bias_rating):
    """Visualize bias using a horizontal bar chart."""
    categories = ["Strong Negative Bias", "Moderate Negative Bias", "Neutral", "Moderate Positive Bias", "Strong Positive Bias"]
    fig, ax = plt.subplots(figsize=(6, 1))
    ax.barh([0], [bias_rating], color="blue", height=0.5)
    ax.set_xlim(0, 5)
    ax.set_yticks([0])
    ax.set_yticklabels(["Bias Level"])
    ax.set_xticks(range(6))
    ax.set_xticklabels(categories, rotation=45, ha="right")
    ax.set_title("Bias Meter")
    return fig

# Streamlit UI
st.title("Random Article Bias Analysis Tool (MediaStack)")
st.markdown("### Fetch a random article and analyze its bias with detailed explanations.")

query = st.text_input("Search Topic", placeholder="Type a topic, e.g., climate change")
num_results = st.number_input("Number of Results to Search", min_value=1, max_value=50, value=10)

if st.button("Fetch Random Article and Analyze"):
    if not API_KEY:
        st.error("Please set your MediaStack API key in the code.")
    elif not query.strip():
        st.error("Search topic cannot be empty.")
    else:
        st.info("Fetching articles...")
        articles = fetch_articles(query, num_results)

        if not articles:
            st.error("No articles found for the given topic.")
        else:
            st.success("Articles fetched successfully!")
            random_article = random.choice(articles)
            title = random_article["Title"]
            description = random_article["Description"]
            url = random_article["URL"]

            st.markdown(f"### Randomly Selected Article")
            st.markdown(f"**Title**: {title}")
            st.markdown(f"**Description**: {description}")
            st.markdown(f"**URL**: [Read the Article]({url})")

            # Analyze bias
            content = fetch_content(url)
            polarity, subjectivity, blob = analyze_sentiment(content)
            bias_rating = compute_bias_rating(polarity)
            bias_percent = bias_percentage(bias_rating)

            st.markdown(f"### Bias Analysis")
            st.markdown(f"**Bias Score**: {bias_rating} ({bias_percent:.2f}%)")
            st.markdown(f"**Subjectivity**: {subjectivity:.2f} (Scale: 0 = Objective, 1 = Subjective)")

            # Display reasons for bias
            st.markdown("#### Reasons for Bias")
            bias_reasons = find_bias_reason(blob)
            if bias_reasons:
                st.markdown("The following words/phrases contributed significantly to the bias score:")
                for word, sentiment in bias_reasons[:10]:  # Display top 10 bias words
                    sentiment_type = "Positive" if sentiment > 0 else "Negative"
                    st.write(f"- **{word}**: {sentiment_type} Sentiment ({sentiment:.2f})")
            else:
                st.write("No significant sentiment words found.")

            # Display bias meter visualization
            fig = visualize_bias_meter(bias_rating)
            st.pyplot(fig)
