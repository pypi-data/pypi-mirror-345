print("""step 1

start-dfs.sh
start-yarn.sh

step 2

jps

step 3


nano mapper.py

#!/usr/bin/env python3
import sys

# Input: student_id,subject,marks
for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith("student_id"):
        continue
    student_id, subject, marks = line.split(",")
    print(f"{student_id}\\t{marks}")



step 4

nano reducer.py


#!/usr/bin/env python3
import sys

def get_grade(avg):
    avg = float(avg)
    if avg >= 90:
        return 'A'
    elif avg >= 80:
        return 'B'
    elif avg >= 70:
        return 'C'
    elif avg >= 60:
        return 'D'
    else:
        return 'F'

current_id = None
total = 0
count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    student_id, marks = line.split("\\t")
    marks = float(marks)

    if current_id == student_id:
        total += marks
        count += 1
    else:
        if current_id:
            avg = total / count
            print(f"{current_id}\\t{avg:.2f}\\t{get_grade(avg)}")
        current_id = student_id
        total = marks
        count = 1

# Output for the last student
if current_id:
    avg = total / count
    print(f"{current_id}\\t{avg:.2f}\\t{get_grade(avg)}")




step 5


hadoop fs -mkdir /input

step 6

nano input.txt


step 7

student_id,subject,marks
8018,BI,85
8018,BDA,90
8018,CI,78
8018,DC,93
8028,BI,97
8028,BDA,99
8028,CI,95
8028,DC,90
8032,BI,86
8032,BDA,94
8032,CI,85
8032,DC,96
8034,BI,60
8034,BDA,55
8034,CI,40
8034,DC,40
8095,BI,85
8095,BDA,90
8095,CI,96
8095,DC,97




step 8


hadoop fs -put -f input.txt /input


step 9

hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar   -input /input   -output /output_grades   -mapper mapper.py   -reducer reducer.py


step 10 

hadoop fs -ls /output_grades


step 11

hadoop fs -cat /output_grades/part-00000""")

