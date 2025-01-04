function openDialog() {
    document.getElementById("url-dialog").style.display = "flex";
}

function closeDialog() {
    document.getElementById("url-dialog").style.display = "none";
}

function submitUrl() {
    const url = document.getElementById("article-url").value;
    
    if (url) {
        // Call your Streamlit function for URL processing
        // Example API call to Streamlit app for URL processing (you need to have a backend to handle this)
        fetch(`http://your-streamlit-url.com/process-url?url=${encodeURIComponent(url)}`)
            .then(response => response.json())
            .then(data => {
                alert('Article URL processed!');
                closeDialog();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Something went wrong!');
            });
    }
}

function searchArticles() {
    const query = document.getElementById("search-bar").value;
    
    if (query) {
        // Call your Streamlit function for search processing
        // Example API call to Streamlit app for searching articles
        fetch(`http://your-streamlit-url.com/search-articles?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                const articles = data.articles || [];
                displayArticles(articles);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to search articles');
            });
    } else {
        clearArticles();
    }
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
