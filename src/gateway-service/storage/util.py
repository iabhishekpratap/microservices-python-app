import pika, json, logging

def upload(f, fs, channel, access):
    try:
        logging.info(f"📁 Received file: {f.filename}")
        fid = fs.put(f)
        logging.info(f"✅ Stored file in GridFS with ID: {fid}")
    except Exception as err:
        logging.exception("🔥 GridFS save failed")
        return "internal server error, fs level", 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
        )
        logging.info("📤 Published message to RabbitMQ")
    except Exception as err:
        logging.exception("🔥 RabbitMQ publish failed")
        fs.delete(fid)
        return f"internal server error rabbitmq issue, {err}", 500
