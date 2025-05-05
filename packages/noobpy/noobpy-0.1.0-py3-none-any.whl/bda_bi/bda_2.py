print("""
step 1

start-dfs.sh
start-yarn.sh

step 2

jps

step 3


nano mapper.py

#!/usr/bin/env python3
import sys

# Dimensions (hardcoded or passed through env/config)
# A is m x n
# B is n x p
m = 2  # rows in A
n = 2  # cols in A / rows in B
p = 2  # cols in B

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    matrix, i, j, value = line.split(",")
    i = int(i)
    j = int(j)
    value = float(value)

    if matrix == "A":
        for col in range(p):
            # Key: i,col ; Value: A,j,value
            print(f"{i},{col}\\tA,{j},{value}")
    elif matrix == "B":
        for row in range(m):
            # Key: row,j ; Value: B,i,value
            print(f"{row},{j}\\tB,{i},{value}")


step 4

nano reducer.py


#!/usr/bin/env python3
import sys
from collections import defaultdict

current_key = None
a_vals = defaultdict(float)
b_vals = defaultdict(float)

def emit_result(key, a_vals, b_vals):
    total = 0
    for k in a_vals:
        if k in b_vals:
            total += a_vals[k] * b_vals[k]
    print(f"{key}\\t{total}")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    key, val = line.split("\\t")
    if key != current_key and current_key is not None:
        emit_result(current_key, a_vals, b_vals)
        a_vals.clear()
        b_vals.clear()

    current_key = key
    tag, k, v = val.split(",")
    k = int(k)
    v = float(v)

    if tag == "A":
        a_vals[k] = v
    elif tag == "B":
        b_vals[k] = v

if current_key is not None:
    emit_result(current_key, a_vals, b_vals)



step 5


hadoop fs -mkdir /input

step 6

nano input.txt


step 7


A,0,0,1
A,0,1,2
A,1,0,3
A,1,1,4
B,0,0,5
B,0,1,6
B,1,0,7
B,1,1,8



step 8


hadoop fs -put -f input.txt /input


step 9

hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar   -input /input   -output /output_mat_5   -mapper mapper.py   -reducer reducer.py


step 10 

hadoop fs -ls /output_mat_5


step 11

hadoop fs -cat /output_mat_5/part-00000""")

