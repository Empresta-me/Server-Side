import pika
import threading 
import os

class pub_sub:

    @staticmethod
    def test_publish(user_pub_key, message):

        print("\n[" + message + "] published to -" + user_pub_key + "- exchange")

        # Establish a connection with RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit'))
        channel = connection.channel()

       # declare the exchange to publish to
        channel.exchange_declare(exchange=user_pub_key, exchange_type='fanout')
        
        channel.basic_publish(exchange=user_pub_key, routing_key='', body=message)

        # Close the connection
        connection.close() 



msg = '{"header": "VOUCH", "state": "FOR", "clock": 0, "sender": "ndShu87QAz6cxEhFN2arSuKRmY9A848mMqwKnQYVuMwj", "receiver": "wGzeUWSGYpNcf8xNfQw2GJG1RnNidDY5YNn9aQFxUhXJ", "message": "Test message", "nonce": 258, "hash": "14YZBN8NVqJKyznFbvDuz6Gj1SC5ZDd6qSPX8WiwVxph", "signature": "381yXZGLpqGyEU5X7nRYknhUfxBg46nv8fSgGr6xRXbhJJGrudZBjXjVFt49tU3vWCizfuE9a8hoiWArieCzVDg6vCy3PYTj"}'

pub_sub.test_publish("ndShu87QAz6cxEhFN2arSuKRmY9A848mMqwKnQYVuMwj", msg)
