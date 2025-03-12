from flask import Flask, request, render_template, send_file, jsonify
import requests
import io

app = Flask(__name__)


API_KEY = "AIzaSyAaz3tinG6umOHG1wXoDw-izEaR7dJZUTo"
CSE_ID = "3123dff1efc344e60"

def google_search(query, search_type=None):
    """Perform a search using Google Custom Search API."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
        "num": 10
    }
    if search_type:
        params["searchType"] = search_type
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching search results: {e}")
        return {}

def get_detailed_answer(query):
    """Fetch a detailed answer using Google Custom Search API."""
    result = google_search(query)
    if "items" in result:
        return "\n".join([item.get("snippet", "No snippet available") for item in result["items"]])
    return "No answer found."

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = ""
    images = []
    if request.method == 'POST':
        user_query = request.form.get('query', '').strip()
        if user_query:
            answer = get_detailed_answer(user_query)
            image_results = google_search(user_query, search_type="image")
            images = [item.get("link", "#") for item in image_results.get("items", [])]

    return render_template('index.html', answer=answer, images=images)

@app.route('/download')
def download_image():
    url = request.args.get('url')
    quality = request.args.get('quality', 'original')
    ratio = request.args.get('ratio', '9:16')

    if not url:
        return "Invalid URL."

    try:
        response = requests.get(url)
        response.raise_for_status()
        return send_file(io.BytesIO(response.content), 
                         mimetype="image/jpeg", 
                         as_attachment=True, 
                         download_name=f'image_{quality}_{ratio}.jpg')
    except requests.RequestException as e:
        return f"Failed to download image: {e}"

@app.route('/get_download_options', methods=['GET'])
def get_download_options():
    qualities = ['4K', '1080p', '720p', '480p', '360p', '240p', '140p']
    ratios = ['9:16', '16:9', '4:3', '1:1']
    return jsonify({'qualities': qualities, 'ratios': ratios})

if __name__ == '__main__':
    app.run(debug=True)
