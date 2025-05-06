# pmeter
A python tool that measures the tcp and udp network metrics

## CSE-603 PDP Project
#####Contributors
Deepika Ghodki
Aman Harsh
Neha Mishra
Jacob Goldverg

#### Links to Relevant Papers
1. [Historical Analysis and Real-Time Tuning](https://cse.buffalo.edu/faculty/tkosar/papers/jrnl_tpds_2018.pdf)
2. Cheng, Liang and Marsic, Ivan. ‘Java-based Tools for Accurate Bandwidth Measurement of Digital Subscriber Line Networks’. 1 Jan. 2002 : 333 – 344.
3. [Java-based tools for accurate bandwidth measurement of Digital Subscriber Line](https://www.researchgate.net/publication/237325992_Java-based_tools_for_accurate_bandwidth_measurement_of_Digital_Subscriber_Line)
4. [Energy-saving Cross-layer Optimization of Big Data Transfer Based on Historical Log Analysis](https://arxiv.org/pdf/2104.01192.pdf)
5. [Cross-layer Optimization of Big Data Transfer Throughput and Energy Consumption](https://par.nsf.gov/servlets/purl/10113313)
6. [HARP: Predictive Transfer Optimization Based on Historical Analysis and Real-time Probing](https://cse.buffalo.edu/faculty/tkosar/papers/sc_2016.pdf)

#### The Problem
Currently, the OneDataShare Transfer-Service do not collect/report(to AWS deployment) the network state they experience. Tools such as "sar" and "ethtool" report metrics like: ping, bandwidth, latency, link capacity, RTT,, etc to the user that allow them to understand bottlenecks in their network.

#### Metrics we collect
1. Kernel Level: 
   * active cores
   * cpu frequency
   * energy consumption
   * cpu Architecture 
2. Application Level: 
   * pipelining
   * concurrency
   * parallelism
   * chunk size
3. Network Level:
   * RTT
   * Bandwidth 
   * BDP(Link capacity * RTT)
   * packet loss rate
   * link capacity
4. Data Characteristics: 
   * Number of files
   * Total Size of transfer
   * Average file size
   * std deviation of file sizes
   * file types in the transfer
    
End System Resource Usage: 
   * % of CPU’s used 
   * % of NIC used.

#### Solution
We initially explored three soultions and we have decided solution 1 would be sufficient and provide accurate enough metrics.

Solution 1. Writing a Python script which the Transfer-Service will run as a CRON job to collect the network conditions periodically. The script will create a file that will be formatted metric report, and the Transfer-Service will then read/parse that file and send it to CockroachDB/Prometheous that will be run on the AWS backend

The current state of the project is we have a python script that supports: kernel, and some network level metrics. The script generates a a file in the users home directory under ~/.pmeter/pmeter_measure.txt, this file stores a json dump of the ODS_Metrics object inside of the file. The cli is able to run for a number of measurements or a certain amount of time.
Every "row" of the file is a new ODS_Metrics object that stores a new measurement. This file then gets parsed and cleaned up as the Transfer-Service reads from it and appends its own data to the object(file count, types of files,,, etc)then proceeds to store the data in InfluxDB/CockroachDB. 

The aggregator service is a publisher to InfluxDB and has 
The aggregator service is a service running in the OneDataShare (ODS) VPC which summarizes and computes the data so we can perform some visualization. We currently have a graph being generated with one metric(latency) and we will now begin to explore ML.

###### Recap
Before we began exploring ML models we began by breaking down the problems which we are attempting to solve again. 
1. What parameters(concurrency, pipelining, parallelism, and chunk size) are optimal for performing a big data file transfer?
2. What is the given network condition that a host is experiencing?

###### The Data:
The current data we are generating is what is commonly refereed to as "Time-Series Data". InfluxDb defines this type of data as "Time series data, also referred to as time-stamped data, is a sequence of data points indexed in time order. Time-stamped is data collected at different points in time.". It is essentially data that represents a snapshot of time for something, this something in our case in the kernel/network conditions that the Operating System is experiencing.

##### Example Graphs
![Latency and CPU Frequency](/docs/images/Screenshot%202022-03-28%20at%2011.14.05%20AM.png "Latency and CPU Frequency")
![RTT](/docs/images/Screenshot%202022-03-28%20at%2011.14.13%20AM.png "RTT")
![RTT Over Time](/docs/images/Screenshot%202022-03-28%20at%2011.15.09%20AM.png "RTT Over Time")
![Example Query](/docs/images/Screenshot%202022-03-28%20at%2011.15.54%20AM.png "Example Query")

#### Challenges per Solution

Solution 1: We currently expect the actual metrics to not be as accurate as the manual implementation on the Java application. As UDP/TCP are dynamic we know that having separate connections(python sockets vs java sockets) will create variability in the measurements. Another source of variability is using another programming language will only provide an estimation of what the Transfer-Service is experiencing in performance as the Java is completely virtualized. 
The benefit of this approach is that Python has many libraries more network measuring libraries.

1. Bandwidth is still only realizable bandwidth for the ODS Transfer-Service.
2. Ping traditionally uses ICMP which requires a high level of permissions, so if the process is not able to run ICMP ping then we use TCP ping which is less accurate but better than nothing.
3. We are still observing the difference between CDB and InfluxDB in terms of extrapolating data. We currently fully support both database types and are now attempting to swell the DB and see how performance is.

#### TO-DO
1. Run the cli on DTN on CCR for 1 week to gather some data.
2. Explore various regressions that would let us extrapolate relationships in values.
3. Create a set of graphs(with types) to generate to summarize the conditions the host is going through over time.


#### Libraries to be used per solution
ping: will allow measurement of packet loss and latency
psutil: A networking library that exposes kernel/os level metrics.
statsd: A library that allows us to construct concise reports for sending to AWS.
influxdb: A Time series database that allows us to store and generate trivial graphs.

Solution 1. tcp-latency, udp-latency, ping, psutil(Exposes: CPU, NIC metrics) allows us to compute RTT, Bandwidth, estimated link capacity.

##### List of Technologies
Tools: ping, psutil,
Technologies: Java, Python, CockroachDB, Prometheus, Grafana

#### What we will Accomplish
By the end of the semester we would like to have the transfer service to be fully monitoring its network conditions and reporting it periodically back to the ODS backend.
We will be using either CockroachDB or Prometheus to be storing the time-series data thus allowing the ODS deployment to optimize the transfer based on the papers above.
For extra browny points we would like to implement a Grafana dashboard so every user can be aware of the network conditions around their transfer.

#### What we have accomplished
1. We have a CLI that captures the kernel, and network parameters that the OS exposes to the application layer
2. We have a time series DB(InfluxDB) which allows us to store and manipulate the time 

#### References
1. 
