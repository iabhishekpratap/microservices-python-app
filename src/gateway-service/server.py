import os, gridfs, pika, json, logging
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

server = Flask(__name__)

# MongoDB Connections
mongo_video = PyMongo(server, uri=os.getenv('MONGODB_VIDEOS_URI'))
mongo_mp3 = PyMongo(server, uri=os.getenv('MONGODB_MP3S_URI'))

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

# RabbitMQ Connection
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq", heartbeat=0))
    channel = connection.channel()
except Exception as e:
    logging.exception("🐰 Failed to connect to RabbitMQ")
    channel = None

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)
    return token if not err else err

@server.route("/upload", methods=["POST"])
def upload():
    access_payload, err = validate.token(request)
    if err:
        return err

    access_payload = json.loads(access_payload)

    if not access_payload.get("admin"):
        return "not authorized", 401

    if len(request.files) != 1:
        return "exactly 1 file required", 400

    for _, f in request.files.items():
        err = util.upload(f, fs_videos, channel, access_payload)
        if err:
            return err

    return "success!", 200

@server.route("/download", methods=["GET"])
def download():
    access_payload, err = validate.token(request)
    if err:
        return err

    access_payload = json.loads(access_payload)

    if not access_payload.get("admin"):
        return "not authorized", 401

    fid_string = request.args.get("fid")
    if not fid_string:
        return "fid is required", 400

    try:
        out = fs_mp3s.get(ObjectId(fid_string))
        return send_file(out, download_name=f"{fid_string}.mp3")
    except Exception as e:
        logging.exception("Failed to fetch file from GridFS")
        return "internal server error", 500

if __name__ == "__main__":
    logging.info("🚀 Upload service starting on port 8080...")
    server.run(host="0.0.0.0", port=8080)
