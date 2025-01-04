# Required Libraries
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob

def get_article_content(url):
    """
    Fetches and extracts the main content of an article from a given URL.

    Parameters:
        url (str): The URL of the article to fetch.

    Returns:
        str: The extracted article text, or an error message if the process fails.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        # Parse the webpage content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the main content (This may vary depending on the site's structure)
        article_content = []
        for tag in ['p', 'article', 'div']:
            elements = soup.find_all(tag)
            for element in elements:
                text = element.get_text(strip=True)
                if text:  # Only include non-empty text
                    article_content.append(text)

        # Join and return the article text
        return ' '.join(article_content)
    except requests.exceptions.RequestException as e:
        return f"Error fetching the article: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

def analyze_sentiment(content):
    """
    Analyzes the sentiment of the content and provides a bias rating.

    Parameters:
        content (str): The text content of the article.

    Returns:
        dict: Sentiment analysis result including polarity, subjectivity, bias rating, and explanation.
    """
    # Perform sentiment analysis using TextBlob
    blob = TextBlob(content)
    polarity = blob.sentiment.polarity  # Ranges from -1 (negative) to 1 (positive)
    subjectivity = blob.sentiment.subjectivity  # Ranges from 0 (objective) to 1 (subjective)

    # Determine bias rating
    if abs(polarity) < 0.1 and subjectivity < 0.3:
        bias_rating = 1
        explanation = "The article appears to be neutral and objective, with minimal bias."
    elif abs(polarity) < 0.3 and subjectivity < 0.5:
        bias_rating = 2
        explanation = "The article is mostly balanced but shows slight leanings in sentiment or subjectivity."
    elif abs(polarity) < 0.5:
        bias_rating = 3
        explanation = "The article exhibits a moderate bias, showing noticeable sentiment or subjective opinions."
    elif abs(polarity) < 0.7:
        bias_rating = 4
        explanation = "The article is strongly biased, with clear sentiment or subjective opinions dominating the content."
    else:
        bias_rating = 5
        explanation = "The article is highly biased, with extreme sentiment or heavily subjective content."

    return {
        "polarity": polarity,
        "subjectivity": subjectivity,
        "bias_rating": bias_rating,
        "explanation": explanation
    }

# Example Usage
if __name__ == "__main__":
    while True:
        # Input URL
        url = input("Enter the URL of the article (or type 'exit' to quit): ")
        if url.lower() == 'exit':
            break

        # Fetch the article content
        content = get_article_content(url)

        # Check if content fetching was successful
        if content.startswith("Error"):
            print(content)
        else:
            # Perform sentiment analysis
            analysis = analyze_sentiment(content)

            # Display results
            print("\nExtracted Article Content:\n")
            print(content[:500] + ("..." if len(content) > 500 else ""))  # Show a snippet of the article

            print("\nSentiment Analysis Results:\n")
            print(f"Polarity: {analysis['polarity']:.2f}")
            print(f"Subjectivity: {analysis['subjectivity']:.2f}")
            print(f"Bias Rating: {analysis['bias_rating']}/5")
            print(f"Explanation: {analysis['explanation']}")