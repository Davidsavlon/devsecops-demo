from flask import Flask, request, jsonify, escape
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-secret')


@app.after_request
def set_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response


@app.route('/')
def home():
    return '<h1>DevSecOps Demo App</h1><p>Running for DAST scanning</p>'


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'version': '1.0'})


@app.route('/search')
def search():
    query = request.args.get('q', '')
    safe_query = escape(query)
    return f'<p>Search results for: {safe_query}</p>'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = escape(request.form.get('username', ''))
        return jsonify({'message': 'Login endpoint', 'user': username})
    return '''
        <form method="POST">
            <input type="text" name="username" placeholder="Username">
            <input type="password" name="password" placeholder="Password">
            <button type="submit">Login</button>
        </form>
    '''


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8090, debug=False)
