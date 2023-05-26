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



msg = '{"header": "VOUCH", "state": "FALSE", "clock": 0, "sender": "ndShu87QAz6cxEhFN2arSuKRmY9A848mMqwKnQYVuMwj", "receiver": "h8MUzTD7a67D4iVHWJudJ1LFhbtiojmLcKzd4W9Yka34", "message": "Test message", "nonce": 45, "hash": "1SJkHUCUgv2rCS5EQU8aBwad5nsjEQJs2LvkGz72Ra4", "signature": "381yXZQYZ5Vdq28XHkDYQeyNXiV95rfWLttzHpjyEu3rLApB272xWUqMm25MXfezAkFqgxs1pc1WedGQADQ9U5XBcunf1K5R"}'

pub_sub.test_publish("ndShu87QAz6cxEhFN2arSuKRmY9A848mMqwKnQYVuMwj", msg)
