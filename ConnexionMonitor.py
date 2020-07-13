# Monitors the download speed & ping of a connection.
# Computer must be online when the script is launched

import speedtest as st
import pandas as pd
import time
import datetime
import logging
import os

# Getting the path to folder where the script is stored
script_folder = os.path.dirname(__file__)

# Initializing logging
logging.basicConfig(filename=script_folder+'/ConnexionMonitorLog.log',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

# Initializing result dataframe & output location
results_log_df = pd.DataFrame()

# Initializing the speedtest target server (one in Bordeaux)
logging.info('New session started')
logging.info('Speedtest initialization...')
servers = [29542]
threads = None

# Declaring the dummy df that will be appended whenever the connection drops
dummy_result_df = pd.json_normalize(
    {'download': 0,
     'upload': 0,
     'ping': None,
     'server': {
         'url': None,
         'lat': None,
         'lon': None,
         'name': None,
         'country': None,
         'cc': None,
         'sponsor': None,
         'id': None,
         'host': None,
         'd': None,
         'latency': None
     },
     'timestamp': None,
     'bytes_sent': None,
     'bytes_received': None,
     'share': None,
     'client': {
         'ip': None,
         'lat': None,
         'lon': None,
         'isp': None,
         'isprating': None,
         'rating': None,
         'ispdlavg': None,
         'ispulavg': None,
         'loggedin': None,
         'country': None
     }
    }
)

while True:
    try:
        s = st.Speedtest()
        s.get_servers(servers)

        logging.info('Testing download speed...')
        s.download(threads=threads)

        logging.info('Testing upload speed...')
        s.upload(threads=threads)

        # s.results.share()  # Results can be "shared" with speedtest.net, generating a neat png
        test_results_df = pd.json_normalize(s.results.dict())

        timestamp = test_results_df['timestamp'][0]
        download = test_results_df['download'][0]/1000000
        upload = test_results_df['upload'][0]/1000000
        ping = test_results_df['ping'][0]

        logging.info(f'Result : {download} Mbps descending, {upload} Mbps ascending, latency of {ping} ms')

    except st.ConfigRetrievalError:
        logging.info('There seems to be a problem with the connection!')
        test_results_df = dummy_result_df
        test_results_df['timestamp'] = '%sZ' % datetime.datetime.utcnow().isoformat()

    logging.info('Appending results and writing output data to CSV file...')
    results_log_df = results_log_df.append(test_results_df, ignore_index=True)
    # Append results to output CSV file, only writing headers if the output file doesn't already exist.
    results_log_df.to_csv(script_folder+'/ConnexionMonitorResults.csv',
                          decimal=",",
                          mode='a',
                          header=not os.path.exists(script_folder+'/ConnexionMonitorResults.csv'),
                          index=False)

    logging.info('Waiting 1 minute...')
    time.sleep(60)
