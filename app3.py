
import streamlit as st
import requests
from textblob import TextBlob
from serpapi import GoogleSearch
import matplotlib.pyplot as plt
import nltk
nltk.download('brown')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')


# SerpAPI API key
SERPAPI_KEY = "5a098566bfea0cfd20b0629f677b8d7fee5b6ec6a7911f991ef1c436b271e3ef"  # Replace with your actual API key

def fetch_articles(query, num_results=10):
    """Fetch article URLs using SerpAPI."""
    params = {
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": SERPAPI_KEY,
    }
    search = GoogleSearch(params)
    results = search.get_json()
    articles = []
    
    if "organic_results" in results:
        for result in results["organic_results"]:
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            articles.append({"Title": title, "Link": link, "Snippet": snippet})
    
    return articles

def fetch_content(url):
    """Fetch the main content of an article."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text  # Return the full content for further processing
    except Exception as e:
        return f"Error fetching content: {e}"

def analyze_sentiment(text):
    """Perform sentiment analysis and return polarity and subjectivity."""
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

def generate_bias_gauge(bias_percentage):
    """Generate a gauge chart for the bias percentage."""
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw={'projection': 'polar'})
    ax.set_theta_offset(3.14159)  # Adjust the start position
    ax.set_theta_direction(-1)
    
    # Gauge sectors
    ax.barh(0, 3.14159 * 2, color='lightgray', alpha=0.3, height=2, left=0)
    ax.barh(0, (3.14159 * 2 * bias_percentage / 100), color='blue', height=2, left=0)
    ax.set_axis_off()

    return fig

def find_bias_reason(blob):
    """Identify reasons for bias based on extreme sentiment words."""
    bias_words = []
    for word, pos in blob.tags:
        # Check if the word has a significant sentiment
        word_blob = TextBlob(word)
        if abs(word_blob.sentiment.polarity) > 0.5:  # Threshold for bias
            bias_words.append(word)
    return bias_words

# Streamlit App
st.title("Article Sentiment and Bias Analyzer")

query = st.text_input("Enter a search query:")
if st.button("Fetch Articles"):
    articles = fetch_articles(query)
    if articles:
        for article in articles:
            st.write(f"**Title:** {article['Title']}")
            st.write(f"[Read more]({article['Link']})")
            st.write(f"**Snippet:** {article['Snippet']}")
            st.write("---")
    else:
        st.write("No articles found.")

url = st.text_input("Enter the URL of an article to analyze:")
if st.button("Analyze Article"):
    content = fetch_content(url)
    if content.startswith("Error"):
        st.write(content)
    else:
        polarity, subjectivity, blob = analyze_sentiment(content)
        bias_rating = compute_bias_rating(polarity)
        bias_pct = bias_percentage(bias_rating)
        bias_gauge = generate_bias_gauge(bias_pct)
        
        # Display results
        st.write("### Sentiment Analysis Results:")
        st.write(f"**Polarity:** {polarity:.2f}")
        st.write(f"**Subjectivity:** {subjectivity:.2f}")
        st.write(f"**Bias Rating:** {bias_rating}/5")
        st.write(f"**Bias Percentage:** {bias_pct:.2f}%")
        
        # Display the bias gauge
        st .pyplot(bias_gauge)
        
        # Find and display bias reasons
        bias_words = find_bias_reason(blob)
        if bias_words:
            st.write("### Words Indicating Bias:")
            st.write(", ".join(bias_words))
        else:
            st.write("No significant bias words found.")