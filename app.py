from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Determine the base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Configure the database
# Use an environment variable for the URI, with a fallback for local development
db_uri = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'flames_results.db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model (no changes needed here)
class FlamesResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name1 = db.Column(db.String(80), nullable=False)
    name2 = db.Column(db.String(80), nullable=False)
    result = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f'<FlamesResult {self.result}>'

# FLAMES Calculation Logic (no changes needed here)
def calculate_flames(name1, name2):
    name1 = name1.lower().replace(" ", "")
    name2 = name2.lower().replace(" ", "")

    list1 = list(name1)
    list2 = list(name2)

    for char1 in list(list1):
        if char1 in list2:
            list1.remove(char1)
            list2.remove(char1)
    
    count = len(list1) + len(list2)
    flames = ['Friends', 'Lovers', 'Affection', 'Marriage', 'Enemies', 'Siblings']
    
    while len(flames) > 1:
        split_index = (count % len(flames) - 1)
        if split_index >= 0:
            right = flames[split_index + 1:]
            left = flames[:split_index]
            flames = right + left
        else:
            flames = flames[:len(flames) - 1]
    
    return flames[0]

# Route for the home page (displays the form)
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the FLAMES calculation
@app.route('/flames', methods=['POST'])
def play_flames():
    name1 = request.form['name1']
    name2 = request.form['name2']

    if not name1 or not name2:
        return "Please enter both names.", 400

    result = calculate_flames(name1, name2)

    new_entry = FlamesResult(name1=name1, name2=name2, result=result)
    db.session.add(new_entry)
    db.session.commit()

    return render_template('index.html', result=result, name1=name1, name2=name2)

# New route to view the database content
@app.route('/indraprasth')
def show_history():
    all_results = FlamesResult.query.order_by(FlamesResult.id.desc()).all()
    return render_template('history.html', results=all_results)

# Create the database and start the server
if __name__ == '__main__':
    # Ensure the 'instance' folder exists
    if not os.path.exists(os.path.join(BASE_DIR, 'instance')):
        os.makedirs(os.path.join(BASE_DIR, 'instance'))
    
    with app.app_context():
        db.create_all()
    
    # Run the development server
    app.run(debug=True)