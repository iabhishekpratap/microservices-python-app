import jwt
import datetime
import os
import psycopg2
import logging
from flask import Flask, request, jsonify

# Initialize Flask
server = Flask(__name__)

# Configure Logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# Database Connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST'),
            database=os.getenv('DATABASE_NAME'),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD'),
            port=5432
        )
        return conn
    except Exception as e:
        logging.exception("❌ Failed to connect to PostgreSQL")
        raise

# JWT Creator
def CreateJWT(username, secret, authz):
    token = jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
            "iat": datetime.datetime.now(tz=datetime.timezone.utc),
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )
    return jsonify(token=token)

# 🔐 Login Route
@server.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        logging.warning("🚫 Missing or invalid basic auth headers")
        return 'Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

    auth_table_name = os.getenv('AUTH_TABLE')
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = f"SELECT email, password FROM {auth_table_name} WHERE email = %s"
        cur.execute(query, (auth.username,))
        user_row = cur.fetchone()

        if not user_row:
            logging.info(f"🔍 No user found with email: {auth.username}")
            return 'Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

        email, password = user_row
        if auth.password != password:
            logging.warning(f"❌ Incorrect password for {auth.username}")
            return 'Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

        logging.info(f"✅ Authenticated: {auth.username}")
        return CreateJWT(auth.username, os.environ['JWT_SECRET'], True)

    except Exception as e:
        logging.exception("🔥 Exception during login")
        return 'Internal server error', 500
    finally:
        if conn:
            conn.close()

# 🧪 Token Validation
@server.route('/validate', methods=['POST'])
def validate():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        logging.warning("🚫 No Authorization header provided")
        return 'Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

    try:
        encoded_jwt = auth_header.split(' ')[1]
        decoded_jwt = jwt.decode(encoded_jwt, os.environ['JWT_SECRET'], algorithms=["HS256"])
        logging.info(f"🔐 JWT validated for user: {decoded_jwt.get('username')}")
        return jsonify(decoded_jwt), 200
    except Exception as e:
        logging.warning("❌ JWT validation failed")
        return 'Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

# App Runner
if __name__ == '__main__':
    logging.info("🚀 Auth service starting on port 5000...")
    server.run(host='0.0.0.0', port=5000)
