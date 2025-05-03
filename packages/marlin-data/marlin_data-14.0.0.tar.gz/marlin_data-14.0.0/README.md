# ``marlin_data`` | the data adapter

&copy; Rahul Tandon, RS Aqua 2024

## About
``marlin_data`` allows access to RSA's acoustic signature database. The module requests the RSA acoustic dataset required in order to run a machine learning (ML). Current version of ``marlin_data`` provides a predefined dataset for proof of concept and tutorial purposes. Future versions will allow for more specific datasets as well as definig training and validation datasets separately. 
> **NOTE**  | Numerical data in ``marlin_data`` is defined using Python's numpy and pandas library.


<!-- 
> One-Line Box made with Blockquote -->

## Dependencies
`
import numpy as np
import pandas as pd
import requests, json
import logging
import dotenv
import os, sys
from dataclasses import dataclass
import random
`

## Installation

`from marlin_data import *`


## Quick Start

### Accessible Data 

#### Datafeed Instance

Each iteration over the Marlin data feed will provide once instance of the datafeed and simulation data / snapshots. Frequency time series in numpy and a pandas dataframe is available along with descrictive metadata. Feed data is an iterable class which can be looped over allowing for an incremental datafeed.

`Feed Instance` -> `frequency_ts_np`

The frequency time series for this data snapshot ( NumPy Array )

        for feed_instance in data_feed: frequency_np_array = feed_instance['frequency_ts_np']
        
`Feed Instance` -> `frequency_ts_pd`

The frequency time series for this data snapshot (pandas `DataFrame`) 

        for feed_instance in data_feed: frequency_data_frame = feed_instance['frequency_ts_pd']

`Feed Instance` -> `meta_data`

Metadata for the associated snapshot. Metadata is a dictionary with the following defined fields:

* `snapshot_id` : unique id for the snapshot
* `data_frame_start` : timestamp for the start of the snapshot data frame
* `data_frame_end` : timestamp for the end of the snapshot data frame
* `listener_location` : geo location of the listening device for snapshot
* `location_name` : human friendly name of listening location
* `frame_delta_t` : delta t for the snapshot (s)
* `sample_rate` : frequency recorder sample rate

#### Signature Data

`SignatureData` dataclass is accessible from `MarlinData` -> `signature_data`. Key values are stored in `MarlinData` -> `signature_index`.

        @dataclass
        class SignatureData:
                frequency_ts_np : np.array
                frequency_ts_pd : pd.DataFrame
                meta_data : {}

Metadata for the associated snapshot. Metadata is a dictionary with the following defined fields:

* `snapshot_id` : unique id for the snapshot
* `data_frame_start` : timestamp for the start of the snapshot data frame
* `data_frame_end` : timestamp for the end of the snapshot data frame
* `listener_location` : geo location of the listening device for snapshot
* `location_name` : human friendly name of listening location
* `frame_delta_t` : delta t for the snapshot (s)
* `sample_rate` : frequency recorder sample rate


#### Simulation Data

`SimulationData` dataclass is accessible from `MarlinData` -> `simulation_data`. Key values are stored in `MarlinData` -> `simulation_index`.

        @dataclass
        class SimulationData:
            frequency_ts_np : np.array
            frequency_ts_pd : pd.DataFrame
            meta_data : {}
            snapshot : bool = True

Metadata for the associated snapshot. Metadata is a dictionary with the following defined fields:

* `snapshot_id` : unique id for the snapshot
* `data_frame_start` : timestamp for the start of the snapshot data frame
* `data_frame_end` : timestamp for the end of the snapshot data frame
* `listener_location` : geo location of the listening device for snapshot
* `location_name` : human friendly name of listening location
* `frame_delta_t` : delta t for the snapshot (s)
* `sample_rate` : frequency recorder sample rate

### Downloading data

Instantiate a `MarlinData` class.

        ` marlin_data = MarlinData(load_args={})`
        
Download signature data from RSA signature database.

        `marlin_data.download_signatures(load_args={})`

Download simulation / ML run data required for datafeed.

        `marlin_data.download_simulation_snapshots(load_args={})`

load_args:

* `limit`       : maximum number of downloads (Require in init())
* `signature_ids` : vector of signature ids
* `ss_ids` : vector of snapshot ids◊
* `location` : vector of locations





### Connecting to datafeed

Create the Marlin datafeed. This data feed can be iterated over in order to simulate a data feed into a model.

        `data_feed = MalrinDataStreamer()`

Connect the downloaded data to the datafeed instance.

        `data_feed.init_data(marlin_data.simulation_data, marlin_data.simulation_index) `

Iterate over the datafeed.

        for data_inst in data_feed:
                print (data_inst)
`










