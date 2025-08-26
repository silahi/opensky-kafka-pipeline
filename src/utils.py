import json
import logging

# ----------------------------
# Logger configuration
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("producer")

def load_config(path="../config/confluent_config.json"):
    """Charge la configuration Confluent Cloud depuis un fichier JSON."""
    with open(path, "r") as f:
        return json.load(f)

def delivery_report(err, msg):
    """Callback de Kafka : succès ou échec de livraison."""
    if err is not None:
        logger.error(f"❌ Delivery failed: {err}")
    else:
        logger.info(f"✅ Delivered to {msg.topic()} [{msg.partition()}] offset {msg.offset()}")
