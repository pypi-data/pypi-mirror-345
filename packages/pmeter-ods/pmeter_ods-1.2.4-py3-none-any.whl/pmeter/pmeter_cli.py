"""PMeter a tool to measure the TCP/UDP network conditions that the running host experiences

Usage:
  pmeter_cli.py measure <INTERFACE> [-K=KER_BOOL -N=NET_BOOL -F=FILE_NAME -S=STD_OUT_BOOL --interval=INTERVAL --measure=MEASUREMENTS --length=LENGTH --user=USER --file_name=FILENAME --folder_path=FOLDERPATH --folder_name=FOLDERNAME]
  pmeter_cli.py carbon <IP> [--max_hops=<MAX_HOPS> --save_per_ip=<SAVE_PER_IP> --save_time=<TIME> --node_id=<NODE_ID> --job_id=<JOB_ID>]
  pmeter_cli.py traceroute <IP> [--mtr --max_hops=<MAX_HOPS> --save_per_ip=<SAVE_PER_IP> --save_time=<TIME> --node_id=<NODE_ID> --job_id=<JOB_ID>]

Commands:
    measure     The command to start measuring the computers network activity on the specified network devices. This command accepts a list of interfaces that you wish to monitor
    carbon      Measure the carbon footprint from the cli's host to the destination ip

Options:
  -h --help                Show this screen
  --version                Show version
  -N --measure_network     Set if we monitor only the network interface [default: True]
  -K --measure_kernel      Set if we monitor only the kernel [default: True]
  -U --measure_udp         Set UDP monitoring only [default: True]
  -T --measure_tcp         Set TCP monitoring only [default: True]
  -S --enable_std_out      Disable printing the results to standard output [default: False]
  --file_name=FILENAME     Set the file name used to measure [default: pmeter_measure.txt]
  --folder_path=FOLDERPATH Set the path to store the measurement files in the default is the users home directory under
  --folder_name=FOLDERNAME Set the folder name for pmeter to dump data into
  --interval=INTERVAL      Set the time to run the measurement in the format HH:MM:SS [default: 00:00:01]
  --measure=MEASUREMENTS   The max number of times to measure your system. Set this value to 0 to ignore this and use only the length [default: 1]
  --length=LENGTH          The amount of time to run for: 5w, 4d 3h, 2m, 1s are some examples of 5 weeks, 4 days, 3 hours, 2 min, 1 sec. Set this value to '-1s' to ignore this field and use only measurement [default: 10s]
  --user=USER              This will override the user we try to pick up from the environment variable(ODS_USER). If no user is passed then we will not submit the data generated to the ODS backend [default: ]
  --max_hops=MAX_HOPS      The maximum number of hops [default: 64]
  --save_per_ip=SAVE_PER_IP Save carbon intensity per IP address [default: False]
  --save_time=<TIME>        Capture timestamp when taking carbon footprint [default: False]
  --node_id=<NODE_ID>        The node name that is running pmeter [default: ""]
  --job_id=<JOB_ID>         The job id that this measurement is correlated too [default: ""]
  --mtr               Use MTR to generate output, must have mtr installed. [default: False]
"""
import json
import math
import subprocess
from pathlib import Path

import pandas as pd
from docopt import docopt
from scapy.layers.dns import DNS, DNSQR
from scapy.volatile import RandShort

from helpers import constants
from datetime import datetime, timedelta
from helpers.file_writer import ODS_Metrics
import time
import copy
import requests
from pandas import DataFrame, read_json
import os
import scapy.layers.inet as inet

# conf.use_pcap = True
old_measure_dict = {}  # this is hackish but the keyis the interface name and for every metric we run of that interface name we replace and then run


def convert_to_endate(length):
    end_date = datetime.now()
    num = int(length[:-1])
    if "s" in length:
        end_date += timedelta(seconds=num)
    if "m" in length:
        end_date += timedelta(minutes=num)
    if "d" in length:
        end_date += timedelta(days=num)
    if "w" in length:
        end_date += timedelta(weeks=num)
    if "h" in length:
        end_date += timedelta(hours=num)
    return end_date


# run measurement using time only
def measure_using_length(interface_list, metric, folder_path, file_name, folder_name, measure_tcp=True,
                         measure_udp=True, measure_kernel=True, measure_network=True, print_to_std_out=False,
                         latency_host="http://google.com", interval=1, length="0s"):
    end_date = convert_to_endate(length)
    current_date = datetime.now()
    while (current_date < end_date):
        print("Current date is less than end date=", current_date < end_date)
        metric.measure_latency_rtt(latency_host)
        for intr_name in interface_list:
            metric.measure(intr_name, measure_tcp, measure_udp, measure_kernel, measure_network, print_to_std_out,
                           latency_host)
            if intr_name in old_measure_dict:
                metric.do_deltas(old_measure_dict[intr_name])
            old_measure_dict[intr_name] = copy.deepcopy(metric)
            metric.to_file(file_name=file_name, folder_path=folder_path, folder_name=folder_name)
        current_date = datetime.now()
        time.sleep(interval)


def measure_using_measurements(interface_list, metric, folder_path, file_name, folder_name, measure_tcp=True,
                               measure_udp=True, measure_kernel=True, measure_network=True, print_to_std_out=False,
                               latency_host="http://google.com", interval=1, measurement=1):
    for i in range(0, measurement):
        metric.measure_latency_rtt(latency_host)
        print("measurement: ", i)
        for intr_name in interface_list:
            metric.measure(intr_name, measure_tcp, measure_udp, measure_kernel, measure_network, print_to_std_out,
                           latency_host)
            if intr_name in old_measure_dict:
                metric.do_deltas(old_measure_dict[intr_name])
            old_measure_dict[intr_name] = copy.deepcopy(metric)
            metric.to_file(file_name=file_name, folder_path=folder_path, folder_name=folder_name)
        time.sleep(interval)


def begin_measuring(user, folder_path, file_name, folder_name, interface='', measure_tcp=True, measure_udp=True,
                    measure_kernel=True, measure_network=True, print_to_std_out=False, interval=1,
                    latency_host="http://google.com", measurement=1, length="0s"):
    metric = ODS_Metrics()
    metric.set_user(user)
    interface_list = []
    if interface == "all":
        for inter_name in metric.get_system_interfaces():
            interface_list.append(inter_name)
    else:
        interface_list.append(interface)
    if measurement == 0:
        print("Measuring by using the duration specified with interval")
        measure_using_length(interface_list=interface_list, metric=metric, folder_path=folder_path, file_name=file_name,
                             folder_name=folder_name, measure_tcp=measure_tcp, measure_udp=measure_udp,
                             measure_kernel=measure_kernel, measure_network=measure_network,
                             print_to_std_out=print_to_std_out, latency_host=latency_host, interval=interval,
                             length=length)
    if length == '0':
        print("Measuring by using the number of measurments to perform with interval")
        measure_using_measurements(interface_list=interface_list, metric=metric, folder_path=folder_path,
                                   file_name=file_name, folder_name=folder_name, measure_tcp=measure_tcp,
                                   measure_udp=measure_udp, measure_kernel=measure_kernel,
                                   measure_network=measure_network, print_to_std_out=print_to_std_out,
                                   latency_host=latency_host, interval=interval, measurement=measurement)
    else:
        measurements_counter = 0
        end_date = convert_to_endate(length)
        current_date = datetime.now()
        while current_date < end_date and measurements_counter < measurement:
            print("Current date= ", str(current_date), "is less than end date=", str(end_date), " is =",
                  current_date < end_date)
            print("currentMeasurement is less than the max measurements", measurements_counter < measurement)
            for intr_name in interface_list:
                metric.measure(intr_name, measure_tcp, measure_udp, measure_kernel, measure_network, print_to_std_out,
                               latency_host)
                if intr_name in old_measure_dict:
                    metric.do_deltas(old_measure_dict[intr_name])
                old_measure_dict[intr_name] = copy.deepcopy(metric)
                metric.to_file(file_name=file_name, folder_path=folder_path, folder_name=folder_name)
            current_date = datetime.now()
            measurements_counter += 1
            time.sleep(interval)


def run_mtr_with_geolocation(destination, max_hops=30, node_id=None):
    """Run MTR and return formatted report with geolocation"""
    cmd = [
        "mtr",
        "-4",
        "-n",
        "--json",
        "-b",
        "-m", str(max_hops),
        destination
    ]

    # Run MTR command
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    mtr_data = json.loads(result.stdout)

    # Get unique IPs for geolocation
    ips = list({hop["host"] for hop in mtr_data["report"]["hubs"]})
    geo_data = geo_locate_ips(ips)
    geo_map = {item["query"]: item for item in geo_data}

    # Build the output structure
    output = {}

    # Add each hop with IP as key
    for hop in mtr_data["report"]["hubs"]:
        ip = hop["host"]
        output[ip] = {
            "lat": geo_map.get(ip, {}).get("lat"),
            "lon": geo_map.get(ip, {}).get("lon"),
            "rtt": hop["Avg"] / 1000,  # Convert to seconds
            "ttl": hop["count"],
            "loss_pct": hop["Loss%"],
            "sent_packets": hop["Snt"],
            "last_rtt": hop["Last"] / 1000,
            "best_rtt": hop["Best"] / 1000,
            "worst_rtt": hop["Wrst"] / 1000,
            "stddev": hop["StDev"] / 1000,
        }

    # Add metadata
    output.update({
        "time": datetime.now().isoformat(),
        "node_id": node_id if node_id else f"{mtr_data['report']['mtr']['src']}-mtr",
        "job_id": "\"\""
    })

    return output


def traceroute(destination, max_hops=30):
    results = []
    # Plain UDP traceroute (no DNS)
    result, _ = inet.traceroute(
        target=destination,
        maxttl=max_hops,
        l4=inet.UDP(sport=RandShort(), dport=33434)  # Random src port, standard UDP traceroute dst port
    )
    for res in result:
        hop_info = {
            "ip": res[1].src,
            "rtt": res[1].time - res[0].sent_time if hasattr(res[1], "time") else None,
            "ttl": res[0].ttl
        }
        results.append(hop_info)
    return results


def geo_locate_ips(ip_list) -> pd.DataFrame:
    # access_key = os.getenv("GEO_LOCATE_ACCESS_KEY")
    payload = [{"query": ip} for ip in ip_list]
    url = "http://ip-api.com/batch"
    r = requests.post(url=url, json=payload)
    # return read_json(r.json())
    return r.json()


def compute_carbon_per_ip(ip_df, store_format=False, save_time=False, max_retries=10, retry_delay=20):
    auth_token = os.getenv("ELECTRICITY_MAPS_AUTH_TOKEN")
    headers = {'auth-token': str(auth_token)}

    carbon_ip_map = {}
    resp_list = []

    for idx, row in ip_df.iterrows():
        cur_lat = row['lat']
        cur_long = row['lon']
        cur_ip = row['query']

        if math.isnan(cur_lat) or math.isnan(cur_long):
            continue

        params = {'lon': cur_long, 'lat': cur_lat}

        # Retry logic
        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            try:
                resp = requests.get(
                    url="https://api.electricitymap.org/v3/carbon-intensity/latest",
                    params=params,
                    headers=headers
                )

                print(f"IP: {cur_ip} | Status Code: {resp.status_code} | Lat {cur_lat} Lon {cur_long}")
                if resp.status_code == 200:
                    carbon_data_json = resp.json()
                    carbon_intensity = carbon_data_json['carbonIntensity']
                    carbon_ip_map[cur_ip] = {
                        "carbon_intensity": carbon_intensity,
                        "lat": cur_lat,
                        "lon": cur_long
                    }
                    print(f"Lat: {cur_lat} Lon: {cur_long} IP: {cur_ip} CarbonIntensity: {carbon_intensity}")
                    resp_list.append(resp)
                    success = True
                else:
                    print(f"Retry {retry_count + 1}/{max_retries} for IP {cur_ip}")
                    retry_count += 1
                    time.sleep(retry_delay)

            except Exception as e:
                print(f"Error for IP {cur_ip}: {e}")
                retry_count += 1
                time.sleep(retry_delay)

        if not success:
            print(f"Failed to fetch data for IP {cur_ip} after {max_retries} retries.")

    # Compute average carbon intensity
    carbon_intensity_path_total = sum(
        entry['carbon_intensity'] for entry in carbon_ip_map.values()
        if isinstance(entry, dict) and 'carbon_intensity' in entry
    )
    avg_carbon_network_path = carbon_intensity_path_total / len(carbon_ip_map) if carbon_ip_map else 0

    print("Average Carbon cost for network path:", avg_carbon_network_path)
    carbon_ip_map['time'] = datetime.now().isoformat()

    return carbon_ip_map, avg_carbon_network_path


def to_file(data, file_path=None, file_name="carbon_pmeter.txt"):
    if file_path is None:
        file_path = os.path.join(Path.home(), ".pmeter", file_name)
    print(file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    j = json.dumps(data)
    with open(file_path, "a+") as f:
        f.write(j + "\n")


def main():
    arguments = docopt(__doc__, version='PMeter 1.0')
    if arguments['measure']:
        interface = arguments['<INTERFACE>']
        file_name = arguments['--file_name']
        folder_path = arguments['--folder_path']
        folder_name = arguments['--folder_name']
        network_only = arguments['--measure_network']
        kernel_only = arguments['--measure_kernel']
        udp_only = arguments['--measure_udp']
        tcp_only = arguments['--measure_tcp']
        std_out_print = arguments['--enable_std_out']
        interval = arguments['--interval']
        pause_between_measure = constants.get_sec(interval)
        times_to_measure = arguments['--measure']
        lengthOfExperiment = arguments['--length']
        user = arguments['--user']
        if folder_name is None: folder_name = ".pmeter"
        print("Parameters recieved: \n", "interface=", interface, "measure network=", network_only, "measure kernel=",
              kernel_only, "interval between measurements=", pause_between_measure, "times to measure default is 1=",
              times_to_measure, 'file_name=', file_name, 'folder_name=', folder_name, 'folder_path=', folder_path)
        begin_measuring(folder_path=folder_path, folder_name=folder_name, file_name=file_name, user=user,
                        interface=interface, measure_tcp=tcp_only, measure_kernel=kernel_only,
                        measure_network=network_only, measure_udp=udp_only, print_to_std_out=std_out_print,
                        interval=pause_between_measure, length=lengthOfExperiment, measurement=int(times_to_measure))
        print("Done Measuring")

    elif arguments['carbon']:
        store_format = arguments['--save_per_ip']
        save_time = arguments['--save_time']
        node_id = arguments['--node_id']
        job_id = arguments['--job_id']
        traceroute_data = traceroute(arguments['<IP>'], int(arguments['--max_hops']))
        ip_list = []
        for entry in traceroute_data:
            ip_list.append(entry['ip'])
        ip_df = pd.DataFrame(geo_locate_ips(ip_list))
        carbon_ip_map, avg_carbon_network_path = compute_carbon_per_ip(ip_df, store_format=bool(store_format),
                                                                       save_time=bool(save_time))
        print(f"Carbon Ip Map: {carbon_ip_map}")
        carbon_ip_map['node_id'] = node_id
        carbon_ip_map['job_id'] = job_id
        print(f"Store Format: {store_format}")
        for ip_meta in traceroute_data:
            ip = str(ip_meta['ip'])
            rtt = ip_meta['rtt']
            ttl = ip_meta['ttl']
            if ip not in carbon_ip_map: continue
            carbon_ip_map[ip]['rtt'] = rtt
            carbon_ip_map[ip]['ttl'] = ttl

        if bool(store_format):
            to_file(carbon_ip_map, file_name='carbon_ip_map.json')
        else:
            to_file(data={'avgCarbon': avg_carbon_network_path})

    elif arguments['traceroute']:
        use_mtr = arguments.get('--mtr', False)
        ip = arguments['<IP>']
        mh = int(arguments.get('--max_hops', 30))
        if not use_mtr:
            traceroute_data = traceroute(arguments['<IP>'], mh)
            to_file(traceroute_data, file_name='traceroute_map.json')
            print("Resulted saved too: traceroute_map.json")
        else:
            data = run_mtr_with_geolocation(ip, mh, "")
            to_file(data, file_name='mtr_map.json')
            print("Resulted saved too: mtr_map.json")


if __name__ == '__main__':
    main()
