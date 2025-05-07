code = '''
1. su hduser
   cd

2. start-dfs.sh
   start-yarn.sh
   jps

3. hdfs dfs -mkdir -p /input
   hdfs dfs -ls /

4. nano weather_data.txt

5. hdfs dfs -put weather_data.txt /input/

6. nano mapper.py
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
                print(f"{year} {min_temp} {max_temp}")


   nano reducer.py
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


   chmod +x mapper.py
   chmod +x reducer.py

7. whereis hadoop
   hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.4.jar \
   > -input /input/weather_data.txt \
   > -output /output/weather_output \
   > -mapper mapper.py \
   > -reducer reducer.py \
   > -file mapper.py \
   > -file reducer.py

8. hdfs dfs -ls /output/weather_output/
   hdfs dfs -cat /output/weather_output/part-00000
'''

print(code)