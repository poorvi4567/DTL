# Required Libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import numpy as np
import io

# Custom CSS with Sidebar Text in Black and New Color Scheme
custom_css = """
<style>
    body {
        font-family: 'Arial', sans-serif;
        background: linear-gradient(to bottom right, #e8eaf6, #e0f7fa);
    }
    h1, h2, h3 {
        text-align: center;
        color: #4a148c;
        font-size: 28px;
    }
    .stSidebar {
        background: linear-gradient(to bottom, #80cbc4, #ffd54f);
        border-right: 5px solid #4a148c;
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar p {
        color: black; /* Sidebar text is black */
    }
    .stButton button {
        background-color: #ffd54f;
        color: #4a148c;
        border: 2px solid #ffab40;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        transition: 0.3s ease-in-out;
    }
    .stButton button:hover {
        background-color: #ffab40;
        border-color: #ff6f00;
    }
    .dataframe {
        border: 2px solid #4a148c;
        border-radius: 8px;
        margin: auto;
    }
    .result-card {
        background: #f3e5f5;
        padding: 20px;
        border: 2px solid #4a148c;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .result-card h4 {
        color: #4a148c;
        font-weight: bold;
    }
</style>
"""

# Inject Custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Define functions
def get_article_content(url):
    """
    Fetch and extract the main content of an article from a given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        article_content = []
        for tag in ['p', 'article', 'div']:
            elements = soup.find_all(tag)
            for element in elements:
                text = element.get_text(strip=True)
                if text:
                    article_content.append(text)
        return ' '.join(article_content)
    except Exception as e:
        return f"Error fetching content: {e}"

def analyze_sentiment(article_text):
    """
    Perform sentiment analysis using TextBlob.
    Returns polarity and subjectivity.
    """
    blob = TextBlob(article_text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

def calculate_bias(polarity):
    """
    Calculate bias based on sentiment polarity, scaled to 1-5.
    """
    # Scale polarity (-1 to 1) to bias score (1 to 5)
    bias_score = int((polarity + 1) * 2) + 1
    return min(max(bias_score, 1), 5)  # Ensure bias is between 1 and 5

def plot_bias_meter(bias_score):
    """
    Create a bias meter visualization.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')

    # New Color Scheme for Bias Meter
    colors = ['#4a148c', '#7b1fa2', '#ba68c8', '#ffd54f', '#ffb300']
    labels = ['Far Left', 'Left', 'Neutral', 'Right', 'Far Right']
    for i, color in enumerate(colors):
        start_angle = -90 + i * 36
        end_angle = start_angle + 36
        ax.add_patch(Wedge((0, 0), 1, start_angle, end_angle, facecolor=color, edgecolor='black'))

    needle_angle = -90 + (bias_score - 1) * 36 + 18
    x_needle = 0.9 * np.cos(np.radians(needle_angle))
    y_needle = 0.9 * np.sin(np.radians(needle_angle))
    ax.plot([0, x_needle], [0, y_needle], color='black', lw=3)

    ax.axis('off')
    plt.title("Bias Meter", fontsize=14)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return buf

# Streamlit App
st.title("🔮 News Article Sentiment & Bias Analyzer")

# Sidebar with Updated Black Text
st.sidebar.title("✨ About the Bias Meter")
st.sidebar.markdown(
    """
    <p style="color: black;">
    The **Bias Meter** categorizes articles into five levels based on sentiment polarity:
    </p>
    <ul style="color: black;">
      <li>💜 <b>Far Left (Purple)</b></li>
      <li>💙 <b>Left (Deep Violet)</b></li>
      <li>💛 <b>Neutral (Gold)</b></li>
      <li>🟢 <b>Right (Yellow-Green)</b></li>
      <li>🟡 <b>Far Right (Bright Gold)</b></li>
    </ul>
    <p style="color: black;">
    **Polarity:** Measures sentiment from -1 (negative) to 1 (positive).<br>
    **Subjectivity:** Ranges from 0 (objective) to 1 (subjective).
    </p>
    """,
    unsafe_allow_html=True,
)

# File uploader
uploaded_file = st.file_uploader("📂 Upload an Excel file", type=["xlsx"])

if uploaded_file:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)
    st.write("📊 Uploaded Data:")
    st.dataframe(df.head())

    if st.button("Analyze Articles"):
        for idx, row in df.iterrows():
            url = row['Link']  # Adjust column name
            title = row.get('Title', 'No Title')
            publisher = row.get('publisher', 'Unknown Publisher')

            st.markdown(f"<div class='result-card'><h4>🔗 {title} ({publisher})</h4>", unsafe_allow_html=True)
            content = get_article_content(url)
            if "Error" not in content:
                polarity, subjectivity = analyze_sentiment(content)
                bias_score = calculate_bias(polarity)

                st.write(f"Polarity: {polarity:.2f} | Subjectivity: {subjectivity:.2f} | Bias Score: {bias_score}")
                bias_image = plot_bias_meter(bias_score)
                st.image(bias_image, caption=f"Bias Score: {bias_score}")
            else:
                st.write("❌ Could not fetch content.")
            st.markdown("</div>", unsafe_allow_html=True)
