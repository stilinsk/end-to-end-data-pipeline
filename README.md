# end-to-end-data-pipeline

In the follwoing project we will be doing a data engineering data pipeline.


 PART ONE
 PYTHON   >>>> KAFKA >>> FLINK >>> POSTGRES 


![7b294e85-6847-4e80-8985-4d684130db56](https://github.com/user-attachments/assets/8c8afe04-c542-401a-91f0-8f501cfeb9d1)


 
 ### PART TWO
  >>>> DBT >>>>POWERBI
> >>> 

 
 ![Screenshot from 2024-07-18 12-22-26](https://github.com/user-attachments/assets/df7f2c29-baf4-40b3-a750-1f36a1b5ff75)


In the first part of our project, we will generate a Docker Compose file that includes all the images we want to run. Then, we will create a Python file to generate sales data. After that, we will stream data to Kafka and process it using Flink. Once the data is streamed using Flink, we will load it into PostgreSQL.


 That's the architechture in  a nut shell.will try to dimestify the first part for  now as easy as possible to help you grasp the concepts and understand how to do the project.



The following tools will be used:

### 1. VS Code

We will use VS Code to create a Python file that generates sales data, which will be run in an environment. We will also create a Docker Compose file from here. Ensure you have it installed, although you can also use PyCharm (it does a great job, as you don't have to manually create an environment, and it handles indentation well).

Since we will be using dbt for this project in later stages, it is advisable to use VS Code as it offers additional help and architecture when working with dbt files.

### 2. IntelliJ IDEA

We will use this text editor to work on Java since Flink primarily runs on Java. In Java, we will do a streaming job where we deserialize data from Kafka and create a sink to load the data into PostgreSQL.

### 3. Docker

Make sure you have Docker installed on your system, as we will need it extensively. Also, install Docker Desktop on your machine; this will help visualize the Docker images installed on your system and monitor the state of the entire data architecture.

### 4. Kafka

We will send the data from the Python file to Kafka, which will be running as a Docker image on localhost to receive the data from Kafka running on Zookeeper. We will then expose the port to grant access to the data to Flink.

### 5. Flink

In this project, we will use Flink to access the data in Kafka. We will deserialize the data and load it, then create a sink to load the data into PostgreSQL.

### 6. PostgreSQL

This will be an image to receive the data after deserialization by Flink. Once this is done, the data can be directly accessed in PostgreSQL.

This will be the first part of our architecture, and we will perform these tasks before proceeding with data modeling and data visualization.




The docker images are 
```
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    hostname: zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    healthcheck:
      test: [ "CMD", "bash", "-c", "echo 'ruok' | nc localhost 2181" ]
      interval: 10s
      timeout: 5s
      retries: 5

  broker:
    image: confluentinc/cp-kafka:7.4.0
    hostname: broker
    container_name: broker
    depends_on:
      zookeeper:
        condition: service_healthy
    ports:
      - "9093:9093"
      - "9101:9101"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://broker:29093,PLAINTEXT_HOST://localhost:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_CONFLUENT_LICENSE_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_CONFLUENT_BALANCER_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_JMX_PORT: 9101
      KAFKA_JMX_HOSTNAME: localhost
    healthcheck:
      test: [ "CMD", "bash", "-c", 'nc -z localhost 9093' ]
      interval: 10s
      timeout: 5s
      retries: 5

  postgres:
    image: postgres:latest
    container_name: postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    healthcheck:
      test: [ "CMD", "pg_isready", "-U", "postgres" ]
      interval: 10s
      timeout: 5s
      retries: 5
```

Instructions for Setting Up and Running the Environment
Docker Compose Setup

Ensure your docker-compose.yml file is properly configured with Zookeeper, Kafka broker, and PostgreSQL services.
Run the following command to start the services:
```
docker compose up -d
```
Note: It might take some time for the Kafka broker to start running. Ensure that all services are up and running before proceeding.
Kafka and PostgreSQL Configuration

Ensure the Kafka broker's hostname (localhost:9093 in your Java code) matches the configuration in your Python file that generates sales transactions.
Make sure the PostgreSQL login credentials (username: postgres, password: postgres, jdbcUrl: jdbc:postgresql://localhost:5432/postgres) match those used in the Flink job.
Running the Python File

Use the following command to run the Python script:
```
python main.py



```
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
```
here is the breakdown
```
### 1. Imports

```python
import json
import random
import time
from faker import Faker
from confluent_kafka import SerializingProducer
from datetime import datetime
```
These lines import the necessary libraries:
- `json` for handling JSON data.
- `random` for generating random values.
- `time` for adding delays.
- `Faker` for generating fake data.
- `SerializingProducer` from the Confluent Kafka library for producing messages to Kafka.
- `datetime` for working with date and time.

### 2. Create a Faker Instance

```python
fake = Faker()
```
This creates an instance of the `Faker` class, which will be used to generate fake data.

### 3. Function to Generate Fake Shop Transactions

```python
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
        "productPrice": round(random.uniform(1000, 100000)),
        "productQuantity": random.randint(1, 4),
        "paymentMethod": random.choice(['M-pesa', 'Fuliza', 'Hustler Fund', 'cash', 'credit card'])
    }
```
This function generates a fake transaction with various details:
- `transactionId`, `productId`, `customerId`: Unique IDs for the transaction, product, and customer.
- `productName`: A random product name from a predefined list.
- `city`: A random city from a predefined list.
- `region`: A random region from a predefined list.
- `transactionDate`: The current date and time in a specific format.
- `productPrice`: A random price between 1000 and 100000.
- `productQuantity`: A random quantity between 1 and 4.
- `paymentMethod`: A random payment method from a predefined list.

### 4. Function for Delivery Report

```python
def delivery_report(err, msg):
    if err is not None:
        print(f'message delivery failed: {err}')
    else:
        print(f"message delivered to {msg.topic}[{msg.partition()}")
```
This function handles the result of message delivery to Kafka:
- If there is an error (`err`), it prints a failure message.
- If there is no error, it prints a success message with the topic and partition where the message was delivered.

### 5. Main Function to Produce Messages to Kafka

```python
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
            time.sleep(5)
        except BufferError:
            print("waiting")
            time.sleep(1)
        except Exception as e:
            print(e)
```
This function does the following:
1. Sets the Kafka topic name to `'financial_transaction'`.
2. Creates a Kafka producer connected to `localhost:9093`.
3. Records the current time.
4. Continuously runs a loop for 2 minutes (120 seconds):
   - Generates a fake transaction.
   - Calculates the total amount (`productPrice` multiplied by `productQuantity`).
   - Prints the transaction.
   - Sends the transaction to Kafka, specifying the topic, key, and value. It also sets the delivery report function.
   - Calls `producer.poll(0)` to handle delivery reports.
   - Waits for 5 seconds before generating the next transaction.
   - If there is a buffer error (i.e., Kafka is not ready), it waits for 1 second.
   - Prints any other exceptions that occur.

### 6. Entry Point

```python
if __name__ == "__main__":
    main()
```
This line ensures that the `main` function is called when the script is run directly.
to start consuming the data we will run these two commands

```
docker exec -it broker /bin/bash
kafka-console-consumer --bootstrap-server localhost:9093 --topic financial_transaction --from-beginning
```

### Summary
This script generates fake shop transactions and sends them to a Kafka topic called `financial_transaction`. It generates a new transaction every 5 seconds for 2 minutes and handles any errors that occur during the process.



#### Prerequisites
Install Flink on your system and start it (while in the bin folder, run this command: ./start-cluster.sh).


Create a new project in IntelliJ IDEA using the Maven archetype.

The JDK should be Java 11, as it is most compatible with Flink.

The catalog will be Maven Central.

The archetype will be Flink Quickstart Java.


The version should be the same as the one installed on your system.

package flink.project;

import Deserializer.JSONValueDeserializationSchema;
import dto.transaction;
import org.apache.flink.annotation.docs.Documentation;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.connector.jdbc.JdbcConnectionOptions;
import org.apache.flink.connector.jdbc.JdbcExecutionOptions;
import org.apache.flink.connector.jdbc.JdbcStatementBuilder;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.connector.jdbc.JdbcSink;

public class DataStreamJob {

	private static final String jdbcUrl ="jdbc:postgresql://localhost:5432/postgres";
	private static final String username = "postgres";
	private static final String password = "postgres";

	public static void main(String[] args) throws Exception {

		final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

		String topic = "financial_transaction";
		KafkaSource<transaction> source = KafkaSource.<transaction>builder()
						.setBootstrapServers("localhost:9093")
								.setTopics(topic)
										.setGroupId("flink-Group")
												.setStartingOffsets(OffsetsInitializer.earliest())
														.setValueOnlyDeserializer(new JSONValueDeserializationSchema())
																.build();
		DataStream<transaction>transactionStream=env.fromSource(source, WatermarkStrategy.noWatermarks(),"Kafka source");

		transactionStream.print();

		JdbcExecutionOptions execOptions =new JdbcExecutionOptions.Builder().withBatchSize(1000)
				.withBatchIntervalMs(200).withMaxRetries(5).build();

		JdbcConnectionOptions connOptions =new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
				.withUrl(jdbcUrl)
				.withDriverName("org.postgresql.Driver")
				.withUsername(username)
				.withPassword(password).build();

		//create transaction table
		transactionStream.addSink(JdbcSink.sink(
				"CREATE TABLE IF NOT EXISTS transaction (" +
						"transaction_id VARCHAR(255) PRIMARY KEY, " +
						"product_id VARCHAR(255), " +
						"product_name VARCHAR(255), " +
						"customer_id VARCHAR(255), " +
						"city VARCHAR(255), " +
						"region VARCHAR(255), " +
						"transaction_date TIMESTAMP, " +
						"product_price DOUBLE PRECISION, " +
						"product_quantity INTEGER, " +
						"payment_method VARCHAR(255), " +
						"total_amount DOUBLE PRECISION" +
						")",

				(preparedStatement, transaction) -> {},
				execOptions,
				connOptions
		));

		transactionStream.addSink(JdbcSink.sink(
				"INSERT INTO transaction " +
						"(transaction_id, product_id, product_name, customer_id,city,region ,transaction_date,product_price, " +
						"product_quantity, payment_method, total_amount) " +
						"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) " +
						"ON CONFLICT (transaction_id) DO UPDATE SET " +
						"product_id = EXCLUDED.product_id, " +
						"product_name = EXCLUDED.product_name, " +
						"customer_id = EXCLUDED.customer_id, " +
						"city = EXCLUDED.city, " +
						"region = EXCLUDED.region, " +
						"transaction_date = EXCLUDED.transaction_date, " +
						"product_price = EXCLUDED.product_price, " +
						"product_quantity = EXCLUDED.product_quantity, " +
						"payment_method = EXCLUDED.payment_method, " +
						"total_amount = EXCLUDED.total_amount " +
						"WHERE transaction.transaction_id = EXCLUDED.transaction_id",
				// Statement builder for INSERT statement
				(preparedStatement, transaction) -> {
					preparedStatement.setString(1, transaction.getTransactionId());
					preparedStatement.setString(2, transaction.getProductId());
					preparedStatement.setString(3, transaction.getProductName());
					preparedStatement.setString(4, transaction.getCustomerId());
					preparedStatement.setString(5, transaction.getCity());
					preparedStatement.setString(6, transaction.getRegion());
					preparedStatement.setTimestamp(7, transaction.getTransactionDate());
					preparedStatement.setDouble(8, Double.parseDouble(transaction.getProductPrice()));
					preparedStatement.setInt(9, transaction.getProductQuantity());
					preparedStatement.setString(10, transaction.getPaymentMethod());
					preparedStatement.setInt(11, transaction.getTotalAmount());
				},
				execOptions,
				connOptions
		)).name("Insert into transaction table");



		env.execute("Flink consumer for shop data");
	}
}

```
Here is a brief explanation of how our code works

```


### Package and Imports
```java
package flink.project;

import Deserializer.JSONValueDeserializationSchema;
import dto.transaction;
import org.apache.flink.annotation.docs.Documentation;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.connector.jdbc.JdbcConnectionOptions;
import org.apache.flink.connector.jdbc.JdbcExecutionOptions;
import org.apache.flink.connector.jdbc.JdbcStatementBuilder;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.connector.jdbc.JdbcSink;
```
- **Package Declaration**: `package flink.project;` indicates the package name for the current Java file.
- **Imports**: Various imports for the required classes and interfaces from Flink, Kafka, and JDBC libraries. These include deserialization schemas, Kafka sources, JDBC connection options, and execution options.

### Class Definition
```java
public class DataStreamJob {
```
- **Class Declaration**: Defines the `DataStreamJob` class which will contain the Flink job.

### Database Connection Constants
```java
private static final String jdbcUrl ="jdbc:postgresql://localhost:5432/postgres";
private static final String username = "postgres";
private static final String password = "postgres";
```
- **Database Connection Details**: Constants for JDBC URL, username, and password for connecting to a PostgreSQL database.

### Main Method
```java
public static void main(String[] args) throws Exception {
```
- **Main Method**: Entry point of the Java application. Throws `Exception` to handle any potential errors.

### Stream Execution Environment
```java
final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
```
- **Execution Environment**: Sets up the Flink execution environment, which is the context in which the job will run.

### Kafka Source Configuration
```java
String topic = "financial_transaction";
KafkaSource<transaction> source = KafkaSource.<transaction>builder()
                .setBootstrapServers("localhost:9093")
                .setTopics(topic)
                .setGroupId("flink-Group")
                .setStartingOffsets(OffsetsInitializer.earliest())
                .setValueOnlyDeserializer(new JSONValueDeserializationSchema())
                .build();
DataStream<transaction>transactionStream=env.fromSource(source, WatermarkStrategy.noWatermarks(),"Kafka source");
```
- **Kafka Source Setup**:
  - Defines the Kafka topic name.
  - Builds a Kafka source with the following configurations:
    - **Bootstrap Servers**: Kafka broker address.
    - **Topics**: The Kafka topic to read from.
    - **GroupId**: Consumer group ID for Kafka.
    - **OffsetsInitializer**: Start reading from the earliest offset.
    - **Deserializer**: Custom deserializer to convert JSON messages to `transaction` objects.
- **Data Stream**: Creates a `DataStream` from the Kafka source, with no watermark strategy and labels it as "Kafka source".

### Print Stream Data
```java
transactionStream.print();
```
- **Print**: Prints the data from the stream to the console for debugging purposes.

### JDBC Execution Options
```java
JdbcExecutionOptions execOptions =new JdbcExecutionOptions.Builder().withBatchSize(1000)
        .withBatchIntervalMs(200).withMaxRetries(5).build();
```
- **JDBC Execution Options**: Configures execution options for JDBC sink:
  - **Batch Size**: Number of records to write in a single batch.
  - **Batch Interval**: Time interval between batches.
  - **Max Retries**: Number of retries in case of failure.

### JDBC Connection Options
```java
JdbcConnectionOptions connOptions =new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
        .withUrl(jdbcUrl)
        .withDriverName("org.postgresql.Driver")
        .withUsername(username)
        .withPassword(password).build();
```
- **JDBC Connection Options**: Configures the connection details to the PostgreSQL database:
  - **URL**: JDBC URL.
  - **Driver Name**: PostgreSQL JDBC driver.
  - **Username**: Database username.
  - **Password**: Database password.

### Create Transaction Table
```java
transactionStream.addSink(JdbcSink.sink(
        "CREATE TABLE IF NOT EXISTS transaction (" +
                "transaction_id VARCHAR(255) PRIMARY KEY, " +
                "product_id VARCHAR(255), " +
                "product_name VARCHAR(255), " +
                "customer_id VARCHAR(255), " +
                "city VARCHAR(255), " +
                "region VARCHAR(255), " +
                "transaction_date TIMESTAMP, " +
                "product_price DOUBLE PRECISION, " +
                "product_quantity INTEGER, " +
                "payment_method VARCHAR(255), " +
                "total_amount DOUBLE PRECISION" +
                ")",

        (preparedStatement, transaction) -> {},
        execOptions,
        connOptions
));
```
- **Sink to Create Table**: Adds a sink to the stream that executes a SQL statement to create the `transaction` table if it does not already exist.
- **SQL Statement**: Defines the table schema with various columns.

### Insert Data into Transaction Table
```java
transactionStream.addSink(JdbcSink.sink(
        "INSERT INTO transaction " +
                "(transaction_id, product_id, product_name, customer_id,city,region ,transaction_date,product_price, " +
                "product_quantity, payment_method, total_amount) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) " +
                "ON CONFLICT (transaction_id) DO UPDATE SET " +
                "product_id = EXCLUDED.product_id, " +
                "product_name = EXCLUDED.product_name, " +
                "customer_id = EXCLUDED.customer_id, " +
                "city = EXCLUDED.city, " +
                "region = EXCLUDED.region, " +
                "transaction_date = EXCLUDED.transaction_date, " +
                "product_price = EXCLUDED.product_price, " +
                "product_quantity = EXCLUDED.product_quantity, " +
                "payment_method = EXCLUDED.payment_method, " +
                "total_amount = EXCLUDED.total_amount " +
                "WHERE transaction.transaction_id = EXCLUDED.transaction_id",
        // Statement builder for INSERT statement
        (preparedStatement, transaction) -> {
            preparedStatement.setString(1, transaction.getTransactionId());
            preparedStatement.setString(2, transaction.getProductId());
            preparedStatement.setString(3, transaction.getProductName());
            preparedStatement.setString(4, transaction.getCustomerId());
            preparedStatement.setString(5, transaction.getCity());
            preparedStatement.setString(6, transaction.getRegion());
            preparedStatement.setTimestamp(7, transaction.getTransactionDate());
            preparedStatement.setDouble(8, Double.parseDouble(transaction.getProductPrice()));
            preparedStatement.setInt(9, transaction.getProductQuantity());
            preparedStatement.setString(10, transaction.getPaymentMethod());
            preparedStatement.setInt(11, transaction.getTotalAmount());
        },
        execOptions,
        connOptions
)).name("Insert into transaction table");
```
- **Sink to Insert Data**: Adds a sink to insert data into the `transaction` table.
- **SQL Statement**: Inserts data with conflict handling using `ON CONFLICT` clause to update existing records.
- **Statement Builder**: Sets the prepared statement parameters using the `transaction` object's getters.

### Execute Flink Job
```java
env.execute("Flink consumer for shop data");
```
- **Execute**: Starts the Flink job with the specified job name "Flink consumer for shop data".

This code sets up a Flink job to read financial transaction data from a Kafka topic, print it to the console, and store it in a PostgreSQL database, creating the table if it doesn't exist and handling conflicts during insertions.

We will also be doing a deserializer for our data in flink where we will be reading the data from kafka converts the format from a json one

```
package Deserializer;

import com.fasterxml.jackson.databind.ObjectMapper;
import dto.transaction;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.util.Collector;

import java.io.IOException;

public class JSONValueDeserializationSchema implements DeserializationSchema<transaction> {

    private final ObjectMapper objectMapper=new ObjectMapper();
    @Override
    public void open(InitializationContext context) throws Exception {
        DeserializationSchema.super.open(context);
    }

    @Override
    public transaction deserialize(byte[] bytes) throws IOException {
        return objectMapper.readValue(bytes, transaction.class);
    }


    @Override
    public boolean isEndOfStream(transaction transaction) {
        return false;
    }

    @Override
    public TypeInformation<transaction> getProducedType() {
        return TypeInformation.of(transaction.class);
    }
}
```

Here is how the code works
```
Let's break down the `JSONValueDeserializationSchema` class, which is responsible for deserializing JSON data into `transaction` objects for use in a Flink job.

### Package and Imports
```java
package Deserializer;

import com.fasterxml.jackson.databind.ObjectMapper;
import dto.transaction;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.util.Collector;

import java.io.IOException;
```
- **Package Declaration**: Indicates the package name as `Deserializer`.
- **Imports**: Imports necessary classes from Jackson for JSON processing, Flink's deserialization schema interface, type information, and utilities.

### Class Definition
```java
public class JSONValueDeserializationSchema implements DeserializationSchema<transaction> {
```
- **Class Declaration**: Defines the `JSONValueDeserializationSchema` class which implements the `DeserializationSchema<transaction>` interface from Flink.

### ObjectMapper Instance
```java
private final ObjectMapper objectMapper = new ObjectMapper();
```
- **ObjectMapper**: Creates an instance of `ObjectMapper` from the Jackson library for converting JSON to Java objects.

### open Method
```java
@Override
public void open(InitializationContext context) throws Exception {
    DeserializationSchema.super.open(context);
}
```
- **open Method**: This method is called when the deserialization schema is opened. It calls the superclass method to handle any required initialization.
  
### deserialize Method
```java
@Override
public transaction deserialize(byte[] bytes) throws IOException {
    return objectMapper.readValue(bytes, transaction.class);
}
```
- **deserialize Method**: This method is responsible for deserializing byte arrays into `transaction` objects.
  - **Parameters**: Takes a byte array (`bytes`) as input.
  - **Returns**: Converts the byte array into a `transaction` object using the `ObjectMapper`.

### isEndOfStream Method
```java
@Override
public boolean isEndOfStream(transaction transaction) {
    return false;
}
```
- **isEndOfStream Method**: This method determines whether the end of the stream has been reached.
  - **Parameters**: Takes a `transaction` object as input.
  - **Returns**: Always returns `false`, indicating that the stream should never end based on the content of a `transaction`.

### getProducedType Method
```java
@Override
public TypeInformation<transaction> getProducedType() {
    return TypeInformation.of(transaction.class);
}
```
- **getProducedType Method**: This method returns the `TypeInformation` for the `transaction` class.
  - **Returns**: Uses `TypeInformation.of(transaction.class)` to provide type information about the produced `transaction` objects.

### Summary
The `JSONValueDeserializationSchema` class is a custom deserialization schema for Flink that converts JSON byte arrays into `transaction` objects using Jackson's `ObjectMapper`. It implements the required methods from Flink's `DeserializationSchema` interface:
- **`open`**: Initializes the schema.
- **`deserialize`**: Converts byte arrays into `transaction` objects.
- **`isEndOfStream`**: Always returns `false`, indicating that there is no predefined end to the stream.
- **`getProducedType`**: Returns the type information for the `transaction` class.

  we will also be setting our getters and setters using lombok in a class

```
package dto;

import java.sql.Timestamp;
import lombok.Data;

@Data
public class transaction {
    private String transactionId;
    private String productId;
    private String productName;
    private String customerId;
    private String city;
    private String region;
    private Timestamp transactionDate;
    private String productPrice;
    private int productQuantity ;
    private String paymentMethod;
    private int  totalAmount;
}

```

after finishing this we will be doing the following commands to submit our flink job

```
mvn clean compile
mvn package
```

when it says build success then means the job is ready fro my pc this was the command i used to run the flink job

``` ~/flink/flink/flink/bin/flink run -c flink.project.DataStreamJob target/FlinkCommerce-1.0-SNAPSHOT.jar```

 PART TWO NEXT
 
   ![Screenshot from 2024-07-18 12-22-26](https://github.com/user-attachments/assets/df7f2c29-baf4-40b3-a750-1f36a1b5ff75)




