from flask import Flask, jsonify, request, session
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

DATABASE = 'vps_hosting.db'

# Helper functions

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    # Create VPS instances table
    cursor.execute('''CREATE TABLE IF NOT EXISTS vps_instances (id INTEGER PRIMARY KEY, user_id INTEGER, instance_name TEXT, status TEXT, FOREIGN KEY (user_id) REFERENCES users (id))''')
    conn.commit()
    conn.close()

# User Authentication
@app.route('/signup', methods=['POST'])
def signup():
    username = request.json.get('username')
    password = request.json.get('password')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return jsonify({'message': 'User created successfully.'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    if user:
        session['user_id'] = user[0]
        return jsonify({'message': 'Login successful.'}), 200
    return jsonify({'error': 'Invalid username or password.'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful.'}), 200

# VPS Instance Management
@app.route('/vps', methods=['POST'])
def create_vps():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized.'}), 401
    instance_name = request.json.get('instance_name')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO vps_instances (user_id, instance_name, status) VALUES (?, ?, ?)', (user_id, instance_name, 'active'))
        conn.commit()
        return jsonify({'message': 'VPS instance created.'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/vps/<int:vps_id>', methods=['GET'])
def get_vps(vps_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized.'}), 401
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vps_instances WHERE id = ? AND user_id = ?', (vps_id, user_id))
    vps = cursor.fetchone()
    if vps:
        return jsonify({'id': vps[0], 'instance_name': vps[2], 'status': vps[3]}), 200
    return jsonify({'error': 'VPS instance not found.'}), 404

@app.route('/vps/<int:vps_id>', methods=['PUT'])
def update_vps(vps_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized.'}), 401
    instance_name = request.json.get('instance_name')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE vps_instances SET instance_name = ? WHERE id = ? AND user_id = ?', (instance_name, vps_id, user_id))
    conn.commit()
    return jsonify({'message': 'VPS instance updated.'}), 200

@app.route('/vps/<int:vps_id>', methods=['DELETE'])
def delete_vps(vps_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized.'}), 401
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM vps_instances WHERE id = ? AND user_id = ?', (vps_id, user_id))
    conn.commit()
    return jsonify({'message': 'VPS instance deleted.'}), 200

# Initialize database
init_db()

if __name__ == '__main__':
    app.run(debug=True)