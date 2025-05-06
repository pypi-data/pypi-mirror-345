code = '''
a) Character counting in a given text file

1. su hduser
   cd

2. nano word_count.txt

3. start-dfs.sh
   start-yarn.sh
   jps

4. hdfs dfs -ls /
   hdfs dfs -rm -r /input
   hdfs dfs -mkdir -p /input
   hdfs dfs -put word_count.txt /input/

5. whereis hadoop
   hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount /input /output

6. hdfs dfs -ls /output/
   hdfs dfs -cat /output/part-r-00000

*************************************************************************************************************************

b) Counting no. of occurrences of every word in a given text file.

1. su hduser
   cd

2. start-dfs.sh
   start-yarn.sh
   jps

3. hdfs dfs -mkdir -p /input
   hdfs dfs -ls /

4. nano character_count.txt

5. hdfs dfs -put character_count.txt /input/

6. nano mapper.py
    #!/usr/bin/env python3
    import sys
    for line in sys.stdin:
        for char in line.strip():
            print(f"{char}\t1")

   nano reducer.py
    #!/usr/bin/env python3
    import sys
    from collections import defaultdict
    counts = defaultdict(int)
    for line in sys.stdin:
        key, val = line.strip().split("\t")
        counts[key] += int(val)
    for key in sorted(counts):
        print(f"{key}\t{counts[key]}")

   chmod +x mapper.py
   chmod +x reducer.py

7. whereis hadoop
   hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.4.jar \
   > -input /input/character_count.txt \
   > -output /output/character_output \
   > -mapper mapper.py \
   > -reducer reducer.py \
   > -file mapper.py \
   > -file reducer.py

8. hdfs dfs -ls /output/character_output/
   hdfs dfs -cat /output/character_output/part-00000

'''
print(code)
