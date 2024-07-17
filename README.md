# end-to-end-data-pipeline

In the follwoing project we will be doing a data engineering data pipeline.

data architechture  for part one of our pipeline

 PYTHON   >>>> KAFKA >>> FLINK >>> POSTGRES 
 
![7b294e85-6847-4e80-8985-4d684130db56](https://github.com/user-attachments/assets/8c8afe04-c542-401a-91f0-8f501cfeb9d1)


 
 ### PART TWO
 >>>> DBT >>>>POWERBI

 Its alot on the first part of our project we will  be generating  a docker compose file that will contain images of all the images that we want to run and then create a python file that generates sales data .From there we will stream data to kafka and process the data using Flink .After streaming the data using flink we will then load the data posgres.


 Thats the architechture in  a nut shell.will try to dimestify the first part for  now as easy as possible to help you grasp the concepts and understand how to do the project.

The following tools will be used
### 1.vs code
This we will be using to create a python file that will be for generating the sales data  and this will actually be run in an environment and we will also be creating a docker compose file still from here ,make sure you have it installed although you can still use pycharm( does also a very good job you dont have to manually create an environment and also it does a very good job with indenting)

since we will also be using dbt for this project in later satges of the project ,it will be advisable to use vs code  as it offers even further help and architechture when working with dbt files

### 2. Intellij idea

We will be using text editor to work on javasince flink promarily runs on java.so in Java we will do a streaming job where we will be diserializing data from kafka and  do a sink to load the daa into postgres

### 3.docker 
Make sure a  yo have docker installed in your system we will need it a great deal.also would be required to install docker desktop in your machine ,this will help visualize the docker images that have been installed in your system and also to look for the state in the entire data architechture

### 4. Kafka
We will be sending the data from the python file to kafka that will be running and docker image of lafla on localhost to recieve the data from kafka  that is running on zookeeper and  then expose the port to grant access the data to flinl

### 5.FLINK

In the following kafka program we will using flink to access  the data that is already in kafka and we will diserialize the data and load  the data  and then create a sink to  laod the data on postgres

### 6. postgres

Also this will be an image to recieve the data after diserialization by flink thus after this now the data can be directly accessed on postgres


This will be the first part of our architechture and we will be perfoming these tasks before perfoming data modelling and data visualization.



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

For the below commands to work we will need to put the following command
``docker compose up -d```
give it time as for the broker may take time before it starts running

The zookeeper,broker and postgres respectively  ,make sure the local host on kafka will match that of the python file generator and also ensure that the login credentials on postgres  wil match remember we  will require the credentials while sinking the data to postgres
