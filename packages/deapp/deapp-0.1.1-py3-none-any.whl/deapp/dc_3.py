print("""

    # word count

        "1. Switch to the Hadoop user:",
        "   $ su hduser",
        "",
        "2. Create a text file to count words:",
        "   $ nano word_count.txt",
        "   # Add your text in this file",
        "   # Press Ctrl + X, then Y, then Enter to save",
        "",
        "3. Start HDFS and YARN:",
        "   $ start-dfs.sh",
        "   $ start-yarn.sh",
        "",
        "4. Verify services are running (use jps):",
        "   $ jps",
        "",
        "5. Clean old input/output directories if they exist:",
        "   $ hdfs dfs -rm -r /input",
        "   $ hdfs dfs -rm -r /output",
        "",
        "6. Create input directory and upload the text file to HDFS:",
        "   $ hdfs dfs -mkdir -p /input",
        "   $ hdfs dfs -put word_count.txt /input/",
        "   $ hdfs dfs -ls /input/",
        "",
        "7. Run the WordCount program (inbuilt MapReduce job):",
        "   $ hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.*.jar wordcount /input /output",
        "",
        "8. Check the output directory:",
        "   $ hdfs dfs -ls /output/",
        "",
        "9. Display the word count result:",
        "   $ hdfs dfs -cat /output/part-r-00000",
        "",
        "10. Shut down HDFS and YARN:",
        "    $ stop-dfs.sh",
        "    $ stop-yarn.sh"


    # character count


        "1. Switch to the Hadoop user:",
        "   $ su hduser",
        "",
        "2. Start HDFS and YARN:",
        "   $ start-dfs.sh",
        "   $ start-yarn.sh",
        "",
        "3. Verify Hadoop daemons are running:",
        "   $ jps",
        "",
        "4. Create an input directory in HDFS:",
        "   $ hdfs dfs -mkdir -p /input",
        "",
        "5. Create a text file and upload it to HDFS:",
        "   $ nano character_count.txt",

        "   $ hdfs dfs -put character_count.txt /input/",
        "   $ hdfs dfs -ls /input/",
        "",
        "6. Create the Mapper and Reducer scripts:",
        "   $ nano mapper.py",
        "   # Write mapper code, then save",
        "   $ nano reducer.py",
        "   # Write reducer code, then save",
        "   $ chmod +x mapper.py",
        "   $ chmod +x reducer.py",
        "",
        "7. Run the Hadoop streaming job:",
        $ hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.*.jar -input /input/character_count.txt -output /output/character_output -mapper mapper.py -reducer reducer.py
        "",
        "8. View the output:",
        "   $ hdfs dfs -ls /output/character_output/",
        "   $ hdfs dfs -cat /output/character_output/part-00000",
        "",
        "9. Stop Hadoop services:",
        "   $ stop-dfs.sh",
        "   $ stop-yarn.sh"

mapper.py

#!/usr/bin/env python3
import sys

for line in sys.stdin:
    for char in line.strip():
        print(f"{char}\\t1")


reducer.py


#!/usr/bin/env python3
import sys
from collections import defaultdict

counts = defaultdict(int)

for line in sys.stdin:
    key, val = line.strip().split("\\t")
    counts[key] += int(val)

for key in sorted(counts):
    print(f"{key}\\t{counts[key]}")




""")
