import shlex
import subprocess
import pandas as pd

DATA = []

jvm = ''
heap_space = ''
ram = ''
topic = 'performance'
replication_factor = 1                                  # replicas
partitions = [2, 4, 8, 16]                              # 2, 4, 8, 16
number_of_records = [1000, 10000, 100000, 1000000]      # 1 billion records
record_size = [10, 100, 1000, 10000, 100000]            # in bytes 10, 100, 1000, 10000, 100000
acks = [-1, 0, 1]                                       # -1   0   1
buffer_memory = [16000000, 32000000, 64000000]          # in bytes 16MB, 32MB, 64MB,
batch_size = [4000, 8000, 16000, 32000, 64000, 128000]  # in bytes 4000 (4KB), 8000, 16000, 32000, 64000, 128000
throughput = '-1'

create_topic_command = """/Users/zion/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor {} 
--partitions {} --topic {} """.format(replication_factor, partitions, topic)

delete_topic_command = """/Users/zion/kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --delete --topic {}""".format(
    topic)

producer_performance_command = """/Users/zion/kafka/bin/kafka-producer-perf-test.sh 
--topic {} --num-records {} --record-size {} --throughput {} --producer-props 
acks={} bootstrap.servers=localhost:9092 buffer.memory={} batch.size={}""" \
    .format(topic
            , number_of_records
            , record_size
            , throughput
            , acks
            , buffer_memory
            , batch_size)

# create_topic_command = shlex.split(create_topic_command)
delete_topic_command = shlex.split(delete_topic_command)
# producer_performance_command = shlex.split(producer_performance_command)

# print(producer_performance_command)

payload = {'Number of Records': '',
           'Record Size': '',
           'Acks': '',
           'Buffer Memory': '',
           'Batch Size': '',
           'Throughput': '',
           'Partitions': '',
           'Replication': ''
           }


def run_delete(c):
    shell = subprocess.Popen(c,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True,
                             bufsize=0)

    for line in shell.stdout:
        print(line.strip())


def run_create(c):
    shell = subprocess.Popen(c,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True,
                             bufsize=0)

    for line in shell.stdout:
        print(line.strip())


def run(i, a, b, c, d, e, f):
    shell = subprocess.Popen(i,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True,
                             bufsize=0)

    for line in shell.stdout:
        payload = {}
        #print(line)
        l = line.strip().split(' ')
        #print(l)

        try:
            payload['Number of Records'] = b
            payload['Record Size'] = c
            payload['Acks'] = d
            payload['Buffer Memory'] = e
            payload['Batch Size'] = f
            payload['Partitions'] = a
            payload['Replication'] = replication_factor
            payload['Throughput records/sec'] = l[3]
            payload['Throughput MB/sec'] = l[5]
            payload['Average Latency'] = l[7]
            payload['Max Latency'] = l[11]
            payload['50th Latency'] = l[15]
            payload['95th Latency'] = l[18]
            payload['99th Latency'] = l[21]

        except IndexError:
            pass

        DATA.append(payload)
        df = pd.DataFrame(DATA)
        df.to_csv('df.csv', index=False, header=False, mode='a')

        print(payload)

    return shell


for a in partitions:
    create = """/Users/zion/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 
    --replication-factor {} --partitions {} --topic {}""".format(replication_factor, a, topic)

    create = shlex.split(create)
    #print(create)
    run_create(create)  # set up

    for b in number_of_records:
        for c in record_size:
            for d in acks:
                for e in buffer_memory:
                    for f in batch_size:
                        producer = """/Users/zion/kafka/bin/kafka-producer-perf-test.sh 
                        --topic {} --num-records {} --record-size {} --throughput {} --producer-props 
                        acks={} bootstrap.servers=localhost:9092 buffer.memory={} batch.size={}""" \
                            .format(topic
                                    , b
                                    , c
                                    , throughput
                                    , d
                                    , e
                                    , f)
                        producer = shlex.split(producer)
                        #print('First batch: {}'.format(producer))
                        producer = run(producer, a, b, c, d, e, f)
    run_delete(delete_topic_command)

df = pd.DataFrame(DATA)
df.to_csv('df.csv', index=False, header=True, mode='a')
