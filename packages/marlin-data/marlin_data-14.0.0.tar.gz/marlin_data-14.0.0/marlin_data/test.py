## 
# ===================================================
# | Acoustic Data Download / Local load and Pipeline Test          |
# ===================================================
#
#
#  c. Rahul Tandon, 2024, RSA 2024 
##



# Inlcude required modules
from datetime import datetime, timedelta
import pickle
import sys
sys.path.append('../marlin_data/marlin_data')
from marlin_data import *

# Specify file locations
# -- folder for test data
simulation_data_path = "/home/vixen/rs/data/acoustic/test_dl"

# -- folder for signature (verification data)
signature_data_path = "/home/vixen/rs/data/acoustic/ellen/raw_repo/hp/sig"

# location must be an array or list of locations
location = ['brixham']

# Init data adapter (marlin adapter)
data_adapter = None
data_adapter = MarlinData(load_args={'limit' : 1})

data_feed_ = None

# download test routine
def download():

    # Download data and store locally
    #   -params-
    #   simulation_path : path to save serial data to locally
    #   limit : max number of downlaods
    #   location : location of hydrophone (must be an array)
    
    data_adapter.download_simulation_snapshots(load_args={'simulation_path':simulation_data_path, 'location':location})



def load():
    # Load data into the marlin data adapter from a local source
    #   -params-
    #   load_path : path to local rep of serial data
    #   limit : max number of downlaods
    #   snapshot_type : type of snapshot [ simulation | signature ]
   
    global data_adapter
    r = data_adapter.load_from_path(load_args={'load_path' : simulation_data_path, "snapshot_type":"simulation", "limit" : 1})



def build_feed():
    # Having downloaded and loaded data locally, we can now initialise the data adapter with the data and 
    # feed data to our optimisation framework via our marlin data feed.

    # Build the MARLIN data feed
    global data_feed_
    print ("Initialising data feed.")
    data_feed_ = MarlinDataStreamer()
    
    # initilise the simulation datafeeder with downloaded data in data_adapter
    data_feed_.init_data(data_adapter.simulation_data, data_adapter.simulation_index)
    


print ("Loading data.")
load()
print ("Building data feed.")
build_feed()

#----------------------
#
# Using Derived Data Structures
#
#----------------------

data_adapter.build_derived_data(n_fft=8192)

for snapshot in data_feed_:
    s_id = snapshot.meta_data['snapshot_id']
    print (f'Building derived data feed structure {s_id}')

    snapshot_derived_data = data_adapter.derived_data.build_derived_data(simulation_data=snapshot, sample_delta_t=1.0)
    with open(f'{s_id}_.der', 'wb') as f:  # open a text file
        pickle.dump(snapshot_derived_data, f) # serialize the list
    
#----------------------
#
# Pipeline of Derived Data into Simple World
#
#----------------------

listen_delta_t = 1 # seconds

for generation_number in range(0,100):

    for individual_idx in range(0, 100):
        
        #init time & index counters
        listen_start_idx = 0
        listen_end_idx = 0
        
        for env_pressure in data_feed_:
            listen_delta_idx = listen_delta_t * env_pressure.meta_data['sample_rate']
            env_pressure_length = env_pressure.frequency_ts_np.shape[0]
            
            while listen_start_idx < env_pressure_length:
               
                # --- get start & end slice idx ---
                listen_end_idx = listen_start_idx + listen_delta_idx
                slice_start = listen_start_idx
                slice_end = min(listen_end_idx,env_pressure_length-1)
                
                # --- get datetime ---
                _s = (slice_start / env_pressure.meta_data['sample_rate']) * 1000 # ms 
                iter_start_time =  env_pressure.start_time + timedelta(milliseconds=_s)
                _s = (slice_end / env_pressure.meta_data['sample_rate']) * 1000
                iter_end_time   =  env_pressure.start_time + timedelta(milliseconds=_s)
                
                
                # --- data input to world ---
                print (f'{iter_start_time} : {iter_end_time}')
                print (f'[{slice_start}:{slice_end}]')
                
                # - query 1 [frames,[dB]] at time (nb. search whole snapshot )
                # energy_value = 0
                # energy_value = data_adapter.derived_data.query_energy_frames_at_time(iter_start_time, env_pressure)
                # print (energy_value[1])
                
                # - query 2 [frames,[dB]] at frequency (nb. search whole snapshot )
                # energy_value = 0
                # energy_value = data_adapter.derived_data.query_energy_frames_at_frequency(120, env_pressure)
                # print (energy_value[1])
                
                # - query 3 [frames,[dB]] at frequency bounds and time (opt) (nb. search whole derived dataset )
                # energy_value = 0
                # energy_value = data_adapter.derived_data.query_energy_frames_at_frequency_bounds(0,120,iter_start_time )
                # print (energy_value[1])
                
                # - query 4 [frames,[dB]] at time bounds (nb. search whole derived dataset )
                # energy_value = 0
                # energy_value = data_adapter.derived_data.query_energy_frames_at_times_bounds(iter_start_time, iter_end_time )
                # print (energy_value[1])
                
                # - query 5 [frames,[dB]] at time AND frequency bounds (nb. search whole derived dataset )
                # energy_value = 0
                # energy_value = data_adapter.derived_data.query_energy_frequency_time_bounds(iter_start_time, iter_end_time, 0, 200 )
                # print (energy_value[1])
                
                
                
                # update listen start idx
                listen_start_idx = listen_end_idx



