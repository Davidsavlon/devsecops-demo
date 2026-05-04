from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>DevSecOps Demo App</h1><p>Running for DAST scanning</p>'

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'version': '1.0'})

@app.route('/search')
def search():
    query = request.args.get('q', '')
    return f'<p>Search results for: {query}</p>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return jsonify({'message': 'Login endpoint'})
    return '''
        <form method="POST">
            <input type="text" name="username" placeholder="Username">
            <input type="password" name="password" placeholder="Password">
            <button type="submit">Login</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, debug=False)
