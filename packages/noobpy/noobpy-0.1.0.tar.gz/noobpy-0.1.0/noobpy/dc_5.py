print("""

# mapper.py


#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    parts = line.split()
    if len(parts) == 3:
        date_str, min_temp, max_temp = parts
        if "-" in date_str:
            year = date_str.split("-")[0]
            print(f"{year}\t{min_temp} {max_temp}")


# reducer.py

#!/usr/bin/env python3
import sys
from collections import defaultdict

temps_by_year = defaultdict(list)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    parts = line.split()
    if len(parts) != 3:
        continue

    year, min_temp, max_temp = parts
    try:
        temps_by_year[year].append((int(min_temp), int(max_temp)))
    except:
        continue

for year in sorted(temps_by_year.keys()):
    mins, maxs = zip(*temps_by_year[year])
    print(f"{year}\t{min(mins)}\t{max(maxs)}")



# steps

su hduser

start-dfs.sh
start-yarn.sh
jps

hdfs dfs -mkdir -p /input
hdfs dfs -ls /

nano weather_data.txt

Year,Month,Day,Max Temp (°C),Min Temp (°C),Rainfall (mm)
1950,01,01,25,-18,43
1950,01,02,26,-17,44
1950,01,03,27,-12,32
1950,01,04,28,-20,41
1950,01,05,29,-13,40
1950,01,06,30,-16,45
1950,01,07,31,-14,33
1950,01,08,32,-19,38
1950,01,09,33,-20,28
1950,01,10,34,-19,40


hdfs dfs -put weather_data.txt /input/
hdfs dfs -ls /input/


nano mapper.py
nano reducer.py
chmod +x mapper.py
chmod +x reducer.py



hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.4.jar \
-input /input/weather_data.txt \
-output /output \
-mapper mapper.py \
-reducer reducer.py


hdfs dfs -ls /output


hdfs dfs -cat /output/part-00000


""")
