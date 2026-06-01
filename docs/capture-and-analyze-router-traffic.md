## Capture and analyze router traffic

I like to understand the traffic going through my router in order to detect issues like unknown ingress connections or unwanted egress connections

1. curl to capture stream from fritzbox with automatic restart if stream gets broken
2. split the stream into valid pcap files using tcpdump
3. run Suricate on the pcap files to analyze the flows and highlight suspicious activities
4. generate full flow information from the alerts in eve.json
5. ask Claude as network specialist for an opinion
6. enrich the data from various security services and databases
+ plus some housekeeping stuff

Results can be viewed on a webpage
