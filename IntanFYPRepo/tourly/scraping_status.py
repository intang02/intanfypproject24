from flask import Flask, jsonify

app = Flask(__name__)

# Example status variable
scraping_status = {
    "ready": False
}

@app.route('/results')
def results():
    return jsonify(scraping_status)

if __name__ == '__main__':
    app.run(debug=True)
