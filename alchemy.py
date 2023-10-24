# This API is working for searching one postcode and it is workine fine !!
# and also showing 404 error message template
#     By pabitra Jana

from flask import Flask, request, jsonify
from flask import render_template
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Create a SQLAlchemy engine
db_name = os.getenv('DBNAME')
db_user = os.getenv('USER')
db_password = os.getenv('PASSWORD')
db_host = os.getenv('HOST')

engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}")

# Create a session
Session = sessionmaker(bind=engine)

@app.route('/', methods=['GET'])
def display_form():
    # If it's a GET request, display the form
    return '''
    <form method="post">
        <label for="postcode">Enter postcode:</label>
        <input type="text" id="postcode" name="postcode" required>
        <input type="submit" value="Submit">
    </form>
    '''

@app.route('/', methods=['POST'])
def scrape():
    try:
        # Get the postcode from the user input
        postcode = request.form.get('postcode')

        # Check if the postcode is a number having 4-digits
        if not postcode.isdigit() or len(postcode) != 4:
            raise ValueError("Invalid postcode. Please enter a 4-digit numeric value.")

        # Create a session
        session = Session()

        # Use SQLAlchemy to execute the query
        query = text("""
        SELECT *
        FROM postcodeDB
        WHERE postcode = :postcode
        """)

        result = session.execute(query, {"postcode": postcode})

        table_list = []
        for row in result:
            keys = ['Postcode', 'Locality', 'State']
            values = row
            table_dict = dict(zip(keys, values))
            table_list.append(table_dict)

        session.close()

        if not table_list:
            return render_template('404.html', message='Postcode not found'), 404

        # Return the JSON response
        return jsonify(table_list)

    except (ValueError, KeyError, TypeError) as e:
        # Handle specific exceptions
        error_message = str(e)
        return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    app.run()
