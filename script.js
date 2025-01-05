function openStreamlitPage() {
    // Redirects to the Streamlit page directly when "Input Article URL" button is clicked
    window.open('https://urlcontent2py-brwdc9kxmqcyxikqvxkznc.streamlit.app/', '_blank');
}

function searchArticles() {
    // Trigger a search for articles directly when the search button is clicked
    fetch(`http://your-streamlit-url.com/search-articles`)
        .then(response => response.json())
        .then(data => {
            const articles = data.articles || [];
            displayArticles(articles);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to search articles');
        });
}

function displayArticles(articles) {
    const resultsContainer = document.getElementById("article-results");
    resultsContainer.innerHTML = '';
    
    articles.forEach(article => {
        const articleDiv = document.createElement('div');
        articleDiv.className = 'article';
        articleDiv.innerHTML = `<h3>${article.title}</h3><p>${article.summary}</p>`;
        resultsContainer.appendChild(articleDiv);
    });
}

function clearArticles() {
    document.getElementById("article-results").innerHTML = '';
}
