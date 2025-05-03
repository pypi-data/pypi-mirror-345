#!/usr/bin/env/pyhton3

"""
Marlin acoustic dataclasses, data adapter, and streamer. 
c. Rahul Tandon, R.S. Aqua, 2024
E: r.tandon@rsaqua.co.uk

=======================================================================
| Sumamry of classes                                                  |
=======================================================================

---SignatureData--- : 
A DataClass that defines the labelled data downloaded. Labelled data is defined as data that has been analysed and annotated. The process of
annotating data is performed using Marlin Ident. SignatureData represents s an acoustic snapshot that has been identified as a legitimate member of a validation dateset.

----SimulationData--- : 
A DataClass that defines all the acoustic data held in the acoustic database. SignatureData represents an acoustic snapshot.

---MarlinData--- :
Responsible for connecting to and downloading data from the acoustic database. 

---MarlinDataStreamer--- :
Initialised with pointer to SimulationData downloaded data and provides the iterable allowing to easily iterate over the downloaded data.


v3.0 - live one
"""

API_VERSION = 1
API_SERVER = "https://vixen.hopto.org"
CONTACT_EMAIL = "r.tandon@rsaqua.co.uk"



# --- NUMBA optimisation ---

from numba import jit, njit, vectorize

# --- module imports ---
import re
import glob
import numpy as np
import pandas as pd
import requests, json
import logging
import time as t
from dotenv import load_dotenv, dotenv_values
import os, sys
from dataclasses import dataclass
import random
from tqdm import tqdm as tq
import scipy
from scipy.stats import norm, kurtosis, entropy
from scipy.stats import rankdata
import antropy as ant
# import antropy as ent
# import ms_entropy as me
import librosa
from datetime import datetime as dt
from datetime import timedelta, timezone
# --- environment setup ---
load_dotenv()
config = dotenv_values("data.env")
# --- logging setup ---
logging.basicConfig(level=logging.CRITICAL)
import pickle
# --- define custom parms ---
api_server = API_SERVER
api_version = API_VERSION
contact_email = CONTACT_EMAIL
import math
import statistics


import matplotlib.pyplot as plt
import threading


from itertools import islice

# from ident_data import IdentData

# Yield successive n-sized
# chunks from l.
def divide_chunks(l, n):
    
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]


# ================================== timers ==================

duration = {}
def startt(name=""):
    duration[name] = t.time()
    
def stopt(desc = "", name="", out=0):
    # print (desc)
    if name == "":
        name = desc
    
    d_ = t.time() - duration[name]
    if out == 1:
        
        print (f'{desc} => {d_} (s)')
    duration[name] = d_

    

# ================================== band pass ==================




'''
Define data classes. 
'''


# for idx in range(0,len(self.time_index_values)-1):
#             # delta_t_ = (abs(avg_frame_t -self.time_index_values[idx]))
#             # delta_t = min(delta_t, delta_t_)
#             # if delta_t == delta_t_:
#             #     msg = f'{avg_frame_t} | {self.time_index_values[idx]} : {self.time_index_values[idx+1]} | {idx} | {delta_t} | {self.time_index_values[idx]} -> {self.time_index_values[idx+1]}'
            
#             #if avg_frame_t >= (self.time_index_values[idx] - timedelta(milliseconds= 1))  and (avg_frame_t< self.time_index_values[idx+1] + timedelta(milliseconds= 1)):
#             if avg_frame_t >= (self.time_index_values[idx])  and (avg_frame_t< self.time_index_values[idx+1] ):
#                 #print (f'time idx : {idx} value : {self.time_index_values[idx]}')
#                 t_index = self.time_index_values[idx]
#                 break


@njit
def get_closest_index_by_positive_value( comp_value : float = None, data_arr = None ):
    
    idx_value = np.argmin(np.abs(data_arr - comp_value))
    return (idx_value)
    
    

@dataclass
class SubDomainFrame:
    """
    Sub domain analysis frame
    - energy profile and stats
   
    """
    frequency_bounds : list[float]
    time_frame : list[dt]
    
    stats : {}
    energy_profile : []


@dataclass
class EnergyFrame:
    """
    Energy data frame. 
   
    """
    
    frequency_bounds : list[float]
    time_frame : list[dt]
    energy_measure : float
    db_measure : float
    id : int
    delta_frequency : float
   
    def __str__(self):
        return (f'{self.frequency_bounds} | {self.time_frame} | {self.energy_measure}')
       
   
   
@dataclass
class SignatureData:
    """
    Signature dataclass. Define acoustic waveform as a numpy array and pandas dataframe. Dataclass defines a acoustic
    snapshot. meta_data defines snapshot.
    """    

    frequency_ts_np : np.array                  # waveform as numpy array
    frequency_ts_pd : pd.DataFrame              # waveform as dataframe
    meta_data : None                            # snapshot definition
    snapshot : bool = True  
    energy_data : list[EnergyFrame]  = None
    start_time : dt = None
    end_time : dt = None
    
    
@dataclass
class SimulationData:
    """
    Signature dataclass. Define acoustic waveform as a numpy array and pandas dataframe. Dataclass defines a acoustic
    snapshot. meta_data defines snapshot.
    """   
     
    frequency_ts_np : np.array                  # waveform as numpy array
    frequency_ts_pd : pd.DataFrame              # waveform as dataframe
    meta_data : None                             # snapshot definition
    snapshot : bool = True
    energy_data : list[EnergyFrame]  = None
    start_time : dt = None
    end_time : dt = None
    

@dataclass
class Multithread:
    """
    Multithread dataclass. Defines data required for multithread compatibility.

  
    """
    mt_snapshot_ids : {}
    number_threads  : int
    
    

'''
Define Classes
'''


class MarlinData(object):
    
    """
    Class to connect and download data from acoustic database.
    """    
    
    def __init__(self, load_args : {} = {}):
        """
        Initialise class object.

        Args:
            load_args (dict, optional): Initialisation arguments : 'limit' | max number of downloads . Defaults to {}.
        """          
    
        self.snapshot_ids = []              # list of signature snapshot ids
        self.sim_snapshot_ids = []          # list of sim snapshot ids
        self.run_ids = []                   # list of run ids
        self.signature_ids = []             # list of signature ids
        self.number_runs = 0                # number of runs in signature data
        self.number_signatures = 0          # number of signatures in data set
        self.number_snapshots = 0           # number of sig snapshots      
        self.number_sim_snapshots = 0       # number of sim snapshots

        self.signature_data = {}            # signature data. Dictionary of SignatureData.
        self.signature_index = []           # index of signature id required as keys
        self.simulation_data = {}           # simulation data. Dictionary of SimulationData.
        self.simulation_index = []          # index of simulation id require as keys
        
        # define default limit
        
        if 'limit' in load_args:
            self.limit_sig = load_args['limit']
        else:
            self.limit_sig = 5
    
        self.derived_data = None
        self.multiple_derived_data = {}
        
        # snapshot already downloaded. Required for single downloads in large batch
        self.downloaded_snapshots = []
    
    def init_multithread(self, number_threads, load_args):
        """
        Initialise multithread data. Returns array of snapshot ids discretised into number of threads which can 
        be loaded for download.

        Args:
            number_threads (_type_): _description_
            load_args (_type_): _description_

        Returns:
            _type_: _description_
        """
        
        snapshot_endpoint = "data/snapshot/data/all"
        api_url = f"{api_server}/rs/api/v{api_version}/{snapshot_endpoint}"
        
        try:
            r = requests.get(api_url) 
            request_json_data_signature = r.json()['data']
            # number_r = len(request_json_data_signature)
            
        except Exception as ex:
            logging.critical(f"[marlin_data.py] Unable to run signature retrieval api request. Email {contact_email} | {ex}")

        
        # download_limit = number_r // number_threads
        download_cnt = 0
        thread_counter = 0
        snapshot_id_holder = {}
        snapshot_id_list = []
        number_r = 0
        for snapshot in request_json_data_signature:
            
           
            if 'location' in load_args:
                if snapshot['data_receiver_location_name'] in load_args['location']:
                    number_r += 1
                    snapshot_id_list.append(snapshot['ss_id'])
                    
        
        download_limit = number_r // number_threads
        snapshot_id_list_mt = []
        for snapshot_id in snapshot_id_list:   
            snapshot_id_list_mt.append(snapshot_id)
            download_cnt += 1
            if download_cnt >= download_limit:
                download_cnt = 0
                snapshot_id_holder[thread_counter] = snapshot_id_list_mt
                thread_counter += 1
                
        return_data = Multithread(snapshot_id_holder, thread_counter)
        return return_data
             
    def download_signature_snapshots(self, load_args : {} = {}) -> ({}):
        
        if 'limit' in load_args:
            self.limit_sig = load_args['limit']
        """Load binary data from RSA server and load into corresponding dataclasses.

        Args:
            load_args (dict, optional): Load arguments. E.g.location contraints. Defaults to {}.

        Returns:
            {}, [] | {key : snapshot_id , value : signature dataclass} , [snapshot_id]
        """   
        
        signature_enpoint = "data/signature"
        api_url = f"{api_server}/rs/api/v{api_version}/{signature_enpoint}"
        
        try:
            r = requests.get(api_url) 
            request_json_data_signature = r.json()['data']

        except Exception as ex:
            logging.critical(f"[marlin_data.py] Unable to run signature retrieval api request. Email {contact_email} | {ex}")

        for signature in request_json_data_signature:
            
             
          
            if signature['snapshot_id'] not in self.snapshot_ids:
                self.snapshot_ids.append(signature['snapshot_id'])
                
            if signature['run_id'] not in self.run_ids:
                self.run_ids.append(signature['run_id'])
                
            if signature['signature_id'] not in self.signature_ids:
                self.signature_ids.append(signature['signature_id'])
            
        
       
        # limit_sig = 5
        limit_sig_cnt = 1
        
        for snapshot_id in self.snapshot_ids:
            
            if limit_sig_cnt > self.limit_sig:
                break
            # -- 
            # We have the signature id now and require snapshot data in order to build metadata, e.g. delta t, time and location id.
            # We now grab all the meta data for the signature
            # --
           
            
            # get the snapshot id of the snapshot xr with signature
            # snapshot_id = signature['snapshot_id']
            snapshot_id = snapshot_id            
            #define API endpoint & url
            snapshot_data_signature_enpoint = "data/snapshot/data"
            snapshot_data_signature_url = f"{api_server}/rs/api/v{api_version}/{snapshot_data_signature_enpoint}/{snapshot_id}"
            # print (snapshot_data_signature_url)
            
            
            # make api request
            try:
                
                r_ss = requests.get(snapshot_data_signature_url) 
                request_json_data_snapshot = r_ss.json()['data'][0]
                
                #---
                # Filter Snapshots
                #---
                
                if 'ss_ids' in load_args:
                    if request_json_data_snapshot['ss_id'] not in load_args['ss_ids']:
                        continue
                
                if 'location' in load_args:
                    # print (signature)
                    
                    #print (request_json_data_snapshot['data_receiver_location_name'], load_args['location'])
                    if request_json_data_snapshot['data_receiver_location_name'] not in load_args['location']:
                        
                        continue
            
               
                
                # print (request_json_data_snapshot)
                meta_data = self.parse_meta(snapshot_data = request_json_data_snapshot)
                
                
            
                
            except Exception as ex:
                logging.debug(f"[marlin_data.py - 2] Unable to run snapshot data retrieval api request. Email {contact_email} | {ex}")
    
            # --
            # Get serial data : meta data complete, download and convert the stored serial data
            # --
            
            #define API endpoint & url
            snapshot_data_signature_enpoint = "data/snapshot/serialdata"
            snapshot_serial_data_url = f"{api_server}/rs/api/v{api_version}/{snapshot_data_signature_enpoint}/{snapshot_id}"
            
            # make api request & load
            try:
                
                r_serial = requests.get(snapshot_serial_data_url) 
                
                request_json_serial_data = r_serial.json()['data'][0]
                
                if 'signature_path' not in load_args.keys():
                    
                    load_args['signature_path'] = ""
                
                domain_data_np, domain_data_pd = self.deserial_data(raw_data = request_json_serial_data['json_raw'], path=load_args['signature_path'], meta_data = meta_data)
                # meta_data = self.parse_meta(snapshot_data = request_json_data_snapshot)
                
                
                sim_data = SignatureData(frequency_ts_np = domain_data_np, frequency_ts_pd = domain_data_pd, meta_data = meta_data)
                
                
              
                self.signature_data[snapshot_id] = sim_data
                
                self.signature_index.append(snapshot_id)
                limit_sig_cnt += 1
                
                
                
                # if domain_data_np or domain_data_pd == None:
                #     logging.debug(f"[marlin_data.py -3] {snapshot_id} Empty serial data file for snapshot raw data.Email {contact_email} ")
                    
                
            except Exception as ex:
                logging.debug(f"[marlin_data.py - 5] Unable to run snapshot data retrieval api request. Email {contact_email} | {ex}")
    
            

        # set length parameters
        self.number_runs = len(self.run_ids)
        self.number_snapshots = len(self.snapshot_ids)
        self.number_signatures = len(self.signature_index)
        
        return self.signature_data, self.signature_index
             
    def download_simulation_snapshots(self, load_args = {},clear=False, id_only = False) -> ({}):
        
        """Load binary data from RSA server and load into corresponding dataclasses.

        Args:
            load_args (dict, optional): _description_. Defaults to {}.

        Returns:
            {}, []: {key : snapshot_id , value : simulation dataclass} , [snapshot_id]
        """   
        
        
        
        if clear == True:
            # self.sim_snapshot_ids = []
            self.downloaded_snapshots = []
        
        sim_id_tracker = []
        if 'limit' in load_args:
            self.limit_sig = load_args['limit']
        
        # print ('downloadng')
        # print (load_args)
        
        
        for location in load_args['location']:
            # print (location)
            snapshot_endpoint = f'data/snapshot/data/all/{location}'
            api_url = f"{api_server}/rs/api/v{api_version}/{snapshot_endpoint}"
            
            request_json_data_snapshots = None
            try:
                r = requests.get(api_url) 
                
                request_json_data_snapshots = r.json()['data']
                
            except Exception as error:
                logging.critical(f"{error}")
                logging.critical(f"[marlin_data.py] Unable to run all snapshots retrieval api request. Email {contact_email}")
            
            
            if request_json_data_snapshots == None:
                return {0 : "No Data"}
            
            limit_sig_cnt = 1
            for snapshot in request_json_data_snapshots:
                if limit_sig_cnt > self.limit_sig:
                
                    break
                # --
                # Build tag and id trackers for data object
                # --
                # logging.debug(load_args['ss_ids'])
                
                # logging.debug(f'ss_id{snaphsot['ss_id']}')
                # Filter---
                
                if 'ss_ids' in load_args:
                    if snapshot['ss_id'] not in load_args['ss_ids']:
                        
                        continue
                if 'location' in load_args:
                    
                    if snapshot['data_receiver_location_name'] not in load_args['location']:
                        
                        continue
                    
                if 'time_start' in load_args:
                    
                   
                    
                    db_ts = snapshot['data_frame_start']
                    timeframe_start = f'{db_ts} UTC'
                    snapshot_dt_start = dt.strptime(timeframe_start, '%y%m%d_%H%M%S.%f %Z')
                    snapshot['dt_start_frame_time'] = snapshot_dt_start
                    
                    db_te = snapshot['data_frame_end']
                    timeframe_end = f'{db_te} UTC'
                    snapshot_dt_end = dt.strptime(timeframe_end, '%y%m%d_%H%M%S.%f %Z')
                    snapshot['dt_end_frame_time'] = snapshot_dt_end
                   
                    constraint_start_str = load_args['time_start']
                    constraint_start = f'{constraint_start_str} UTC'
                    constraint_dt_start = dt.strptime(constraint_start, '%y%m%d_%H%M%S.%f %Z')
                    
                    constraint_end_str = load_args['time_end']
                    constraint_end = f'{constraint_end_str} UTC'
                    constraint_dt_end = dt.strptime(constraint_end, '%y%m%d_%H%M%S.%f %Z')
                    
                    # print (constraint_dt_start)
                    
                    if constraint_dt_start > snapshot_dt_end:
                        continue
                    
                    
                    if constraint_dt_end < snapshot_dt_start:
                        continue
                    
                    # print (timeframe_start, timeframe_end)
                    tracker = {'id' : snapshot['ss_id'], 'start_time' : snapshot_dt_start}
                    sim_id_tracker.append(tracker)
                    
                # ----
                
                if snapshot['ss_id'] not in self.sim_snapshot_ids:
                    self.sim_snapshot_ids.append(snapshot['ss_id'])
                    limit_sig_cnt += 1
                # if snapshot['run_id'] not in self.run_ids:
                #     self.sim_run_ids.append(signature['run_id'])
                    
            
            
        if id_only:
            
            #order by time ascending
           
            sim_id_tracker_sorted = sorted(sim_id_tracker, key=lambda x: x['start_time'])
            print ("Returning sim ids only.")
            return (sim_id_tracker_sorted)
           
            
            
        for snapshot_id in self.sim_snapshot_ids:
           
            # -- 
            # We have the signature id now and require snapshot data in order to build metadata, e.g. delta t, time and location id.
            # We now grab all the meta data for the signature
            # --
            
            if snapshot_id in self.downloaded_snapshots:
                continue
            
            # get the snapshot id of the snapshot xr with signature
            # snapshot_id = signature['snapshot_id']
            snapshot_id = snapshot_id            
            #define API endpoint & url
            snapshot_data_signature_enpoint = "data/snapshot/data"
            snapshot_data_signature_url = f"{api_server}/rs/api/v{api_version}/{snapshot_data_signature_enpoint}/{snapshot_id}"
            
            
            # make api request
            try:
                r_ss = requests.get(snapshot_data_signature_url) 
                request_json_data_snapshot = r_ss.json()['data'][0]
                
                #filter location
                
                    
                
                meta_data = self.parse_meta(snapshot_data = request_json_data_snapshot)
               
            except Exception as ex:
                logging.critical(f"[marlin_data.py - 2] Unable to run snapshot data retrieval api request. Email {contact_email} | {ex}")
    
            # --
            # Get serial data : meta data complete, download and convert the stored serial data
            # --
            
            #define API endpoint & url
            snapshot_data_signature_enpoint = "data/snapshot/serialdata"
            snapshot_serial_data_url = f"{api_server}/rs/api/v{api_version}/{snapshot_data_signature_enpoint}/{snapshot_id}"
            
            # make api request
            try:
                
                r_serial = requests.get(snapshot_serial_data_url)
                try: 
                    request_json_serial_data = r_serial.json()['data'][0]
                    
                except Exception as ex:
                    logging.critical(f'Exception raised: {ex}')
                    continue
                
                if "success" in r_serial.json()['data'][0]:
                    continue
                    
                if 'simulation_path' not in load_args.keys():
                    load_args['simulation_path'] = ""
                
                domain_data_np, domain_data_pd = self.deserial_data(raw_data = request_json_serial_data['json_raw'], path=load_args['simulation_path'],meta_data= meta_data)
                
                signature_frame_start_dt = dt.strptime(meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
                signature_frame_end_dt = dt.strptime(meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
               
                sig_data = SimulationData(frequency_ts_np = domain_data_np, frequency_ts_pd = domain_data_pd, meta_data = meta_data)
                sig_data.start_time = signature_frame_start_dt
                sig_data.end_time = signature_frame_end_dt
                self.simulation_data[snapshot_id] = sig_data
                self.simulation_index.append(snapshot_id)
                # if domain_data_np or domain_data_pd == None:
                #     logging.debug(f"[marlin_data.py -3] {snapshot_id} Empty serial data file for snapshot raw data.Email {contact_email} ")
                    
                
                
                self.downloaded_snapshots.append(snapshot_id)
            except Exception as ex:
                logging.critical(f"[marlin_data.py - 5] Unable to run snapshot data retrieval api request. Email {contact_email} | {ex}")
    

        # set lenght parameters
        self.number_sim_snapshots = len(self.sim_snapshot_ids)
        
        return self.simulation_data, self.simulation_index
    
    def get_track_data(self, mmsi : int = 0, lander_loc : str = "", approach_radius : float =0.0, start_time : str = "", end_time : str = ""):
        '''
            Get a list of snapshot ids from mmsi of vessel. approaches. Check validity and XR with existing data. Use Marlin API
        '''
        
        self.approaches = []
        
        lander_pos = {}
        lander_pos['netley'] = {'lat' : 50.871, 'long' : -1.373}
        lander_lat = lander_pos[lander_loc]['lat']
        lander_long = lander_pos[lander_loc]['long']
        
        url = f'https://vixen.hopto.org/rs/api/v1/data/ships/tracks/{mmsi}/target_known/{lander_lat}/{lander_long}/{approach_radius}'
        
        track_data = None
        try:
            r = requests.get(url) 
            track_data = r.json()
            number_approaches = track_data['number_of_approaches']
            number_tracks = track_data['number_tracks']

        except Exception as ex:
            logging.critical(f"[marlin_data.py] Unable to run signature retrieval api request. Email {contact_email} : {ex}")

        # for each approach create a vector of snapshot ids.
        for approach_id in range(0,number_approaches):
            
            start_time = track_data['approach_profiles'][approach_id][0]['time']
            end_time = track_data['approach_profiles'][approach_id][len(track_data['approach_profiles'][approach_id])-1]['time']
            
            session_id = random.randrange(0,99999)
            
            post_data = {
                "start_time": start_time,
                "end_time": end_time,
                "location": lander_loc,
                "session_id": session_id,
                "track": "true"
            };
           
            
        
            valid_url =url = "https://vixen.hopto.org/rs/api/v1/data/valid/"
            valid_r = requests.post(valid_url, json.dumps(post_data)) 
            valid_data = valid_r.json()
            snapshot_ids = valid_data['snapshot_ids']
            percent_cover = min(valid_data['percentage_complete'], 100)
            
            # build approach profile data
            approach_profile = track_data['approach_profiles'][approach_id]
            
            
            
            self.approaches.append({'snapshot_ids' : snapshot_ids, 'percent_cover' : percent_cover, 'mmsi' : mmsi, 'approach_profile' : approach_profile})

        return self.approaches
    
    def get_ident_research_link(self, target_time, location, name, position, uid):
        # 2024-09-11T22:59:56.200427Z from decisions
        link_str = ""
        
        application_id = random.randint(0,9999)
        
        target_time_dt = dt.strptime(target_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        start_time_dt = target_time_dt - timedelta(seconds=600)
        end_time_dt = target_time_dt + timedelta(seconds=600)
        
        url_start_time = start_time_dt.strftime("%Y/%m/%d %H:%M:%S")
        url_end_time = end_time_dt.strftime("%Y/%m/%d %H:%M:%S")
        
        link_str = f'https://vixen.hopto.org/rs/ident_app/ident_gui/index.php?application_id={application_id}&location_value={location}&start_time={url_start_time}&end_time={url_end_time}&name={name}&uid={uid}&position={position}&level=10'
        return link_str
    
    def get_snapshots(self, start_time : str = "", end_time : str = ""):
        pass
    
        #  var valid_ids = [];
        # var valid_snapshots = [];

        # for (var i = 0; i < this.snapshot_ids.length; i++) {
        #     var snap = this.snapshots[this.snapshot_ids[i]];

        #     var snap_start_t = snap.timeframe_start_ms;
        #     if ((snap_start_t >= start_time_ms) && (snap_start_t < end_time_ms)) {
        #         console.log(snap);
        #         valid_ids.push(this.snapshot_ids[i]);
        #     }
        # }

        # for (var i = 0; i < valid_ids.length; i++) {
        #     valid_snapshots.push(this.snapshots[valid_ids[i]]);
        # }
        
        # for sim_data in self.simulation_index:
        #     print (self.simulation_data[sim_data])
        
        
        
        
    
    
    def parse_meta(self, snapshot_data : {} = None) -> {}:
        
        """
        Parse query return of snapshot data into metadata

        Returns:
            {}: MetaData of snapshot.
        """        
        
        meta_data = {}
        meta_data['snapshot_id '] = snapshot_data['ss_id']
        meta_data['snapshot_id'] = snapshot_data['ss_id']
        meta_data['data_frame_start'] = snapshot_data['data_frame_start']
        meta_data['data_frame_end'] = snapshot_data['data_frame_end']
        meta_data['listener_location'] = snapshot_data['data_receiver_location']
        meta_data['location_name'] = snapshot_data['data_receiver_location_name']
        meta_data['frame_delta_t'] = snapshot_data['data_delta_time']
        meta_data['sample_rate'] =  snapshot_data['sample_rate']
        
        start_t_dt = dt.strptime(meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
        marlin_start_time = start_t_dt.timestamp()
        
        end_t_dt = dt.strptime(meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
        marlin_end_time = end_t_dt.timestamp()
        
        meta_data['marlin_start_time'] =  int(start_t_dt.timestamp()) * 1000
        meta_data['marlin_end_time'] =  int(end_t_dt.timestamp()) * 1000
        
        #meta_data['marlin_end_time'] = 
        #print (meta_data['data_frame_start'])
        return meta_data
    
    def load_from_path(self, load_args : {} = None):
        # print (load_args)
        load_limit = 5
        load_cnt = 1
        sim_ids = []
        id_filter = False
        if 'limit' in load_args.keys():
            load_limit = load_args['limit']
        
        if 'ss_ids' in load_args.keys():
            id_filter = True
            sim_ids = load_args['ss_ids']
        
        path = load_args['load_path']
        files = glob.glob(f'{path}/*')
        # print (files)
        pat = r'.*\_(.*)\..*'    
        processed_snapshots = []
        snapshot_times = {}
        number_files =  0
        for file in files:
            
            np_data, pd_data, c = (None, None, None)
            
            search_result = re.match(pat, file)
            if search_result == None:
                continue
            snapshot_id = search_result.group(1)
            # print (path)
            # print (snapshot_id)
        
            data_filepath = f'{path}/streamedfile_{snapshot_id}.dat'
            # print (data_filepath)
            
            metadata_filepath = f'{path}/metadata_{snapshot_id}.json'
            
            
            
            if snapshot_id not in processed_snapshots:
                if id_filter:
                    if snapshot_id not in sim_ids:
                        continue    
                processed_snapshots.append(snapshot_id)
                try:
                    with open(data_filepath, 'rb') as fr:
                        c = fr.read()
                    np_data = None
                    pd_data = None 
                    dtype = np.dtype("float32")
                    np_data  = np.frombuffer(c, dtype=dtype)
                    pd_data = pd.DataFrame(np_data)
                    fr.close()
                    
                    with open(metadata_filepath, 'rb') as fr:
                        meta_data = json.load(fr)
                    
                    
                    
                    
                    # time considerations
                    start_t_dt = dt.strptime(meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
                    snapshot_times[start_t_dt] = snapshot_id
                    
                    end_t_dt = dt.strptime(meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
                    #print (meta_data['data_frame_end'], end_t_dt)
                   
                
                    
                    if ('marlin_start_time' not in meta_data):
                        meta_data['marlin_start_time'] =  int(start_t_dt.timestamp()) * 1000
                    
                    if ('marlin_end_time' not in meta_data):
                        meta_data['marlin_end_time'] =  int(end_t_dt.timestamp()) * 1000
                    
                    if load_args['snapshot_type'] == "simulation":
                        
                        sig_data = SimulationData(frequency_ts_np = np_data, frequency_ts_pd = pd_data, meta_data = meta_data, start_time=start_t_dt, end_time=end_t_dt)
                        self.simulation_data[snapshot_id] = sig_data
                        # self.simulation_index.append(snapshot_id)
                        
                    else:
                        
                        sig_data = SignatureData(frequency_ts_np = np_data, frequency_ts_pd = pd_data, meta_data = meta_data,  start_time=start_t_dt, end_time=end_t_dt)
                        self.signature_data[snapshot_id] = sig_data
                        # self.signature_index.append(snapshot_id)
            
                except Exception as ex:
                    print(ex)
                    
                load_cnt += 1
                # if load_cnt >= load_limit:
                #     break
            number_files += 1
        # rearrange index vector wrt time
        
        
        # self.simulation_index = []
        # self.signature_index = []
        
        dates_sorted = sorted(snapshot_times.keys())
        # print (f'{number_files} loaded.')
        # print (f'load limit {load_limit}')
        for time_ in dates_sorted[0:load_limit]:
            
            if load_args['snapshot_type'] == "simulation":
                
                snapshot_id = snapshot_times[time_]
                self.simulation_index.append(snapshot_id)
                
                
                
            if load_args['snapshot_type'] == "signature":
                snapshot_id = snapshot_times[time_]
                self.signature_index.append(snapshot_id)
                
        res = {}
        
        
        if load_args['snapshot_type'] == "simulation":
            
            _num = len(self.simulation_index)
            # print (f'{_num} snapshots loaded. Limit : {load_limit}')
            _times = len(snapshot_times.keys())
            _ss = len(self.simulation_data.keys())
            # print (f'{_times} | {_ss}')
            res['number snapshots'] = _ss
            res['number times'] = _times
            res['index size'] = _num
        # for id, time in snapshot_times.items():
        #     print (time)
        
        if load_args['snapshot_type'] == "signature":
            _num = len(self.signature_index)
            # print (f'{_num} snapshots loaded. Limit : {load_limit}')
            _times = len(snapshot_times.keys())
            _ss = len(self.signature_data.keys())
            # print (f'{_times} | {_ss}')
            res['number snapshots'] = _ss
            res['number times'] = _times
            res['index size'] = _num
        
        
        
        return res
    
    def build_game(self):
        """
            Add signature / labelled data to the simulation mix in order to ensure we have labelled data in the simulation.
        """
        # --- add siganture snapshots to simulation game if not already present
        for sig_snap_id in self.signature_index:
            if sig_snap_id  not in self.simulation_index:
                self.simulation_index.append(sig_snap_id)
                self.simulation_data[sig_snap_id] = self.signature_data[sig_snap_id]
        
        # --- re order snapshot ids into chronological order
        snapshot_times = {}
        for snapshot in self.simulation_index:
            # print (self.simulation_data[snapshot])
            start_t_dt = dt.strptime(self.simulation_data[snapshot].meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
            snapshot_times[start_t_dt] = self.simulation_data[snapshot].meta_data['snapshot_id']
        
        
        dates_sorted = sorted(snapshot_times.keys())
        # clear index
        self.simulation_index = []
        # rebuild index
        
        for time_ in dates_sorted:
            snapshot_id = snapshot_times[time_]
            self.simulation_index.append(snapshot_id)
            
        # print (self.simulation_index)
     
    def deserial_data(self, raw_data : {} = None, path : str = "", meta_data : {} = None) -> (np.array, pd.DataFrame):
        """
        Read/stream remote serial data and load into a readable format / data structure.

        Args:
            raw_data from a snapshot data query from Marlin API

        Returns:
            np.array, pd.DataFrame
        """        
        
        np_data, pd_data, c = (None, None, None)
        
        random_tag = meta_data['snapshot_id']
        # pandas_data = None
        # c = None
        if 'raw_data_url' in raw_data:
            
            
            filepath = ""
            if path == "":
                filepath = f'streamedfile_{random_tag}.dat'
                json_filepath = f'metadata_{random_tag}.json'
            else:
                filepath = f'{path}/streamedfile_{random_tag}.dat' 
                json_filepath =  f'{path}/metadata_{random_tag}.json' 

            with open(json_filepath, 'w') as f_:
                json.dump(meta_data, f_)
                print (f'saving download: {filepath}')

            serial_domain_data_fn = raw_data['raw_data_url']
            #print (f'grabbing from [{serial_domain_data_fn}]')
            r = requests.get(serial_domain_data_fn, allow_redirects=True, stream=True)
            
            total_length = r.headers.get('content-length')
            
            print (f"[Marlin Data : Fetching binary data : {serial_domain_data_fn}]")
           
            # f = open(f'streamed_file{random_tag}', 'wb')
            f = open(filepath, 'wb')
            dl = 0
            total_length = int(total_length)
            
            for data in r.iter_content(chunk_size=2000):
                dl += len(data)
                f.write(data)
                done = int(50* dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
                sys.stdout.flush()

            sys.stdout.flush()

            
            # with open(f'streamed_file{random_tag}', 'rb') as fr:
            #     c = fr.read()
            with open(filepath, 'rb') as fr:
                c = fr.read()
                
            dt = np.dtype("float32")
            np_data  = np.frombuffer(c, dtype=dt)
            pd_data = pd.DataFrame(np_data)
            fr.close()

            
        return np_data, pd_data
      
    def build_derived_data(self, n_fft : int = 1024):
        self.derived_data = MarlinDerivedData(n_fft=n_fft)



class MarlinDataStreamer(object):
    """
    Class to connect to MarlinData and provide an iterable for data access.

    
    """   
    def __init__(self):
       
        self.data_feed = {}
        self.data_ids = []
        self.feed_index = -1
        self.data_vec_length = 0
    
    def init_data(self, data_feed : {} = {}, data_ids : [] = []) -> None:
        """_summary_

        Args:
            data_feed ({}, optional): Dataclass structure and key. Defaults to {}.
            data_ids ([], optional): keys. Defaults to [].
        """        
        # initiaslise vector of feed epoch ids
        self.data_ids = data_ids
        
        # initialise the feed dataset
        self.data_feed = data_feed
        
        # determine lenght of data feed
        self.data_vec_length = len(self.data_ids)
        
        # start data feed
        self.feed_index = 0
        
    def get_data(self, data_idx : int = 0):
        return self.data_feed[data_idx]
    
    def __iter__(self):
        return self
        
    def __next__(self):
      
        if self.feed_index >= self.data_vec_length:
            
            self.feed_index = 0
            raise StopIteration
        
        feed_value = self.data_feed[self.data_ids[self.feed_index]]
        self.feed_index += 1
        return feed_value


    #---
    # Filters
    #---

    def init_snapshots_time(self, time_of_interest : dt, search_seconds : int):
        """
        Filter data stream by a time of interest.

        Args:
            time_of_interest (dt): time of interest
            search_seconds (int): buffer time for data stream

        Returns:
            int: 1 for success
        """        
        filtered_data = {}
        filtered_index = []
        
        search_seconds_dt = timedelta(seconds = search_seconds)
        
        
        for key_value in self.data_ids:
        
            # for key_value, data_inst in self.data_feed.items():
            
            data_inst = self.data_feed[key_value]
            
            data_time = data_inst.start_time
        
            delta_time = abs(time_of_interest - data_time).total_seconds()
            # print(f'{data_time} | {time_of_interest} | {delta_time}')
            # if delta_time < search_seconds_dt:
            if delta_time<float(search_seconds):
                
                filtered_data[key_value] = data_inst
                filtered_index.append(key_value)
        
        # set feed to filtered data
        self.init_data(filtered_data, filtered_index)
        
        
        return 1

class MarlinDerivedData(object):
    
    def __init__(self, n_fft : int = 2048):
        """
        Initialise Class

        Args:
            n_fft (int, optional): Fourier frame size. Defaults to 1024.
        """
        self.n_fft = n_fft  
        self.energy_frames = []                         # global energy_frames
        self.sample_times = []                          # sample times from fft
        self.model_sample_times = []                    # sample times for model
        self.data_start_time = None                     # time bounds for data
        self.data_end_time = None                       # time bounds for data
        self.number_energy_frames = 0                   # number of energy data frames
       
        self.labelled_data = {}                         # data_structure to xr labelled data with
        
        self.sub_domain_frames = []
        self.power_spectrum = {}
        
        self.fast_index_energy_stats = {}               # frequency bound indexing for optimised energy data
        
        self.spectral_entropy_across_time = {}          # temportal spectral e across all t bins for a f index
        self.spectral_entropy_across_freq = {}          # temportal spectral e across all f bins for a t index
        self.spectral_entropy_f_t = {}
        
        self.fourier = None
        self.fourier_delta_t = 0
        self.fourier_delta_f = 0 
        self.index_delta_t = 0
        self.index_delta_f = 0
        
        self.min_freq = 0
        
        self.spectral_entropies = {}
        self.discretised_source_data = {}
        
    
    
    def build_discretised_data(self):
        pass
    
    def build_derived_data(self, simulation_data : SimulationData = None, f_min : int = 0, f_max : int = 1000, indexing = False):
        """
        

        Args:
            signature_data (SignatureData, optional): _description_. Defaults to None.
        """
        
        '''
        Build derived data from raw energy time series. 
        1. perform fft on dataset -> f and t bins
        '''
        
     
        self.sample_rate = simulation_data.meta_data['sample_rate']
        
        # --- run sft on data --
        raw_data = simulation_data.frequency_ts_np
        # print (raw_data)
        #--- gain ---
        # raw_data_ = raw_data * 40 
        # print (raw_data_)
        
        hop_length = self.n_fft // 2
        # logging.critical(f'{raw_data}')
        # startt(name="fft_it")
        # op_data = IdentData(data_source=raw_data)
        # op_data.fft_it()
        # stopt(desc="fft_it", out=1)
        
        # startt(name="fit")
        # op_data = IdentData(data_source=raw_data)
        # s = op_data.fft_it()
        # stopt(desc="fft_it", out=1)
        
        # startt(name="fft_it")
        # op_data = IdentData(data_source=raw_data)
        # s = op_data.fft_it()
        # stopt(desc="fft_it", out=1)
        
        # self.n_fft = len(raw_data)
        
        startt(name="lib_fft")
        s = np.abs(librosa.stft(raw_data, n_fft=self.n_fft, hop_length=hop_length))
        # stopt(desc="lib_fft", out=1)
        
        # print (s.shape)
        # print (s[300][2])
        D = s
        
        self.fourier = s
        
        # fft_r = np.abs(librosa.stft(raw_data_, n_fft=self.n_fft, hop_length=hop_length))
        # print (fft_r)
        
        #D = librosa.amplitude_to_db(np.abs(librosa.stft(raw_data_, n_fft=self.n_fft, hop_length=hop_length)), ref=np.max)

        # energy = D[300, 2]
        # print (energy)
        
        # --- get frequemcies and time ranges ---
        startt(name="t_bins")
        librosa_time_bins = librosa.frames_to_time(range(0, D.shape[1]), sr=simulation_data.meta_data['sample_rate'], hop_length=(self.n_fft//2), n_fft=self.n_fft)
        # stopt(desc="t_bins", out=1)
        # print (simulation_data.meta_data['sample_rate'])
        # print (librosa_time_bins)
        # print (f'nfft : {self.n_fft}')
        startt(name="f_bins")
        librosa_f_bins = librosa.core.fft_frequencies(n_fft=self.n_fft, sr=simulation_data.meta_data['sample_rate'])
        # stopt(desc="f_bins", out=1)
        # self.min_f = librosa_f_bins[0]
        # self.max_f = librosa_f_bins[len(librosa_f_bins)-1]
        self.librosa_time_bins=  librosa_time_bins
        # print (self.librosa_time_bins)
      
        self.librosa_f_bins = librosa_f_bins
        df = librosa_f_bins[2]-librosa_f_bins[1]
        dti = librosa_time_bins[2] - librosa_time_bins[1]
       
        
        self.fourier_delta_t = dti
        self.fourier_delta_f = df
        
        self.dt = dti
        
       
        print (f'delta_t = t: {self.fourier_delta_t} | f : {self.fourier_delta_f}')

        # time considerations
        signature_frame_start_dt = dt.strptime(simulation_data.meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
        signature_frame_end_dt = dt.strptime(simulation_data.meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
       
        # marlin_sample_time_dt = timedelta(seconds = marlin_sample_time)
        
        simulation_data.start_time = signature_frame_start_dt
        simulation_data.end_time = signature_frame_end_dt
        
        
        
        # --- build time reference vector
        librosa_time_bins_dt = list (map(lambda v : signature_frame_start_dt +  timedelta(seconds=v), librosa_time_bins))
        # print (librosa_time_bins)
        # for i in range(1,len(librosa_time_bins)):
        #     print (librosa_time_bins[i]-librosa_time_bins[i-1])
        
        #print (librosa_time_bins_dt)
        
        # librosa_time_bins_dt.sort()
        self.sample_times.extend(librosa_time_bins_dt) 
        self.sample_times.sort()
        self.data_start_time = self.sample_times[0]
        self.data_end_time = self.sample_times[len(self.sample_times)-1]
        # self.build_sample_time_vector(librosa_time_bins)
        # self.sample_times = list(map(lambda i, v : signature_frame_start_dt + timedelta(seconds=((v[i]-v[i-1])/2)),enumerate(librosa_time_bins[1:len(librosa_time_bins)])))
        # self.sample_times = list (map(lambda v : (v[1]-v, enumerate(librosa_time_bins)))
        # # --- build energyframes ---
        
        self.fft_times = []
        
        # iterate over time bins and build energy datastructures
        self.max_freq = f_max
        self.min_freq = f_min
        self.max_energy = 0
        self.delta_frequency = 0
        energy_frames = []
        _id = 0
        
        number_fourier_point = 0
        
        # duration = len(custom_waveform)/sample_rate
        # n = len(raw_data)
        # Y = np.fft.fft(raw_data)/self.n_fft # dft and normalization
        # Y = Y[:n//2]
        # self.power_spectrum = Y
        
        # power spectrum
        # print ("Building power spectrum")
        # average over file
        # D_AVG = np.mean(self.fourier, axis=1)
        # print (D_AVG)
        
        # print (len(self.librosa_f_bins))
        # print (len(D_AVG))
        
        # plt.plot(self.librosa_f_bins[5:],D_AVG[5:],color='green', linewidth=0.5, markersize=0.5)
        # plt.xlabel('f (Hz)')
        # plt.ylabel('Amplitude')
        # plt.title("Waveform")
        # plt.savefig(f'test_plot.png')
        # plt.close() 
        # discretised power spectrumhjui  
        
        
        # ---- DISCRETISED DATA ---------------------------------------------
        self.power_rankings = {}
        self.discretised_power_spectrum = []
        self.discretised_perm_entropy = []
        self.discretised_spectral_entropy = []
        self.discretised_time_index = []
        self.sorted_frequencies = []
        self.discretised_psd = []
        # delta_index = math.floor(int(self.sample_rate) * 0.1)
        delta_index = min(int(self.sample_rate * 0.5), len(raw_data))
        
        # print (self.sample_rate)
        current_idx = 0
        end_idx = delta_index
        discrete_number = 0
        elapsed_s = 0
        
        while current_idx < len(raw_data):
            
            lcl_power_rankings = []
            dim = len(raw_data[current_idx:end_idx])
            
            da = raw_data[current_idx:end_idx]
            dim = len(da)
            
            s_ = np.abs(librosa.stft(da, n_fft=dim, hop_length=(dim//2)))
            s_db = librosa.power_to_db(s_**2, ref=np.max)
            
            # time indexing
            self.discretised_time_index.append(elapsed_s)
            
            # power spectrum
            f_power_vector = np.mean(s_, axis=1)
            self.librosa_f_discrete_bins = librosa.core.fft_frequencies(n_fft=dim, sr=self.sample_rate)
            self.librosa_time_disrete_bins = librosa.frames_to_time(range(0, s_.shape[1]), sr=self.sample_rate, n_fft=dim,  hop_length=(dim//2))
            self.discretised_power_spectrum.append(f_power_vector)
            
            # sorted frequencies
            sorted_indeces = np.argsort(f_power_vector)
            sorted_indeces = sorted_indeces[::-1]
            sorted_frequencies = self.librosa_f_discrete_bins[sorted_indeces]
            self.sorted_frequencies.append(sorted_frequencies)
            
            # perm entropy (interesting for regime change)
            perm_ent = ant.perm_entropy(raw_data[current_idx:end_idx], normalize=True)
            self.discretised_perm_entropy.append(perm_ent)
            
            # spectral entropy (interesting for regime change)
            spec_ent = ant.spectral_entropy(raw_data[current_idx:end_idx], sf=self.sample_rate, method='welch', normalize=True)
            self.discretised_spectral_entropy.append(spec_ent)
            
            # power density specrtum
            psd = scipy.signal.periodogram(raw_data[current_idx:end_idx], fs=self.sample_rate)
            self.discretised_psd.append(psd)
            
            
            
            
            # update counters
            discrete_number +=1     
            current_idx = end_idx
            end_idx = current_idx + delta_index   
            elapsed_s += ((end_idx - current_idx) / self.sample_rate) 
        
       
        
       
        
        if indexing:
        
        #! ======================== INDEXING ================================
            self.max_freq = 0 # reset for indixing
            tmp_power_vector = []
            for freq_idx in range(1,len(librosa_f_bins)-1):
                # print (librosa_f_bins[len(librosa_f_bins)-1])
                tmp_energy = 0
                tmp_counter = 0
                
                if ((librosa_f_bins[freq_idx]>= f_min) and (librosa_f_bins[freq_idx] <= f_max)):
                    self.max_freq = max(self.max_freq, librosa_f_bins[freq_idx] )
                    self.min_freq = min(self.min_freq, librosa_f_bins[freq_idx] )
                    
                    for sample_time_idx in range(0, len(librosa_time_bins)-1):
                        number_fourier_point+=1
                        energy = D[freq_idx, sample_time_idx]
                        
                        #decibal conversion
                        db = 20 * math.log10(abs(energy))
                        
                        tmp_energy+=tmp_energy + energy
                        tmp_counter += 1
                        self.max_energy = max(self.max_energy, energy)
                        
                        sample_time_start = signature_frame_start_dt + timedelta(seconds=librosa_time_bins[sample_time_idx])
                        # sample_time_end = signature_frame_start_dt + timedelta(seconds=librosa_time_bins[sample_time_idx+1])
                        sample_time_end = sample_time_start + timedelta(seconds=self.fourier_delta_t)
                        self.fft_times.append(sample_time_start)
                        # create energy frame
                        delta_f = librosa_f_bins[freq_idx] - librosa_f_bins[freq_idx-1]
                        self.delta_frequency = delta_f
                        ef = EnergyFrame(frequency_bounds=[librosa_f_bins[freq_idx-1], librosa_f_bins[freq_idx]], time_frame=[sample_time_start, sample_time_end], energy_measure=energy, id=_id, delta_frequency = delta_f, db_measure= db)
                        
                        # add energy frame to list of energy frames
                        energy_frames.append(ef)
                        self.energy_frames.append(ef)
                        _id += 1 
                    
                    avg_energy = tmp_energy/tmp_counter
                    tmp_power_vector.append(avg_energy)
            
            
            # for ef in self.energy_frames:
            #     print (ef.frequency_bounds[0], ef.time_frame[0])
                
            self.number_energy_frames = len(energy_frames)
            
            number_freq_frames = len(self.librosa_f_bins)
            number_time_frames = len(self.librosa_time_bins)
        
            self.power_spectrum[simulation_data.meta_data['snapshot_id']] = tmp_power_vector
            
            # print (tmp_power_vector)
            # print (len(tmp_power_vector))
            # plt.plot(self.librosa_f_bins,tmp_power_vector,color='green', linewidth=0.5, markersize=0.5)
            # plt.xlabel('f (Hz)')
            # plt.ylabel('Amplitude')
            # plt.title("Waveform")
            # plt.savefig(f'test_plot_2.png')
            # plt.close() 
            
            simulation_data.energy_data = energy_frames
            self.number_energy_frames = len(energy_frames)
            
            save_str = {
                'location' :  simulation_data.meta_data['location_name'],
                'snapshot_id' : simulation_data.meta_data['snapshot_id'],
                'meta_data' :  simulation_data.meta_data,
                'enegry_vector' : energy_frames,
                'max_f' : f_max,
                'min_f' : f_min
            }
            
            
            print (f'Size of energy vector = {self.number_energy_frames}')
            
            return save_str
            
    def build_derived_labelled_data(self, signature_data : SignatureData = None):
        """
        Build structure of signature time frames
        nb. resolution will be an issue here.
        This data structure is used to query validity of decision values in optimisation.
        Args:
            signature_data (SignatureData, optional): _description_. Defaults to None.
        """
        # update time frame of signature
        signature_frame_start_dt = dt.strptime(signature_data.meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
        signature_frame_end_dt = dt.strptime(signature_data.meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
        signature_data.start_time = signature_frame_start_dt
        signature_data.end_time = signature_frame_end_dt 
        time_bounds = [signature_data.start_time, signature_data.end_time]
        self.labelled_data[str(signature_data.meta_data['snapshot_id'])] = time_bounds
                
    def build_xr_data(self, user_uid = "", target=""):
        
        """
            Here we download all labelled data required and store it in the labelled data structure. Previously, only ss ids where used, but we can now build the label data structure without ss id.
            Labelled data without ss id is scalable and flexible and the preffered methodology. Need to consider how to build game to confirm valid signature / labelled data in simulation
        """
        
        # request the data from DB and build labelled_data stucture
        signature_enpoint = "data/signature"
        api_url = f"{api_server}/rs/api/v{api_version}/{signature_enpoint}"
        
        try:
            r = requests.get(api_url) 
            request_json_data_signature = r.json()['data']

        except Exception as ex:
            logging.critical(f"[marlin_data.py] Unable to run signature retrieval api request. Email {contact_email} | {ex}")

        # print (request_json_data_signature)
        # print (f'user : {user_uid}')
        for data_row in request_json_data_signature:
            
            label = data_row['label']
            
            if target == "":
                if user_uid == "":
                    
                    start_dt =  dt.fromtimestamp(float(data_row['start_time_ms'])/1000)
                    # print (start_dt)
                    time_bounds = [data_row['start_time_ms'], data_row['end_time_ms'], label]
                    tag = random.random()
                    self.labelled_data[tag] = time_bounds
                else:
                    if data_row['user_uid'] == user_uid:
                        
                        start_dt =  dt.fromtimestamp(float(data_row['start_time_ms'])/1000)
                        # print (start_dt)
                        time_bounds = [data_row['start_time_ms'], data_row['end_time_ms'], label]
                        tag = random.random()
                        self.labelled_data[tag] = time_bounds
            
            else:
                if target == label:
                    if user_uid == "":
                    
                        start_dt =  dt.fromtimestamp(float(data_row['start_time_ms'])/1000)
                        # print (start_dt)
                        time_bounds = [data_row['start_time_ms'], data_row['end_time_ms'], label]
                        tag = random.random()
                        self.labelled_data[tag] = time_bounds
                    else:
                        if data_row['user_uid'] == user_uid:
                            
                            start_dt =  dt.fromtimestamp(float(data_row['start_time_ms'])/1000)
                            # print (start_dt)
                            time_bounds = [data_row['start_time_ms'], data_row['end_time_ms'], label]
                            tag = random.random()
                            self.labelled_data[tag] = time_bounds
                
            
        
        

        logging.info(f"[marlin_data.py]  [1103] XR structure built.")
        
    def build_band_energy_profile(self,sample_delta_t : float = 1000,  simulation_data : SimulationData = None, discrete_size = 200, sort : bool = False):
        """
        

        Args:
            time_start (dt): _description_
            time_end (dt): _description_
            frequency_min (float): _description_
            frequency_max (float): _description_

        Returns:
            _type_: _description_
        """
        
        self.sample_rate = simulation_data.meta_data['sample_rate']
        
        self.delta_t = sample_delta_t
        self.max_energy = 0
        self.min_energy = 1000
        self.max_avg_energy = 0
        
        if sample_delta_t == -1:
            sample_delta_t = self.dt * 3
            print (f'Best temporal resolution mode engaged!')
        
        # print ("Building Energy Profiles")
        
        # iterate over f buckets
        frequency_bound_lower = self.min_freq
        # print (f'min f : {frequency_bound_lower}')
        # time considerations
        signature_frame_start_dt = dt.strptime(simulation_data.meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
        signature_frame_end_dt = dt.strptime(simulation_data.meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
        marlin_sample_time = sample_delta_t  #seconds
        
        # print (self.min_freq,self.max_freq)
        frequency_bound_index = 0
        
        f_hit = False
        t_hit = False
        # print (f'building for : {frequency_bound_lower}, {self.max_freq}')
        
        frequency_bound_index = 0
        
        entropy_time_tracker = {}
        
        
        while frequency_bound_lower < self.max_freq-100:
            
            discrete_bucket_size = min((self.max_freq-frequency_bound_lower ), discrete_size)
            frequency_bound_upper = frequency_bound_lower + discrete_bucket_size
            active_frequency = (frequency_bound_upper + frequency_bound_lower) / 2
            sample_time_start = signature_frame_start_dt
            
            time_bounds_stats = {}
            power_spec_start_idx  = 0
            total_en = 0
            num_t_bins = 0
            time_bound_index = 0
            while sample_time_start < signature_frame_end_dt: 
                
                
                # print (f'{sample_time_start} of {signature_frame_end_dt}')
                
                
                
                
                
                energy_sum = 0
                energy_frames = []
                energy_profile = []
                max_energy = 0
                min_energy = 1000000000
                
                sample_time_end = sample_time_start + timedelta(seconds=sample_delta_t)
                active_sample_time = sample_time_start + timedelta(seconds=(sample_delta_t/2))
                # get raw power spectrum
                s_r = simulation_data.meta_data['sample_rate']
                power_spec_end_idx  = power_spec_start_idx + round(sample_delta_t * s_r)
                snapshot_power_spectrum = simulation_data.frequency_ts_np
                
                
                #e_n = ent.spectral_entropy(simulation_data.frequency_ts_np[power_spec_start_idx:power_spec_end_idx], s_r, method='fft')
                e_n = ent.spectral_entropy(simulation_data.frequency_ts_np[power_spec_start_idx:power_spec_end_idx], s_r, method='fft', normalize=True)
                total_en = total_en + e_n
                #e_n = me.calculate_spectral_entropy(simulation_data.frequency_ts_np[power_spec_start_idx:power_spec_end_idx])
                # print (simulation_data.frequency_ts_np[int(power_spec_start_idx):int(power_spec_end_idx)])
                # print(simulation_data.frequency_ts_np)
                
                power_spec_start_idx = power_spec_end_idx
                number_t_hits = 0
                number_f_hits =0 
                # print (f'{sample_time_start},{sample_time_end}')
                for energy_data in self.energy_frames:
                    # print (energy_data.frequency_bounds)
                    #print (f'searching: {energy_data.time_frame},{energy_data.frequency_bounds}')
                    # print (energy_data.time_frame[0], sample_time_start)
                    # print (energy_data.time_frame[1], sample_time_end)
                    # print ( energy_data.time_frame[0],  energy_data.time_frame[1])
                    # print (sample_time_start, sample_time_end)
                    # exit()
                    avg_frame_f = (energy_data.frequency_bounds[0] + energy_data.frequency_bounds[1]) /2
                    # if energy_data.time_frame[0] >= sample_time_start and energy_data.time_frame[1] <= sample_time_end:
                    if energy_data.time_frame[0] <= active_sample_time and energy_data.time_frame[1] >= active_sample_time:
                        t_hit = True
                        number_t_hits += 1
                        # print (f'active f {active_frequency}')
                       
                        # print (energy_data.frequency_bounds[0])
                        if avg_frame_f >= frequency_bound_lower and avg_frame_f <= frequency_bound_upper: 
                        # if energy_data.frequency_bounds[0] <= active_frequency and energy_data.frequency_bounds[1] >= active_frequency: 
                            f_hit = True
                            number_f_hits += 1
                            energy_frames.append(energy_data)
                           
                    # if energy_data.time_frame[0] >= sample_time_start and energy_data.time_frame[1] <= sample_time_end:
                    #     t_hit = True
                    #     # print (energy_data.frequency_bounds[0])
                    #     if energy_data.frequency_bounds[0] >= frequency_bound_lower and energy_data.frequency_bounds[1] <= frequency_bound_upper: 
                    #         f_hit = True
                    #         energy_frames.append(energy_data)
                            
                            
                number_hits = len(energy_frames)
                # print(f'number hits: {number_hits}')
                # print(f'number t hits: {number_t_hits}')
                # print(f'number f hits: {number_f_hits}')
                
                if number_hits == 0:
                    
                    print ("err")
                    print (sample_time_start)
                    print (frequency_bound_lower)
                    print (f_hit)
                    print (t_hit)
                    print (energy_data)
                    sample_time_start = sample_time_end
                    print (active_frequency)
                    continue
                
                
                
                f_hit = False
                t_hit = False
                energy_sum = 0
                frequency_counter = {}
                for energy_frame in energy_frames:
                    e = abs(energy_frame.energy_measure)
                    max_energy = max(max_energy, e)
                    min_energy = min(min_energy,e)
                    energy_sum += abs(energy_frame.energy_measure)
                    
                    
                    if frequency_bound_index in frequency_counter:
                        frequency_counter[frequency_bound_index].append(e)
                    else:
                        frequency_counter[frequency_bound_index] = []
                        frequency_counter[frequency_bound_index].append(e)
                        
                
                avg_f = math.floor(energy_frame.frequency_bounds[0] + energy_frame.frequency_bounds[1])/2
                # print(f'sum : {energy_sum}')
                
                
                ind_e_profile = []
                
                v = frequency_counter[frequency_bound_index]
                
                # print (v)
                
                avg_energy  = 0
                harmonic    = 0
                median      = 0
                variance    = 0
                kurtosis_value    = 0
                entropy_value = 0
                
                if (len(v) > 2):
                    avg_energy  = statistics.mean(v)
                    harmonic    = statistics.harmonic_mean(v)
                    median      = statistics.median(v)
                    variance    = statistics.variance(v)
                    kurtosis_value    = kurtosis(v)
                    entropy_value = entropy(v)
                    
                
                stdev = 0
                active_f = avg_f
                if len(v) > 2:
                    stdev = statistics.stdev(v)
                
                stats = {
                    'max_energy'    : max_energy,
                    'min_energy'    : min_energy,
                    'mean_energy'   : avg_energy,
                    'stdev'         : stdev,
                    'variance'      : variance,
                    'kurtosis'      : kurtosis_value,
                    'entropy'       : entropy_value,
                    'spectral_entropy' : e_n,
                    'f' : avg_f
                }
                
                # print (stats)
                # update metrics
                self.max_energy = max(self.max_energy, max_energy)
                self.min_energy = min(self.min_energy, min_energy)
                self.max_avg_energy = max(self.max_avg_energy, avg_energy)
                
                # record subdomain frame
                sub_domain_frame= SubDomainFrame([frequency_bound_lower,frequency_bound_upper],[sample_time_start,sample_time_end],stats, v)
                #print(sub_domain_frame.stats)
                self.sub_domain_frames.append(sub_domain_frame)
                time_bounds_stats[sample_time_start] = sub_domain_frame
                
                if time_bound_index in entropy_time_tracker:
                    entropy_time_tracker[time_bound_index] = entropy_time_tracker[time_bound_index] + e_n
                else:
                    entropy_time_tracker[time_bound_index] = e_n
                    
                sample_time_start = sample_time_end
                time_bound_index += 1
                num_t_bins += 1
                
            
            # entropy across all time
            self.spectral_entropy_across_time[frequency_bound_index] = float(total_en/num_t_bins)
            #print (f'spectral e {self.spectral_entropy[frequency_bound_index]}')
            
           
            
            # print (f'time {sample_time_end} complete')
            # print (f'f {frequency_bound_lower} | index: {frequency_bound_index} complete')
            self.fast_index_energy_stats[frequency_bound_index] = time_bounds_stats
            #print (self.fast_index_energy_stats[frequency_bound_index])
            
            #inrement counters
            frequency_bound_index += 1 
            frequency_bound_lower = frequency_bound_upper
        
        # entropy across all f
        
        for e,v in entropy_time_tracker.items():
            self.spectral_entropy_across_freq[e] = float(v/frequency_bound_index)
            #print (self.spectral_entropy_across_freq[e])
        # self.spectral_entropy_across_freq[frequency_bound_index] = float(total_en/num_f_bins)
        # print (f'spectral e {self.spectral_entropy[frequency_bound_index]}')
        # exit()
              
              
        # convert 
    def ft_build_band_energy_profile(self,sample_delta_t : float = 1000,  simulation_data : SimulationData = None, discrete_size = 200, sort : bool = False):
        """
        

        Args:
            time_start (dt): _description_
            time_end (dt): _description_
            frequency_min (float): _description_
            frequency_max (float): _description_

        Returns:
            _type_: _description_
        """
        self.sample_rate = 1
        self.sample_rate = simulation_data.meta_data['sample_rate']
        self.number_energy_frames_used = 0
        self.delta_t = sample_delta_t
        self.index_delta_t = sample_delta_t
        self.index_delta_f = discrete_size
        print ("Building")
        query_time_start = t.time()
        
        self.max_energy = 0
        self.min_energy = 1000
        self.max_avg_energy = 0
        
        if sample_delta_t == -1:
            sample_delta_t = self.dt * 3
            print (f'Best temporal resolution mode engaged! {sample_delta_t}')
        
        
        # iterate over f buckets
        frequency_bound_lower = self.min_freq
        # print (f'min f : {frequency_bound_lower}')
        # time considerations
        signature_frame_start_dt = dt.strptime(simulation_data.meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
        signature_frame_end_dt = dt.strptime(simulation_data.meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
        marlin_sample_time = sample_delta_t  #seconds
        
        
        # print (f'sig from {signature_frame_start_dt} -> {signature_frame_end_dt}')
        
        
        # print (self.min_freq,self.max_freq)
        frequency_bound_index = 0
        
        f_hit = False
        t_hit = False
        
        frequency_bound_index = 0
        
        entropy_time_tracker = {}
        self.frequency_index_values = {}
        
        # build indexing
        frequency_bound_lower = self.min_freq
        
        startt(name="build_f_skeleton")
        while frequency_bound_lower < self.max_freq:
           
            sample_time_start = signature_frame_start_dt
            frequency_bound_upper = frequency_bound_lower + discrete_size
            self.fast_index_energy_stats[frequency_bound_index] = {}
            self.frequency_index_values[frequency_bound_index] = []
            self.frequency_index_values[frequency_bound_index].append(frequency_bound_lower)
            self.frequency_index_values[frequency_bound_index].append(frequency_bound_upper)
            time_sub_data = {}
            self.time_index_values = []
            while sample_time_start < signature_frame_end_dt: 
                #print (f'active f { sample_time_start}')
                sample_time_end = sample_time_start + timedelta(seconds=sample_delta_t)
                self.time_index_values.append(sample_time_start)
                # build index
                time_sub_data[sample_time_start] = SubDomainFrame([frequency_bound_lower,frequency_bound_upper],[sample_time_start,sample_time_end],{}, [])
                
                sample_time_start = sample_time_end
            
            self.fast_index_energy_stats[frequency_bound_index] = time_sub_data
       
            #inrement counters
            frequency_bound_index += 1 
            frequency_bound_lower = frequency_bound_upper


        # build numba
        # stopt(desc="build_f_skeleton", out=1)
       
        # print ('f index built')
        idx = 0 
        total_e_frames = len(self.energy_frames) 
        
        startt(name="numba_vector_build")
        # convert index data to Numpy for Numba optimisation
        self.time_idx_lookup = {}
        # get the number of f bins
        number_f_index = len(list((self.fast_index_energy_stats.keys())))
        subdomain_vev_length = len(list(self.fast_index_energy_stats[0].keys()))
        # initialise 1D of numpy as empty
        self.f_index_numpy = np.empty([number_f_index,subdomain_vev_length],dtype=int )
        
        
        for freq_indx in range(0,number_f_index):
            time_subdomain_data = self.fast_index_energy_stats[freq_indx]
            # set value of nump
            self.f_index_numpy[freq_indx] = freq_indx
            
            # now for the second dimension. Iterate over the dictionary of subdomain data and add to vector
            # decide what to save in the vector
            
            # print (f'time_idx {subdomain_vev_length}' )
            subdomain_ctr = 0
            for time_start, subdomain in self.fast_index_energy_stats[freq_indx].items():
                # convert time_start from python datetime to ms (int)
                time_start_ms = time_start.timestamp() * 1000
                self.f_index_numpy[freq_indx][subdomain_ctr] = time_start_ms
                if subdomain_ctr not in self.time_idx_lookup:
                    self.time_idx_lookup[subdomain_ctr] = time_start
                subdomain_ctr+=1
                
        # stopt(desc="numba_vector_build", out=1)
        
        # fill indexing
        startt(name="add_to_index")
        
        for energy_data in self.energy_frames:
            startt(name="energy_data_iter")
            status = self.add_to_index(energy_data)
            if (status == 1):
                self.number_energy_frames_used += 1
           
            # print (f'{idx} of {total_e_frames}')
            # stopt(desc="energy_data_iter", out=1)
            remaining_e = len(self.energy_frames) - self.number_energy_frames_used
            time_r = ((len(self.energy_frames) - self.number_energy_frames_used) * duration["energy_data_iter"]) / 60
            # print (f'e remaining : {remaining_e} | energy_time_remaining = {time_r}')
            idx += 1
        
        # stopt(desc="add_to_index", out=1)
        

        
        query_time_end = t.time()
        query_time = query_time_end - query_time_start
        # print (f'frames used : {self.number_energy_frames_used} of {self.number_energy_frames}')
        # print (f'adapter build')
        # print (f'index query time {query_time}')
        
        
        # startt(name="numba_vector_build")
        # # convert index data to Numpy for Numba optimisation
        # self.time_idx_lookup = {}
        # # get the number of f bins
        # number_f_index = len(list((self.fast_index_energy_stats.keys())))
        # subdomain_vev_length = len(list(self.fast_index_energy_stats[0].keys()))
        # # initialise 1D of numpy as empty
        # self.f_index_numpy = np.empty([number_f_index,subdomain_vev_length],dtype=int )
        
        
        # for freq_indx in range(0,number_f_index):
        #     time_subdomain_data = self.fast_index_energy_stats[freq_indx]
        #     # set value of nump
        #     self.f_index_numpy[freq_indx] = freq_indx
            
        #     # now for the second dimension. Iterate over the dictionary of subdomain data and add to vector
        #     # decide what to save in the vector
            
        #     # print (f'time_idx {subdomain_vev_length}' )
        #     subdomain_ctr = 0
        #     for time_start, subdomain in self.fast_index_energy_stats[freq_indx].items():
        #         # convert time_start from python datetime to ms (int)
        #         time_start_ms = time_start.timestamp() * 1000
        #         self.f_index_numpy[freq_indx][subdomain_ctr] = time_start_ms
        #         if subdomain_ctr not in self.time_idx_lookup:
        #             self.time_idx_lookup[subdomain_ctr] = time_start
        #         subdomain_ctr+=1
                
        # stopt(desc="numba_vector_build", out=1)
        
        # print (self.f_index_numpy)
        
        # self.discretised_source_data = discretise_data(simulation_data.frequency_ts_np, simulation_data.meta_data['sample_rate'], self.index_delta_t , number_intervals, start_idx, end_idx)
       
   

    def accomadate_energy_frames(self,energy_frames=[]):
            # --- fill indexing ---
        query_time_start = t.time()
        total_e_frames = len(energy_frames) 
        idx = 0
        for energy_data in energy_frames:
            # print (energy_data)
            status = self.add_to_index(energy_data)
            if (status == 1):
                self.number_energy_frames_used += 1
            # print (f'{idx} of {total_e_frames}')
            
            idx += 1
        
        

        
        query_time_end = t.time()
        query_time = query_time_end - query_time_start
        # print (f'frames used : {self.number_energy_frames_used} of {self.number_energy_frames}')
        # print (f'adapter build')
        # print (f'index query time {query_time}')



    def ft_mt_build_band_energy_profile(self,sample_delta_t : float = 1000,  simulation_data : SimulationData = None, discrete_size = 200, sort : bool = False):
        """
        

        Args:
            time_start (dt): _description_
            time_end (dt): _description_
            frequency_min (float): _description_
            frequency_max (float): _description_

        Returns:
            _type_: _description_
        """
        self.number_energy_frames_used = 0
        self.delta_t = sample_delta_t
        self.index_delta_t = sample_delta_t
        self.index_delta_f = discrete_size
        
        query_time_start = t.time()
        
        self.max_energy = 0
        self.min_energy = 1000
        self.max_avg_energy = 0
        
        if sample_delta_t == -1:
            sample_delta_t = self.dt * 3
            print (f'Best temporal resolution mode engaged! {sample_delta_t}')
        
        
        # iterate over f buckets
        frequency_bound_lower = self.min_freq
        # print (f'min f : {frequency_bound_lower}')
        # time considerations
        signature_frame_start_dt = dt.strptime(simulation_data.meta_data['data_frame_start'], '%y%m%d_%H%M%S.%f')
        signature_frame_end_dt = dt.strptime(simulation_data.meta_data['data_frame_end'], '%y%m%d_%H%M%S.%f')
        marlin_sample_time = sample_delta_t  #seconds
        
        
        # print (f'sig from {signature_frame_start_dt} -> {signature_frame_end_dt}')
        
        
        # print (self.min_freq,self.max_freq)
        frequency_bound_index = 0
        
        f_hit = False
        t_hit = False
        
        frequency_bound_index = 0
        
        entropy_time_tracker = {}
        self.frequency_index_values = {}
        
        # build indexing
        frequency_bound_lower = self.min_freq
        
        while frequency_bound_lower < self.max_freq:
            # print (f'active f {frequency_bound_lower}')
            sample_time_start = signature_frame_start_dt
            frequency_bound_upper = frequency_bound_lower + discrete_size
            self.fast_index_energy_stats[frequency_bound_index] = {}
            self.frequency_index_values[frequency_bound_index] = []
            self.frequency_index_values[frequency_bound_index].append(frequency_bound_lower)
            self.frequency_index_values[frequency_bound_index].append(frequency_bound_upper)
            time_sub_data = {}
            self.time_index_values = []
            while sample_time_start < signature_frame_end_dt: 
                # (print (f'active f { sample_time_start}'))
                sample_time_end = sample_time_start + timedelta(seconds=sample_delta_t)
                self.time_index_values.append(sample_time_start)
                # build index
                time_sub_data[sample_time_start] = SubDomainFrame([frequency_bound_lower,frequency_bound_upper],[sample_time_start,sample_time_end],{}, [])
                
                sample_time_start = sample_time_end
       
            self.fast_index_energy_stats[frequency_bound_index] = time_sub_data
       
            #inrement counters
            frequency_bound_index += 1 
            frequency_bound_lower = frequency_bound_upper
       
        # print ('f index built')
        idx = 0 
        total_e_frames = len(self.energy_frames) 
        
        
        number_threads = 10
        # print (f'number_index : {total_e_frames}')
        delta_ind = math.floor(total_e_frames/number_threads)
        data_chunks = []
        threads_v = []
        for item in divide_chunks(self.energy_frames,delta_ind):
            data_chunks.append(item)
            l = len(item)
            # print(f'length {l}')
            x = threading.Thread(target=self.accomadate_energy_frames, args=(item,))
            threads_v.append(x)
        
        for thread in threads_v:
            # thread.start()
            # print (thread)
            thread.start()
        
            
        # for i in range(0, number_threads):
            
        #     print (f'thread : {i}')
        #     print (f'start index : {}')
        #     print (f'end index : {}')
        #     x = threading.Thread(target=self.accomadate_energy_frames, args=(0,total_e_frames-1))
        
        
        
        # --- fill indexing ---
        
        # for energy_data in self.energy_frames:
            
        #     status = self.add_to_index(energy_data)
        #     if (status == 1):
        #         self.number_energy_frames_used += 1
        #     print (f'{idx} of {total_e_frames}')
        #     idx += 1
        
        # query_time_end = t.time()
        # query_time = query_time_end - query_time_start
        # print (f'frames used : {self.number_energy_frames_used} of {self.number_energy_frames}')
        # print (f'adapter build')
        # print (f'index query time {query_time}')
        
        # --- fill indexing ---

    def add_to_index(self, energy_data):
        startt(name="inner_index_add")
        #print (energy_data)
        # print (self.time_index_values[len(self.time_index_values)-1])
        # exit()
        status = 0 # added or not  0: false, 1: true
        
        avg_frame_f = (energy_data.frequency_bounds[0] + energy_data.frequency_bounds[1]) /2
        avg_frame_t = energy_data.time_frame[0] + (((energy_data.time_frame[1])-(energy_data.time_frame[0])) / 2 )
        avg_frame_t_ms = avg_frame_t.timestamp() * 1000
        # get f index
        # f_index = min(self.frequency_index_values.keys(), key=lambda x: abs(x[1] -  avg_frame_f))
        # print (f_index)
        
        # get t index
        # t_index = min(self.fast_index_energy_stats[2].keys(), key=lambda x: abs(x -  avg_frame_t))
        #print (t_index)
        f_index = 0
        t_index = 0
        for f, v in self.frequency_index_values.items():
            if avg_frame_f > v[0] and avg_frame_f < v[1]:
                # print (f, v[0], avg_frame_f)
                f_index = f
                break
        msg = ''
        min_delta_t = 1000
        delta_t = abs(avg_frame_t -self.time_index_values[0])
        # for f_index, sub_domain_data in self.fast_index_energy_stats.items():
        
        # search_array = self.
        startt(name="search_time")
        
        
        # for idx in range(0,len(self.time_index_values)-1):
        #     if avg_frame_t >= (self.time_index_values[idx])  and (avg_frame_t< self.time_index_values[idx+1] ):
        #         #print (f'time idx : {idx} value : {self.time_index_values[idx]}')
        #         t_index = self.time_index_values[idx]
        #         break
        
        idx = get_closest_index_by_positive_value(avg_frame_t_ms, self.f_index_numpy[f_index] )
        t_index = self.time_index_values[idx]
            
        # stopt(desc="search_time", out=1)
        # print (t_index)
        
        #last figure - not needed now?
        # if avg_frame_t >= (self.time_index_values[len(self.time_index_values)-1] ):
        # if avg_frame_t >= (self.time_index_values[len(self.time_index_values)-1] - timedelta(milliseconds= 1)):
            
            # print (f'time idx : {idx} value : {self.time_index_values[idx]}')
            # t_index = self.time_index_values[idx+1]
            # break
            
            # t_index = self.time_index_values[len(self.time_index_values)-1]
        
            
        if t_index != 0:
            # print ('idx found')
            subdomain = self.fast_index_energy_stats[f_index][t_index]
            # print (energy_data.energy_measure)
            subdomain.energy_profile.append(energy_data.energy_measure)
            # print (f'number in subdomain : {len(subdomain.energy_profile)=}')
            status = 1
            
            avg_energy  = 0
            # harmonic    = 0
            # median      = 0
            # variance    = 0
            # kurtosis_value    = 0
            # entropy_value = 0
            
            v = subdomain.energy_profile
            # if (len(subdomain.energy_profile) > 2):
            #     avg_energy  =   statistics.mean(v)
            #     harmonic    =    statistics.harmonic_mean(v)
            #     median      =   statistics.median(v)
            #     variance    =   statistics.variance(v)
            #     kurtosis_value    = kurtosis(v)
            #     entropy_value = entropy(v)
                
            
            # stdev = 0
            
            # if len(v) > 2:
            #     stdev = statistics.stdev(v)
            
            subdomain.stats = {
                'max_energy'    : max(v),
                'min_energy'    : min(v)
                # 'mean_energy'   : avg_energy,
            #     'stdev'         : stdev,
            #     'variance'      : variance,
            #     'kurtosis'      : kurtosis_value,
            #     'entropy'       : entropy_value,
            #     'f'             : (energy_data.frequency_bounds[0] + energy_data.frequency_bounds[1])/2
            }
            
            
        
            
            
            
        else:
            print (f'no data found for {avg_frame_t} and {avg_frame_f} | f:{f_index} t: {t_index}')
            print (msg)
            # print ("no data")
        # stopt(desc="inner_index_add", out=1)
        # if t_index is not 0:
        #     print (self.fast_index_energy_stats[f_index][t_index])
        return status
      
    
    def check_data(self):
        # check data in self.fast_index_energy_stats[f_index][t_index]. Delta t's may be too small and energy values
        # may not be added correctly.
        
        for f, t_vec in self.fast_index_energy_stats.items():
            for t_string, t_data in t_vec.items():
                if t_data.stats == None:
                    print (f'No stats for f index {f} and time {t_data}')
    
    def query_band_energy_loaded_profile(self, time_start: dt, time_end:dt, frequency_min : float, frequency_max:float):
        
       
        query_time = time_start
        # print (f'frequency max: {frequency_max}')
        # print (f'frequency min: {frequency_min}')
        # print (f'query time  : {query_time}')
        #iterate over frequency bound frames
        query_frames = []
        for domain_frame in self.sub_domain_frames:
            # print (domain_frame.time_frame[0])
            if query_time >= domain_frame.time_frame[0] and query_time <= domain_frame.time_frame[1]:
                
                #print (domain_frame.frequency_bounds[0],domain_frame.frequency_bounds[1] )
                
                #if query_frequency >= domain_frame.frequency_bounds[0] and query_frequency <= domain_frame.frequency_bounds[1]:
                if domain_frame.frequency_bounds[1] >= frequency_min and frequency_min >= domain_frame.frequency_bounds[0] :
                    # print (f'hit : {domain_frame.frequency_bounds}')
                    #print (domain_frame.time_frame[0],domain_frame.time_frame[0] )
                    query_frames.append(domain_frame)
                    
                    continue
                    # print (domain_frame.frequency_bounds[0])
                    # return domain_frame.energy_profile, domain_frame.stats
                if domain_frame.frequency_bounds[1] >= frequency_max and frequency_max >= domain_frame.frequency_bounds[0] :
                    # print (f'hit : {domain_frame.frequency_bounds}')
                    #print (domain_frame.time_frame[0],domain_frame.time_frame[0] )
                    query_frames.append(domain_frame)
                    
                    continue
                    # print (domain_frame.frequency_bounds[0])
                    # return domain_frame.energy_profile, domain_frame.stats
                if domain_frame.frequency_bounds[0] >= frequency_min and domain_frame.frequency_bounds[1] <= frequency_max :
                    # print (f'hit : {domain_frame.frequency_bounds}')
                    #print (domain_frame.time_frame[0],domain_frame.time_frame[0] )
                    query_frames.append(domain_frame)
                    
                    continue
                    # print (domain_frame.frequency_bounds[0])
                    # return domain_frame.energy_profile, domain_frame.stats
                if domain_frame.frequency_bounds[0] >= frequency_min and  domain_frame.frequency_bounds[1] <= frequency_max  :
                    # print (f'hit : {domain_frame.frequency_bounds}')
                    #print (domain_frame.time_frame[0],domain_frame.time_frame[0] )
                    query_frames.append(domain_frame)
                    
                    continue
                    # print (domain_frame.frequency_bounds[0])
                    # return domain_frame.energy_profile, domain_frame.stats
                    
        data_l = len(query_frames)
        # print (f'found : {data_l}')
        # for f in query_frames:
        #     print (f'{f.frequency_bounds[0]}')
        # print (frequency_min, frequency_max)
        
        return query_frames
    
    def query_energy_frames_at_time(self, _time : dt, data_instance : SimulationData = None):
        """
        
        Query energy frames by frequency bounds. 

        Args:
            time (dt): _description_
            frequency (float): _description_
            data_instance (SimulationData): _description_

        Returns:
              [EnergyFrame]: List of valid energy frames, float : average energy value
        """
        
        energy_frames = []
        if data_instance is not None:
            for energy_data in data_instance.energy_data:
                if _time >= energy_data.time_frame[0] and _time <= energy_data.time_frame[1]:
                    energy_frames.append(energy_data)
        else:
            energy_frames = self.energy_frames
    
        energy_sum = 0
        for energy_frame in energy_frames:
            energy_sum += energy_frame.energy_measure
        
        avg_energy = energy_sum/max(1,len(energy_frames))
        
            

        return energy_frames, avg_energy
    
    def query_energy_frames_at_frequency(self, frequency: float, data_instance : SimulationData = None, _time : dt = None):
        """
        
        Query energy frames by frequency bounds and time bounds
    
        Args:
            time (dt): _description_
            frequency (float): _description_
            data_instance (SimulationData): _description_

        Returns:
            [EnergyFrame]: List of valid energy frames, float : average energy value
        """
        
        energy_frames = []
        if _time is not None:
            if data_instance is not None:
                for energy_data in data_instance.energy_data:
                    if frequency >= energy_data.frequency_bounds[0] and frequency <= energy_data.frequency_bounds[1]  and (energy_data.time_frame[0] <= _time and energy_data.time_frame[1] >= _time):
                        energy_frames.append(energy_data)
            else:
                for energy_data in self.energy_frames:
                    # print (energy_data.frequency_bounds[0],energy_data.frequency_bounds[1] )
                    # print (energy_data.time_frame[0])
                    
                    if frequency >= energy_data.frequency_bounds[0] and frequency <= energy_data.frequency_bounds[1] and energy_data.time_frame[0] <= _time and energy_data.time_frame[1] >= _time:
                        # print ("here")
                        energy_frames.append(energy_data)
                    
        if _time is None:
            if data_instance is not None:
                for energy_data in data_instance.energy_data:
                    if frequency >= energy_data.frequency_bounds[0] and frequency <= energy_data.frequency_bounds[1]:
                        energy_frames.append(energy_data)
            
            else:
                for energy_data in self.energy_frames:
                    if frequency >= energy_data.frequency_bounds[0] and frequency <= energy_data.frequency_bounds[1]:
                        energy_frames.append(energy_data)
    
    
    
        energy_sum = 0
        for energy_frame in energy_frames:
            energy_sum += energy_frame.energy_measure
        
        avg_energy = energy_sum/max(1,len(energy_frames))
        return energy_frames, avg_energy
  
    def get_max_f_index(self):
        for key, value in self.fast_index_energy_stats.items():
            print (key)
    
    def ft_query_energy_frame(self, _time : dt, freq : float):
        # print (self.fft_times[0], self.fft_times[1])
        # print (self.fft_times[len(self.fft_times)-1], self.fft_times[len(self.fft_times)-2])
        # print (self.time_index_values[0], self.time_index_values[len(self.time_index_values)-1])
        # print (self.fast_index_energy_stats[0])
        # exit()
        query_time_start = t.time()

        t_index = min(self.fft_times, key=lambda x: abs(x - _time))
        f_index = min(self.librosa_f_bins, key=lambda x: abs(x -  freq))
        # print (type(self.fft_times), type(self.librosa_f_bins))
        # print (f_index, t_index)
        # print ('---')
       
        f_idx = np.where(self.librosa_f_bins == f_index)[0]
        t_idx = (self.fft_times.index(t_index))
        # # # t_idx = (np.abs(self.fft_times - _time)).argmin()
        # print (f_index, t_index, self.librosa_f_bins[f_idx])
        # print (f_idx, t_idx)
        # print (f_idx, t_idx)
        query_time_end = t.time()
        query_time = query_time_end - query_time_start
        # print (f'index query time {query_time}')
        # print (self.fourier[f_idx, t_idx])
        
        return (self.fourier[f_idx, t_idx], t_index)
        
    
    def query_stats_freq_index(self, frequency_index : int = 0, _time : dt = None ):
        #v3.0
        # _time_ms = _time.timestamp() * 1000
        # numpy_time_start = t.time()
        
        # idx_value = self.f_index_numpy[frequency_index].flat[np.abs(self.f_index_numpy[frequency_index] - _time_ms).argmin()]
        # print (idx_value)
        # numpy_time_end = t.time()
        # numpy_time = numpy_time_end - numpy_time_start
        # print (f'NUMPY index query time {numpy_time}')
        
        query_time_start = t.time()
        if frequency_index in self.fast_index_energy_stats:
            stats_time_vector = self.fast_index_energy_stats[frequency_index]
            
        else:
            return None
        
        t_index = min(self.fast_index_energy_stats[frequency_index].keys(), key=lambda x: abs(x - _time))
        stats_data = stats_time_vector[t_index]
        query_time_end = t.time()
        query_time = query_time_end - query_time_start
        print (f'Python index query time {query_time}')
        
        return (stats_data)
    
    
    
    
    def query_stats_vector_freq_index(self, frequency_index : int = 0, _time_start : dt = None, _time_end : dt = None ):
        
        query_time_start = t.time()
        stats_vector = []
        if frequency_index in self.fast_index_energy_stats:
            stats_time_vector = self.fast_index_energy_stats[frequency_index]
        else:
            print (f'Index not found {frequency_index}')
            return None
        
        
        # print (stats_time_vector)
        for subdomain, v in stats_time_vector.items():
            # print (_time_start, _time_end)
            # print (v.time_frame[0], v.time_frame[1])
            # active_time = (v.time_frame[0]) + ((v.time_frame[1] - v.time_frame[0]) / 2)
            active_time = (_time_start) + ((_time_end - _time_start) / 2)
            # if active_time > _time_start and active_time < _time_end:
            if active_time > v.time_frame[0] and active_time < v.time_frame[1]:
                # print ('hit')
                stats_vector.append(v)
            
        query_time_end = t.time()
        query_time = query_time_end - query_time_start
        # print (f'index vector query time {query_time}')
        
        return (stats_vector)
    
    def query_energy_frames_at_frequency_bounds(self, frequency_min: float, frequency_max: float, _time : dt = None):
        """

        Args:
            frequency_min (float): _description_
            frequency_max (float): _description_
            _time (dt, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        query_time_start = t.time()
        energy_frames = []
        if _time is not None:
                # print (f'min_f : {self.min_freq} {self.max_freq}')
                # print (_time)
                t_hit = False
                for energy_data in self.energy_frames:
                    # print (energy_data.time_frame[0], energy_data.time_frame[1])
                    if energy_data.time_frame[0] <= _time and energy_data.time_frame[1] >= _time:
                        t_hit = True
                        if energy_data.frequency_bounds[0] <= frequency_min and energy_data.frequency_bounds[1] >= frequency_max:
                            # print ("here")
                            energy_frames.append(energy_data)
                            continue
                        
                        if  frequency_min >= energy_data.frequency_bounds[0] and energy_data.frequency_bounds[1] >= frequency_min:
                            # print ("here")
                            energy_frames.append(energy_data)
                            continue
                        if  frequency_max >= energy_data.frequency_bounds[0] and energy_data.frequency_bounds[1] >= frequency_max:
                            # print ("here")
                            energy_frames.append(energy_data)
                            continue
                        
                        if  frequency_max >= energy_data.frequency_bounds[0] and energy_data.frequency_bounds[1] >= frequency_max:
                            # print ("here")
                            energy_frames.append(energy_data)
                            continue
                        
                        if  energy_data.frequency_bounds[0] >= frequency_min and energy_data.frequency_bounds[1] <= frequency_max:
                            # print ("here")
                            energy_frames.append(energy_data)
                            continue
                        
                       
                        
                        #if domain_frame.frequency_bounds[0] >= frequency_min and domain_frame.frequency_bounds[1] <= frequency_max :
                        #if domain_frame.frequency_bounds[0] >= frequency_min and  domain_frame.frequency_bounds[1] <= frequency_max  :
                        
                    
        if _time is None:
           
                for energy_data in self.energy_frames:
                    if energy_data.frequency_bounds[0] >= frequency_min and energy_data.frequency_bounds[1] <= frequency_max:
                        energy_frames.append(energy_data)
    
    
    
        energy_sum = 0
        db_sum = 0
        data_len = len(energy_frames)
        #print  (f'data length (t): {data_len} fmin : {frequency_min} fmax: {frequency_max} time: {t_hit}')
        for energy_frame in energy_frames:
            # print (energy_frame.energy_measure)
            energy_sum += energy_frame.energy_measure
            db_sum += energy_frame.db_measure
            # print (energy_frame.frequency_bounds[0], energy_frame.frequency_bounds[1])
        
        avg_energy = 0
        avg_energy = energy_sum/max(1,len(energy_frames))
        avg_db = 0
        avg_db = db_sum/max(1,len(energy_frames))
        query_time_end = t.time()
        query_time = query_time_end-query_time_start
        # print (f'time to query data adapter {query_time}')
        
        return energy_frames, avg_energy, avg_db
    
    def query_energy_frames_at_times_bounds(self, time_start: dt, time_end: dt):
        """
        

        Args:
            time_start (dt): _description_
            time_end (dt): _description_

        Returns:
            _type_: _description_
        """
        
        energy_frames = []
        
           
        for energy_data in self.energy_frames:
            
            
            if energy_data.time_frame[0] >= time_start and energy_data.time_frame[1] <= time_end:
                energy_frames.append(energy_data)


        energy_sum = 0
        for energy_frame in energy_frames:
            energy_sum += energy_frame.energy_measure
        
        avg_energy = energy_sum/max(1,len(energy_frames))
        return energy_frames, avg_energy
    
    def query_energy_frequency_time_bounds(self, time_start: dt, time_end: dt, frequency_min: float, frequency_max: float):
        """
        

        Args:
            time_start (dt): _description_
            time_end (dt): _description_
            frequency_min (float): _description_
            frequency_max (float): _description_

        Returns:
            _type_: _description_
        """
        energy_frames = []
        for energy_data in self.energy_frames:
                    
                    if energy_data.frequency_bounds[0] >= frequency_min and energy_data.frequency_bounds[1] <= frequency_max and energy_data.time_frame[0] >= time_start and energy_data.time_frame[1] <= time_end:
                        energy_frames.append(energy_data)
    
        energy_sum = 0
        for energy_frame in energy_frames:
            energy_sum += energy_frame.energy_measure
        
        avg_energy = energy_sum/max(1,len(energy_frames))
        return energy_frames, avg_energy
    
    def query_band_energy_profile(self, time_start: dt, time_end:dt, frequency_min : float, frequency_max:float, sort : bool = False):
        """
        

        Args:
            time_start (dt): _description_
            time_end (dt): _description_
            frequency_min (float): _description_
            frequency_max (float): _description_

        Returns:
            _type_: _description_
        """
        energy_sum = 0
        energy_frames = []
        energy_profile = []
        max_energy = 0
        min_energy = 1000000000
        for energy_data in self.energy_frames:
                    
                    if energy_data.frequency_bounds[0] >= frequency_min and energy_data.frequency_bounds[0] <= frequency_max and energy_data.time_frame[0] >= time_start and energy_data.time_frame[1] <= time_end:
                        
                        energy_frames.append(energy_data)
                        # print (energy_data.time_frame)
    
        energy_sum = 0
        frequency_counter = {}
        for energy_frame in energy_frames:
            e = abs(energy_frame.energy_measure)
            max_energy = max(max_energy, e)
            min_energy = min(min_energy,e)
            energy_sum += abs(energy_frame.energy_measure)
            avg_f = math.floor(energy_frame.frequency_bounds[0] + energy_frame.frequency_bounds[1]/2)
            if avg_f in frequency_counter:
                frequency_counter[avg_f].append(e)
            else:
                frequency_counter[avg_f] = []
                frequency_counter[avg_f].append(e)
            # e_entry = {
            #     'frequency' : energy_frame.frequency_bounds[0],
            #     'energy'    : e
            # }
            # energy_profile.append(e_entry)
        ind_e_profile = []
        
        for f, v in frequency_counter.items():
            
            e_avg = statistics.mean(v)
            harmonic = statistics.harmonic_mean(v)
            median = statistics.median(v)
            stdev = 0
            if len(v) > 2:
                stdev = statistics.stdev(v)
            
            e_entry = {
                'frequency'         : float(f),
                'average_energy'     : float(e_avg),
                'harmonic'          : harmonic,
                'median'            : median,
                'stdev'             : stdev
                
            }
            energy_profile.append(e_entry)
            ind_e_profile.append(e_avg)
            
        
        avg_energy = energy_sum/max(1,len(energy_frames))
        
        if sort:
            energy_profile.sort(key=lambda x: x.frequency, reverse=False)
        
        #f stats
        mode_e_mean     = statistics.mean(ind_e_profile)
        mode_e_stdev    = statistics.stdev(ind_e_profile)
        mode_e_var      = statistics.variance(ind_e_profile)
        
        stats = {
            'max_energy'    : max_energy,
            'min_energy'    : min_energy,
            'avg_energy'    : avg_energy,
            'mean'          : mode_e_mean,
            'stdev'         : mode_e_stdev,
            'variance'      : mode_e_var
        }
        return energy_frames,energy_profile, stats 
    
    def query_label_time(self, time_start: dt, time_end : dt):
        """
        Query for labelled data in a time frame
        Args:
            time_start (dt): _description_
            time_end (_type_): _description_
            dt (_type_): _description_

        Returns:
            _type_: _description_
        """
        xr_data = {"xr":False}
        #math by time rahter than snapshot ids for scalablity / differeing resolutions
        # print(self.labelled_data)
        query_hits = []
        # print (self.labelled_data)
        # exit()
        #print (self.labelled_data)
        for snapshot_id, time_bounds in self.labelled_data.items():
            # print (time_bounds[1])
            # now convert to ms for comparisons
            time_start_ms = dt.timestamp(time_start.replace(tzinfo=timezone.utc)) * 1000
            time_end_ms = dt.timestamp(time_end.replace(tzinfo=timezone.utc)) * 1000
            
            
            # time_start_ms = time_start.timestamp() * 1000
            # time_end_ms = time_end.timestamp() * 1000
            
            
            # print (time_start)
            # print (time_start_ms)
            # print (float(time_bounds[0]))
            # if time_start_ms < float(time_bounds[0]):
            #     print (">")
            # else: 
            #     print ("less")
            # print (dt_stamp * 1000)
            # exit()
            
            if float(time_start_ms) <= float(time_bounds[0]) and float(time_end_ms) >= float(time_bounds[1]):
                
                
                xr_data = {
                    "xr"                : True,
                    "xr_time_start"     : time_start,
                    "xr_time_end"       : time_end,
                    "label_snapshot_id" : snapshot_id
                }
                
                query_hits.append(xr_data)
                return query_hits
                
                
            if float(time_start_ms) >= float(time_bounds[0]) and float(time_end_ms) <= float(time_bounds[1]):
                # print (time_start_ms, time_bounds[0], time_end_ms, time_bounds[1])
                
                xr_data = {
                    "xr"                : True,
                    "xr_time_start"     : time_start,
                    "xr_time_end"       : time_end,
                    "label_snapshot_id" : snapshot_id
                }
                query_hits.append(xr_data)
                return query_hits
            
            mid_sig_time = float(time_bounds[0]) + ((float(time_bounds[1])- float(time_bounds[0]))/2)
            mid_iter_time = float(time_start_ms) + ((float(time_end_ms)- float(time_start_ms))/2)
            # print (mid_sig_time, mid_iter_time,abs(mid_sig_time-mid_iter_time) )
            
            if (abs(mid_sig_time-mid_iter_time) < 100):
                xr_data = {
                    "xr"                : True,
                    "xr_time_start"     : time_start,
                    "xr_time_end"       : time_end,
                    "label_snapshot_id" : snapshot_id
                }
                query_hits.append(xr_data)
                return query_hits
    
        
        
        return query_hits
    
    def query_label_id(self, snapshot_id : str = ""):
        if snapshot_id in self.labelled_data.keys():
            return True
    
    def get_f_from_idx(self, idx):
        f = self.min_freq + (idx *  (self.index_delta_f))
        return f
    
    def get_index_from_f(self, f):
        if f < self.min_freq or self.max_freq < f:
            return -1
        index_number = (f-self.min_freq)//self.index_delta_f
        return index_number
    
    
    
    def __str__(self):
        
        return(f'[Max Frequency] : {self.max_freq} [Min Frequency] : {self.min_freq} [dt] : {self.fourier_delta_t}  [df] : {self.fourier_delta_f} [sr] : {self.sample_rate}')
    
    def save(self, args = {}):
        s_id = args['snapshot_id']
        fileName = f'{s_id}.drv'
        saveFile = open(fileName, 'wb')
        pickle.dump(self, saveFile)
        saveFile.close()



if __name__ == "__main__":
    limit = 3000
    data_adapter = MarlinData(load_args={'limit': 10})
    r = data_adapter.download_simulation_snapshots(load_args={"snapshot_type": "simulation", "limit": limit, "location":['brixham'], "time_start" : '240225_135500.000504', "time_end" : '240225_135800.000504'}, id_only=True)
    print (r)  
    
    for data in r:
        print (data['start_time'])
    
    # link = data_adapter.get_ident_research_link(target_time='2024-09-11T22:59:56.200427Z', location='milford_haven',
    #                                      name="Rahul", position="RD", uid="0001vixen")
    
    # print (link)


@jit
def query_stats_freq_index_hyped(frequency_index : int = 0, _time : int = None, data_arr = None ):
    #v3.0
    
    # numpy_time_start = t.time()
    
    idx_value = data_arr[frequency_index].flat[np.abs(data_arr[frequency_index] - _time).argmin()]
    return (idx_value)
    # print (idx_value)
    # numpy_time_end = t.time()
    # numpy_time = numpy_time_end - numpy_time_start
    # print (f'HYPED NUMPY index query time {numpy_time}')
    
    