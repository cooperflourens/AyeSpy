from flask import Flask, render_template_string
import pandas as pd

app = Flask(__name__)


# HTML template as a multi-line string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple UI Example</title>
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
    </style>
</head>
<body>
    <div class="overlay"></div>
    <div class="header"> 
        <h1><img src="{{url_for('static', filename='logo.png')}}", alt="logo"/>Seek the Seal</h1>
    </div>
    <h3>Discover what your politicians really think, in their own words.</h3>
    <div id="form">
        <form action="" method="post">
            <div class="container">
                <input type="search" id="search" name="search" list="search-options" placeholder="Politician Name">
                <datalist id="search-options">
                    {% for option in options %}
                    <option value="{{ option }}">
                    {% endfor %}
                </datalist>
            </div>
            <div class="container">
                <input type="text" id="textfield" name="textfield" placeholder="Issue of interest">
            </div>
            <div class="range-container">
                <select id="timerange" name="timerange">
                    <option value="" disabled selected>Time Range</option>
                    <option value="hours">Past 24 hours</option>
                    <option value="weeks">Past week</option>
                    <option value="months">Past month</option>
                    <option value="years">Past year</option>
                    <option value="forever">All time</option>
                </select>
            </div>
            <div class="button-container">
                <button type="submit">Submit</button>
            </div>
        </form>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def homepage():
    # Define names for elastic search
    df = pd.read_csv('data/legislators-current.csv')
    names = df['full_name'].to_list()
    # For POST requests, you can access submitted data using request.form
    return render_template_string(HTML_TEMPLATE, options=names)

if __name__ == '__main__':
    app.run(debug=True)
