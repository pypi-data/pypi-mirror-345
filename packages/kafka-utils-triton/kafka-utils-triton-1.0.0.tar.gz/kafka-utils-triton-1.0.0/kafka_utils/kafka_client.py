from confluent_kafka import Producer, Consumer, KafkaException
from kafka_utils.logger import get_logger

logger = get_logger("kafka_utils")

class KafkaPublisher:
    @staticmethod
    def publish(topic: str, server: str, value: str, key: str = None):
        p = Producer({'bootstrap.servers': server})
        try:
            p.produce(
                topic=topic,
                key=key,
                value=value,
                callback=lambda err, msg: (
                    logger.error(f"Error: {err}") if err else logger.info(f"Delivered to {msg.topic()} [{msg.partition()}]")
                )
            )
            p.flush()
        except KafkaException as e:
            logger.error(f"Publishing failed: {e}", exc_info=True)


class KafkaSubscriber:
    @staticmethod
    def subscribe(topic: str, server: str, group_id: str):
        c = Consumer({
            'bootstrap.servers': server,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        try:
            c.subscribe([topic])
            logger.info(f"Subscribed to topic: {topic}")

            while True:
                msg = c.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error(f"Consumer error: {msg.error()}")
                    continue

                logger.info(f"Received message: key={msg.key()}, value={msg.value()}")
        except KeyboardInterrupt:
            logger.info("Subscription interrupted")
        finally:
            c.close()