import json
import random
import time

from faker import Faker
from confluent_kafka import SerializingProducer
from datetime import datetime

fake = Faker()


def shop_transactions():
    user = fake.simple_profile()

    return {
        "transactionId": fake.uuid4(),
        "productId": fake.uuid4(),
        "productName": random.choice(
            ['Iphone', 'Tecno', 'Itel', 'Samsung', 'Redmi', 'Nokia', 'Huawei', 'Xiaomi', 'Google']),
        "customerId": fake.uuid4(),
        "city": random.choice(['Nakuru', 'Momabasa', 'Thika', 'Eldoret', 'Nairobi', 'Kisumu', 'Kisii']),
        "region": random.choice(['Central', 'North', 'East', 'West', 'South']),
        "transactionDate": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
        "productPrice": round(random.uniform(1000, 100000), ),
        "productQuantity": random.randint(1, 4),
        "paymentMethod": random.choice(['M-pesa', 'Fuliza', 'Hustler Fund', 'cash', 'credit card'])

    }


def delivery_report(err, msg):
    if err is not None:
        print(f'message delivery failed: {err}')
    else:
        print(f"message delivered to {msg.topic}[{msg.partition()}")


def main():
    topic = 'financial_transaction'
    producer = SerializingProducer({
        'bootstrap.servers': 'localhost:9093'
    })
    curr_time = datetime.now()

    while (datetime.now() - curr_time).seconds < 120:
        try:
            transaction = shop_transactions()
            transaction['totalAmount'] = transaction['productPrice'] * transaction['productQuantity']
            print(transaction)

            producer.produce(topic,
                             key=transaction['transactionId'],
                             value=json.dumps(transaction),
                             on_delivery=delivery_report)

            producer.poll(0)
            # wait for 5 seconds before next transaction
            time.sleep(5)
        except BufferError:
            print("waiting")
            time.sleep(1)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
