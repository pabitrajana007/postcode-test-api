# In this it is showing all the error postcodes at first !!
# And it is working properly !!


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
        <label for="postcodes">Enter postcodes (comma-separated):</label>
        <input type="text" id="postcodes" name="postcodes" required>
        <input type="submit" value="Submit">
    </form>
    '''

@app.route('/', methods=['POST'])
def scrape():
    try:
        # Get the comma-separated postcodes from the user input
        postcodes_input = request.form.get('postcodes')

        # Split the input on commas to extract individual postcodes
        postcodes = postcodes_input.split(',')

        # Create a session
        session = Session()

        table_list = []
        error_messages = []

        for postcode in postcodes:
            # Strip leading and trailing spaces from the postcode
            postcode = postcode.strip()

            # Check if the postcode is a number having 4-digits
            if not postcode.isdigit() or len(postcode) != 4:
                error_messages.append(f"Invalid postcode: {postcode}. Please enter a 4-digit numeric value.")
            else:
                # Use SQLAlchemy to execute the query
                query = text("""
                SELECT *
                FROM postcodeDB
                WHERE postcode = :postcode
                """)

                result = session.execute(query, {"postcode": postcode})

                found = False  # Flag to track if the postcode was found

                for row in result:
                    keys = ['Postcode', 'Locality', 'State']
                    values = row
                    table_dict = dict(zip(keys, values))
                    table_list.append(table_dict)
                    found = True

                if not found:
                    # Add a custom error message for postcode not found
                    error_messages.append(f"Postcode {postcode} not found in the database. 404! not found")

        session.close()

        response_data = {}

        if error_messages:
            response_data['Error'] = error_messages

        if table_list:
            response_data['Output-Response'] = table_list

        # Return the JSON response
        return jsonify(response_data)

    except (ValueError, KeyError, TypeError) as e:
        # Handle specific exceptions
        error_message = str(e)
        return jsonify({'error': error_message}), 500


if __name__ == '__main__':
    app.run()
