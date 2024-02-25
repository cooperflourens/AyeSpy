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
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        .container {
            margin-bottom: 20px;
        }
        input[type="text"], input[type="search"], input[type="date"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            display: inline-block;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            padding: 14px 20px;
            margin: 8px 0;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>SEEK the SPAN</h1>
    <form action="" method="post">
        <div class="container">
            <label for="search">Representative Name:</label>
            <input type="search" id="search" name="search" list="search-options" placeholder="Type to search...">
            <datalist id="search-options">
                {% for option in options %}
                <option value="{{ option }}">
                {% endfor %}
            </datalist>
        </div>
        <div class="container">
            <label for="textfield">Topic Name:</label>
            <input type="text" id="textfield" name="textfield" placeholder="Enter some text...">
        </div>
        <div class="container">
            <label for="startdate">Start Date:</label>
            <input type="date" id="startdate" name="startdate">
            <label for="enddate">End Date:</label>
            <input type="date" id="enddate" name="enddate">
        </div>
        <button type="submit">Submit</button>
    </form>
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
