import pika
import threading 
import os

class pub_sub:

    @staticmethod
    def start_listening(user_pub_key, on_message):

        print("\nStarting to listen to " + user_pub_key + "...")

        # create a connection to RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbit'))
        channel = connection.channel()

        # declare the exchange to subscribe to
        channel.queue_declare(queue=user_pub_key, durable=True)

        # start consuming messages in a separate thread
        def consume():
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=user_pub_key, on_message_callback=on_message, auto_ack=True)
            channel.start_consuming()

        thread = threading.Thread(target=consume)
        thread.start()


    @staticmethod
    def test_publish(user_pub_key, message):

        print("\n[" + message + "] published to -" + user_pub_key + "- exchange")

        # Establish a connection with RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1'))
        channel = connection.channel()

       # declare the exchange to publish to
        channel.exchange_declare(exchange=user_pub_key, exchange_type='fanout')
        
        channel.basic_publish(exchange=user_pub_key, routing_key='', body=message)

        # Close the connection
        connection.close() 


# define a function to handle incoming messages
def on_message(channel, method, properties, body): 
    print("Received message: {}".format(body.decode()), flush=True)
    # do something with the message here

#pub_sub.start_listening("my_pub_key2", on_message)
#pub_sub.test_publish("my_pub_key2", "O/_\\O")
