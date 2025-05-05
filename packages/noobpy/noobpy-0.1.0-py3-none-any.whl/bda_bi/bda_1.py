print("""step 1

start-dfs.sh
start-yarn.sh

step 2

jps

step 3

nano mapper.py

#!/usr/bin/env python3
import sys

for line in sys.stdin:
    words = line.strip().split()
    for word in words:
        print(f"{word}\\t1")

step 4

nano reducer.py


#!/usr/bin/env python3
import sys

current_word = None
current_count = 0

for line in sys.stdin:
    word, count = line.strip().split("\\t")
    count = int(count)

    if current_word == word:
        current_count += count
    else:
        if current_word:
            print(f"{current_word}\\t{current_count}")
        current_word = word
        current_count = count

if current_word == word:
    print(f"{current_word}\\t{current_count}")


step 5


hadoop fs -mkdir /input

step 6

nano input.txt


step 7


Hadoop is an open-source framework used for storing and processing large datasets across clusters of computers. It uses a distributed file system (HDFS) and the MapReduce programming model. Designed for scalability and fault tolerance, Hadoop enables efficient data analysis and is widely used in big data applications across industries.


step 8


hadoop fs -put input.txt /input


step 9


hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar \
    -D mapreduce.job.reduces=1 \
    -input /input \
    -output /output \
    -mapper mapper.py \
    -reducer reducer.py

step 10 

hadoop fs -ls /output


step 11

hadoop fs -cat /output/part-00000""")

