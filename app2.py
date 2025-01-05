import streamlit as st
import pandas as pd
import requests
from textblob import TextBlob
from serpapi import GoogleSearch
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns

# SerpAPI API key
SERPAPI_KEY = "5a098566bfea0cfd20b0629f677b8d7fee5b6ec6a7911f991ef1c436b271e3ef"

def fetch_articles(query, num_results=10):
    """Fetch article URLs using SerpAPI."""
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
    """Fetch the main content of an article."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text[:5000]  # Return up to 5000 characters for simplicity
    except Exception as e:
        return f"Error fetching content: {e}"

def analyze_sentiment(text):
    """Perform sentiment analysis and return polarity and subjectivity."""
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

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

def bias_reasoning(polarity):
    """Provide detailed reasoning for the bias rating."""
    if polarity < -0.5:
        return "The article uses strongly negative language, focusing on critical perspectives."
    elif polarity < -0.2:
        return "The article leans negative, highlighting issues or challenges with a moderate tone."
    elif polarity < 0.2:
        return "The article maintains a neutral perspective, presenting a balanced view."
    elif polarity < 0.5:
        return "The article adopts a moderately positive tone, emphasizing strengths or opportunities."
    else:
        return "The article is strongly positive, often highlighting favorable aspects."

def download_as_excel(dataframe):
    """Prepare dataframe for download as Excel."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Articles')
    processed_data = output.getvalue()
    return processed_data

# Streamlit UI with custom CSS
st.set_page_config(layout="wide", page_title="Interactive Article Analysis")
st.markdown("""
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f4f4f4;
        color: #333;
        font-size: 18px;
    }
    h1 {
        font-size: 4rem;
        color: #d9534f;
    }
    h2 {
        font-size: 2.5rem;
        color: #d9534f;
    }
    h3 {
        font-size: 2rem;
        color: #d9534f;
    }
    .stTextInput>div>div>input {
        font-size: 1.5rem;
    }
    .stButton>button {
        font-size: 1.5rem;
        padding: 12px 30px;
        background-color: #d9534f;
        color: white;
        border-radius: 10px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #c9302c;
    }
    .stMarkdown {
        font-size: 1.2rem;
    }
    footer {
        font-size: 1.2rem;
        background-color: #333; /* Dark background for footer */
        color: white;
        padding: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Main content
st.title("Google Search with Bias Detector Tool 🎯")
st.markdown("### Explore diverse perspectives with real-time sentiment analysis and alternative opinions. 🔍")

query = st.text_input("Search Topic", placeholder="Type a topic, e.g., climate change 🌍")
num_results = st.number_input("Number of Results", min_value=1, max_value=50, value=10)

if st.button("Search and Analyze 🕵️‍♂️"):
    if not SERPAPI_KEY:
        st.error("❗ Please set your SerpAPI key in the code.")
    elif not query.strip():
        st.error("❗ Search topic cannot be empty.")
    else:
        st.info("Fetching articles... ⏳")
        articles_df = fetch_articles(query, num_results)

        if articles_df.empty:
            st.error("No articles found for the given topic. 😞")
        else:
            st.success(f"Successfully fetched articles. 🎉")
            st.info("Performing sentiment analysis... 🔬")
            articles_df["Content"] = articles_df["Link"].apply(fetch_content)
            articles_df["Polarity"], articles_df["Subjectivity"] = zip(
                *articles_df["Content"].apply(lambda x: analyze_sentiment(x))
            )
            articles_df["Bias Rating"] = articles_df["Polarity"].apply(compute_bias_rating)
            articles_df["Bias Reasoning"] = articles_df["Polarity"].apply(bias_reasoning)
            
            st.write("Analysis complete. Here are the results:")

            for _, row in articles_df.iterrows():
                with st.container():
                    st.subheader(row["Title"])
                    st.markdown(f"**Link:** [Read Article]({row['Link']}) 🔗")
                    st.markdown(f"**Snippet:** {row['Snippet']} 📝")
                    st.markdown(f"**Polarity:** {row['Polarity']:.2f} | **Subjectivity:** {row['Subjectivity']:.2f}")
                    st.markdown(f"**Bias Reasoning:** {row['Bias Reasoning']}")

                    # Fetch alternate opinion based on opposite polarity
                    if row["Polarity"] > 0:  # Positive polarity
                        alternate = articles_df.loc[articles_df["Polarity"] < 0]
                    elif row["Polarity"] < 0:  # Negative polarity
                        alternate = articles_df.loc[articles_df["Polarity"] > 0]
                    else:  # Neutral polarity
                        alternate = articles_df.loc[articles_df["Polarity"].abs() == articles_df["Polarity"].abs().max()]

                    if not alternate.empty:
                        alt_article = alternate.iloc[0]
                        st.markdown(f"**Alternate Opinion:** [{alt_article['Title']}]({alt_article['Link']}) 📰")
                    else:
                        st.markdown("**Alternate Opinion:** No opposite opinion found. 😞")

            st.download_button(
                label="Download Results as Excel 📊",
                data=download_as_excel(articles_df),
                file_name="articles_analysis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            # Visualization
            st.markdown("### Sentiment Analysis Visualization 📊")
            plt.figure(figsize=(12, 6))
            sns.barplot(x=articles_df.index, y=articles_df["Polarity"], palette="coolwarm")
            plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
            plt.title("Polarity of Articles", fontsize=16)
            plt.xlabel("Article Index", fontsize=12)
            plt.ylabel("Polarity", fontsize=12)
            st.pyplot(plt)

# Footer
st.markdown("<footer>Powered by NewsLens 🚀</footer>", unsafe_allow_html=True)
