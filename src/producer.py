import time
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

from fetch_opensky import fetch_opensky_data
from utils import load_config, delivery_report, logger

# ----------------------------
# Charger config Confluent
# ----------------------------
conf = load_config()
TOPIC = conf["topic"]

# ----------------------------
# Configuration Schema Registry
# ----------------------------
schema_registry_conf = {
    "url": conf["schema.registry.url"],
    "basic.auth.user.info": conf["basic.auth.user.info"]
}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

key_schema_str = schema_registry_client.get_latest_version(f"{TOPIC}-key").schema.schema_str
value_schema_str = schema_registry_client.get_latest_version(f"{TOPIC}-value").schema.schema_str

key_avro_serializer = AvroSerializer(schema_registry_client, key_schema_str)
value_avro_serializer = AvroSerializer(schema_registry_client, value_schema_str)

# ----------------------------
# Configuration du Producer Kafka
# ----------------------------
producer_conf = {
    "bootstrap.servers": conf["bootstrap.servers"],
    "security.protocol": conf["security.protocol"],
    "sasl.mechanisms": conf["sasl.mechanism"],
    "sasl.username": conf["sasl.username"],
    "sasl.password": conf["sasl.password"],
    "key.serializer": key_avro_serializer,
    "value.serializer": value_avro_serializer
}
producer = SerializingProducer(producer_conf)

# ----------------------------
# Produire un message Kafka
# ----------------------------
def produce_message(state):
    try:
        value = {
            "icao24": state[0],
            "callsign": state[1].strip() if state[1] else None,
            "origin_country": state[2].strip() if state[2] else None,
            "time_position": int(state[3]) if state[3] else int(time.time()),
            "last_contact": int(state[4]) if state[4] else int(time.time()),
            "longitude": state[5],
            "latitude": state[6],
            "baro_altitude": state[7],
            "on_ground": state[8],
            "velocity": state[9],
            "heading": state[10],
            "vertical_rate": state[11]
        }
        key = {"icao24": state[0]}

        producer.produce(
            topic=TOPIC,
            key=key,
            value=value,
            on_delivery=delivery_report
        )
        producer.poll(0)
        return True
    except Exception as e:
        logger.error(f"Error producing message: {e}")
        return False

# ----------------------------
# Main loop
# ----------------------------
def main():
    logger.info("🚀 Starting OpenSky → Kafka Producer (every 15 secondes)")
    try:
        while True:
            states = fetch_opensky_data()
            if states:
                success_count = 0
                for s in states:
                    if produce_message(s):
                        success_count += 1
                producer.flush()
                logger.info(f"✅ Sent {success_count} messages to '{TOPIC}'")
            else:
                logger.warning("⚠️ No data fetched from OpenSky API")
            logger.info("⏳ Sleeping 15 secondes...")
            time.sleep(15)
    except KeyboardInterrupt:
        logger.info("🛑 Stopping producer...")
        producer.flush()

if __name__ == "__main__":
    main()
