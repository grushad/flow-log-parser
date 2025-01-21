#### Python program that parses flow log and generates an output based on a look up file

Input to program:
* file name of flow logs data
* file name of the look up file
* output file name (optional)

Command to run:

```
python3 flow_log_parser.py lookup_table.csv flow_logs.txt --output output.csv
```

Requirements:
Python3 will be required to run the program.

Code flow:
- Have used the socket module in python to lookup for protocol name and their mapping to number.
- Have created functions to perform various subtasks such as reading the flow log file, reading the lookup table file and then processing the data read from them.

Tests:
- Have added few basic unit tests for the functions that I have created. The tests are not extensive and can be extended to ensure the correctness of our program.

Assumptions:
* Flow log is a txt file and have split based on space, this can be easily changes to csv or any other file type.
* Flow log data is valid; although have added a check if a flow log line has missing destination port/ protocol but haven't added extensive checks.
* Look up table is valid and has all fields populated.
