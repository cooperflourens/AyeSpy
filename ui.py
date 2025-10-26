from flask import Flask, render_template_string, request
import pandas as pd
import os

app = Flask(__name__)


# HTML template as a multi-line string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AyeSpy - Congressional Transparency</title>
    <style>
        .header {
            text-align: center;
        }
        .header img {
            border-radius: 50%;
            width: 4%;
            padding: 20px;
            vertical-align: middle;
            display: inline-block;
        }
        .header h1 {
            position: relative;
            left: 10px;
            vertical-align: middle;
            display: inline-block;         
        }
        h1 {
            text-align: center;
        }
        h3 {
            text-align: center;
        }
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-image: url({{ url_for('static', filename='capitolbuilding.jpg') }});
            background-size: cover;
            background-color: black;
        }
        .overlay {
            background-color: rgba(0, 0, 0, 0.7);
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            position: relative;
            z-index: 1;
        }
        form {
            width: 85%;
            float: right;
        }
        .container {
            margin: 0px 10px 20px 10px;
            width: 25%;
            float: left;
        }
        .range-container {
            margin: 0px 10px 20px 10px;
            width 20%;
            float: left;
        }
        .button-container {
            width: 10%;
            float: left;
        }
        input[type="text"], input[type="search"], input[type="date"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            display: inline-block;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
            float: left;
        }
        button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            padding: 13px;
            margin: 8px 10px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        select {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            display: inline-block;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .results {
            clear: both;
            margin-top: 30px;
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            margin-left: 20px;
            margin-right: 20px;
        }
        .result-item {
            margin-bottom: 15px;
            padding: 15px;
            border-left: 4px solid #4CAF50;
            background-color: white;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .result-item:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .result-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
            font-size: 16px;
        }
        .result-snippet {
            color: #666;
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 8px;
        }
        .result-meta {
            font-size: 12px;
            color: #888;
            font-style: italic;
        }
        .quote-expanded {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
            margin-top: 10px;
            display: none;
        }
        .quote-highlight {
            background-color: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: bold;
        }
        .quote-full {
            font-size: 15px;
            line-height: 1.6;
            color: #333;
            margin-bottom: 10px;
            white-space: pre-wrap;
        }
        .quote-context {
            font-size: 13px;
            color: #666;
            font-style: italic;
            border-top: 1px solid #dee2e6;
            padding-top: 10px;
        }
        .click-hint {
            font-size: 11px;
            color: #999;
            text-align: right;
            margin-top: 5px;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
        }
        .modal-content {
            background-color: white;
            margin: 2% auto;
            padding: 20px;
            border-radius: 8px;
            width: 90%;
            height: 90%;
            overflow-y: auto;
            position: relative;
        }
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            position: absolute;
            top: 10px;
            right: 20px;
        }
        .close:hover {
            color: black;
        }
        .hearing-transcript {
            margin-top: 40px;
        }
        .transcript-stats {
            background-color: #e3f2fd;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
            font-size: 14px;
        }
        .transcript-content {
            max-height: 80vh;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 15px;
            background-color: #f9f9f9;
        }
        .transcript-quote {
            margin-bottom: 20px;
            padding: 10px;
            border-left: 3px solid #4CAF50;
            background-color: white;
            border-radius: 4px;
        }
        .speaker-name {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
            font-size: 14px;
        }
        .quote-text {
            color: #555;
            line-height: 1.5;
            margin-bottom: 5px;
        }
        .quote-date {
            font-size: 11px;
            color: #888;
            font-style: italic;
        }
        .view-full-hearing {
            background-color: #2196F3;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            margin-top: 5px;
            display: inline-block;
        }
        .view-full-hearing:hover {
            background-color: #1976D2;
        }
        .search-info {
            color: #666;
            font-style: italic;
            margin-bottom: 15px;
        }
        .no-results {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="overlay"></div>
    <div class="header"> 
        <h1><img src="{{url_for('static', filename='logo.png')}}", alt="logo"/>AyeSpy</h1>
    </div>
    <h3>Discover what your politicians really think, in their own words.</h3>
    <div id="form">
        <form action="" method="post">
            <div class="container">
                <input type="search" id="search" name="search" list="search-options" placeholder="Politician Name" value="{{ search_term or '' }}">
                <datalist id="search-options">
                    {% for option in options %}
                    <option value="{{ option }}">
                    {% endfor %}
                </datalist>
            </div>
            <div class="container">
                <input type="text" id="textfield" name="textfield" placeholder="Issue of interest" value="{{ issue_term or '' }}">
            </div>
            <div class="range-container">
                <select id="timerange" name="timerange">
                    <option value="" disabled {% if not time_range %}selected{% endif %}>Time Range</option>
                    <option value="hours" {% if time_range == 'hours' %}selected{% endif %}>Past 24 hours</option>
                    <option value="weeks" {% if time_range == 'weeks' %}selected{% endif %}>Past week</option>
                    <option value="months" {% if time_range == 'months' %}selected{% endif %}>Past month</option>
                    <option value="years" {% if time_range == 'years' %}selected{% endif %}>Past year</option>
                    <option value="forever" {% if time_range == 'forever' %}selected{% endif %}>All time</option>
                </select>
            </div>
            <div class="button-container">
                <button type="submit">Submit</button>
            </div>
        </form>
    </div>
    
    {% if search_results %}
    <div class="results">
        <div class="search-info">
            {% if search_term or issue_term %}
                Search results for: 
                {% if search_term %}"{{ search_term }}"{% endif %}
                {% if search_term and issue_term %} and {% endif %}
                {% if issue_term %}"{{ issue_term }}"{% endif %}
                {% if time_range %} ({{ time_range }}){% endif %}
            {% endif %}
        </div>
        
        {% if search_results|length > 0 %}
            {% for result in search_results %}
            <div class="result-item" onclick="toggleQuote({{ loop.index0 }})">
                <div class="result-title">{{ result.title }}</div>
                <div class="result-snippet">{{ result.snippet | safe }}</div>
                <div class="result-meta">{{ result.date }} | {{ result.committee }}</div>
                <div class="click-hint">Click to view full quote and context</div>
                
                <div class="quote-expanded" id="quote-{{ loop.index0 }}">
                    <div class="quote-full">{{ result.full_quote | safe }}</div>
                    <div class="quote-context">
                        <strong>Document:</strong> {{ result.committee }}<br>
                        <strong>Date:</strong> {{ result.date }}<br>
                        <strong>Speaker:</strong> {{ result.speaker }}
                    </div>
                    <div class="view-full-hearing" onclick="event.stopPropagation(); showFullHearing('{{ result.committee }}')">
                        View Full Hearing Transcript
                    </div>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="no-results">
                No results found. Try different search terms or check if data is loaded.
            </div>
        {% endif %}
    </div>
    {% endif %}
    
    <!-- Modal for full hearing transcript -->
    <div id="hearingModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <div id="modalContent"></div>
        </div>
    </div>
    
    <script>
        function toggleQuote(index) {
            const expanded = document.getElementById('quote-' + index);
            if (expanded.style.display === 'none' || expanded.style.display === '') {
                expanded.style.display = 'block';
            } else {
                expanded.style.display = 'none';
            }
        }
        
        function showFullHearing(documentId) {
            const modal = document.getElementById('hearingModal');
            const modalContent = document.getElementById('modalContent');
            
            // Show loading
            modalContent.innerHTML = '<div style="text-align: center; padding: 50px;">Loading full hearing transcript...</div>';
            modal.style.display = 'block';
            
            // Fetch the full hearing transcript
            fetch(`/hearing/${documentId}`)
                .then(response => response.text())
                .then(data => {
                    modalContent.innerHTML = data;
                })
                .catch(error => {
                    modalContent.innerHTML = '<div style="text-align: center; padding: 50px; color: red;">Error loading hearing transcript: ' + error + '</div>';
                });
        }
        
        function closeModal() {
            document.getElementById('hearingModal').style.display = 'none';
        }
        
        // Close modal when clicking outside of it
        window.onclick = function(event) {
            const modal = document.getElementById('hearingModal');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

def get_full_hearing_transcript(document_id):
    """
    Get the complete transcript for a hearing document
    """
    try:
        hearings_file = 'congressional_hearings_test2.csv'
        if not os.path.exists(hearings_file):
            hearings_file = 'data/congressional_hearings_test2.csv'
        
        if not os.path.exists(hearings_file):
            return []
            
        df = pd.read_csv(hearings_file)
        hearing_quotes = df[df['document'] == document_id].sort_values('date')
        
        return hearing_quotes.to_dict('records')
        
    except Exception as e:
        print(f"Error getting hearing transcript: {e}")
        return []

def highlight_search_terms(text, search_terms):
    """
    Highlight search terms in text with HTML spans
    """
    if not search_terms:
        return text
    
    highlighted_text = text
    for term in search_terms:
        if term and term.strip():
            # Case-insensitive highlighting
            import re
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted_text = pattern.sub(
                lambda m: f'<span class="quote-highlight">{m.group()}</span>',
                highlighted_text
            )
    return highlighted_text

def search_hearings(politician=None, issue=None, time_range=None):
    """
    Search function that looks through congressional hearing data.
    Now properly filters by who actually said the quotes.
    """
    try:
        # Try to load the congressional hearings data
        hearings_file = 'congressional_hearings_test2.csv'
        if not os.path.exists(hearings_file):
            hearings_file = 'data/congressional_hearings_test2.csv'
        
        if not os.path.exists(hearings_file):
            return []
            
        df = pd.read_csv(hearings_file)
        
        results = []
        
        # Simple text search (case-insensitive)
        for _, row in df.iterrows():
            document = str(row.get('document', ''))
            name = str(row.get('name', ''))
            quote = str(row.get('quote', ''))
            date = str(row.get('date', ''))
            
            match = False
            
            # Check politician name - must match the 'name' field (who actually said it)
            if politician:
                # Check if politician name appears in the speaker name field
                if politician.lower() in name.lower():
                    match = True
            
            # Check issue/topic in the quote content
            if issue and issue.lower() in quote.lower():
                match = True
            
            # If searching for both politician and issue, both must match
            if politician and issue:
                politician_match = politician.lower() in name.lower()
                issue_match = issue.lower() in quote.lower()
                match = politician_match and issue_match
            elif politician and not issue:
                # Only politician search
                match = politician.lower() in name.lower()
            elif issue and not politician:
                # Only issue search - match any quote containing the issue
                match = issue.lower() in quote.lower()
            
            if match:
                # Create a better snippet with more context
                quote_text = quote
                snippet_length = 300  # Longer snippet for better context
                
                # If searching for an issue, try to center the snippet around the keyword
                if issue and issue.lower() in quote_text.lower():
                    issue_pos = quote_text.lower().find(issue.lower())
                    start = max(0, issue_pos - snippet_length // 2)
                    end = min(len(quote_text), start + snippet_length)
                    snippet = quote_text[start:end]
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(quote_text):
                        snippet = snippet + "..."
                else:
                    snippet = quote_text[:snippet_length] + "..." if len(quote_text) > snippet_length else quote_text
                
                # Prepare search terms for highlighting
                search_terms = []
                if politician:
                    search_terms.append(politician)
                if issue:
                    search_terms.append(issue)
                
                results.append({
                    'title': f"{name} - {document}",
                    'snippet': highlight_search_terms(snippet, search_terms),
                    'full_quote': highlight_search_terms(quote_text, search_terms),
                    'speaker': name,
                    'date': date,
                    'committee': document
                })
        
        # Limit results to 10 for display
        return results[:10]
        
    except Exception as e:
        print(f"Search error: {e}")
        return []

@app.route('/hearing/<document_id>')
def show_hearing_transcript(document_id):
    """
    Show the full transcript for a hearing document
    """
    transcript = get_full_hearing_transcript(document_id)
    
    if not transcript:
        return f"Hearing {document_id} not found", 404
    
    # Get search terms from the current session for highlighting
    search_terms = []
    # We'll pass these through URL parameters or session
    
    # Create HTML for the transcript
    transcript_html = f"""
    <div class="hearing-transcript">
        <h2>Full Hearing Transcript: {document_id}</h2>
        <div class="transcript-stats">
            <strong>Total Quotes:</strong> {len(transcript)} | 
            <strong>Speakers:</strong> {len(set(q.get('name', '') for q in transcript))}
        </div>
        <div class="transcript-content">
    """
    
    for quote in transcript:
        speaker = quote.get('name', 'Unknown')
        text = quote.get('quote', '')
        date = quote.get('date', '')
        
        # Highlight search terms if any
        highlighted_text = text  # For now, no highlighting in full transcript
        
        transcript_html += f"""
            <div class="transcript-quote">
                <div class="speaker-name">{speaker}</div>
                <div class="quote-text">{highlighted_text}</div>
                <div class="quote-date">{date}</div>
            </div>
        """
    
    transcript_html += """
        </div>
    </div>
    """
    
    return transcript_html

@app.route('/', methods=['GET', 'POST'])
def homepage():
    # Define names for politician search
    try:
        df = pd.read_csv('data/legislators-current.csv')
        names = df['full_name'].to_list()
    except:
        names = ['Joe Biden', 'Nancy Pelosi', 'Mitch McConnell', 'Chuck Schumer']
    
    search_results = []
    search_term = ""
    issue_term = ""
    time_range = ""
    
    # Handle form submission
    if request.method == 'POST':
        search_term = request.form.get('search', '').strip()
        issue_term = request.form.get('textfield', '').strip()
        time_range = request.form.get('timerange', '')
        
        # Only search if we have at least one search term
        if search_term or issue_term:
            search_results = search_hearings(
                politician=search_term,
                issue=issue_term,
                time_range=time_range
            )
    
    return render_template_string(
        HTML_TEMPLATE, 
        options=names,
        search_results=search_results,
        search_term=search_term,
        issue_term=issue_term,
        time_range=time_range
    )

if __name__ == '__main__':
    app.run(debug=True)
