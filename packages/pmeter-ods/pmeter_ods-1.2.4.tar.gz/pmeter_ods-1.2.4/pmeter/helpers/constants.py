class NetworkMetrics:
    BANDWIDTH="bandwith"
    PACKET_LOSS="packet_loss"
    LINK_CAPACTITY="link_capacity"
    ROUND_TRIP_TIME="round_trip_time"
    BANDWIDTH_DELAY_PRODUT="bandwidth_delay_product"

class KernelMetrics:
    ACTIVE_CORES="active_cores"
    CPU_FREQUENCY="cpu_frequency"
    ENERGY_CONSUMPTION="energy_consumption"
    CPU_ARCHITECTURE="cpu_architecture"
    NETWORK_CARD_USAGE="nic_usage"
    CPU_USAGE="cpu_usage"

#Found this function here https://www.admin-magazine.com/HPC/Articles/Process-Network-and-Disk-Metrics
def bytes2human(n):
       # From sample script for psutils
   """
   >>> bytes2human(10000)
   '9.8 K'
   >>> bytes2human(100001221)
   '95.4 M'
   """
   symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
   prefix = {}
   for i, s in enumerate(symbols):
      prefix[s] = 1 << (i + 1) * 10
   for s in reversed(symbols):
      if n >= prefix[s]:
         value = float(n) / prefix[s]
         return '%.2f %s' % (value, s)
   return '%.2f B' % (n)

#Found this here to convert HH:MM:SS to seconds https://stackoverflow.com/questions/6402812/how-to-convert-an-hmmss-time-string-to-seconds-in-python
def get_sec(time_str):
    print("Parsing time=",time_str, "to seconds")
    """Get seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)