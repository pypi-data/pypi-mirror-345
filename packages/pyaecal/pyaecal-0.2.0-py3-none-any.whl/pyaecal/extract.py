#  Copyright (c) 2017-2021 Jeorme Douay <jerome@far-out.biz>
#  All rights reserved.
# Far-Out extraction
import glob
import logging
import os
from datetime import datetime
from queue import Queue
from threading import Thread

import mdfreader as mdfr
import polars


class Extract(Thread):
    """
    Extract class extract channels from single or multiple files
    """

    def __init__(self):
        super().__init__()
        # self.files = []
        self.timestamp = datetime.fromtimestamp(0)
        self.channels = []
        self.rename = dict()
        self.interpolate = dict()
        self.optional = dict()
        self.mdf = mdfr.Mdf()
        self.files = Queue()
        self.data = Queue()

    def add_channel(self, channel, rename="", optional=False, inter=False):
        """
        Set a channel to be retrieved from the MDF.
        If a rename name is supplied, the channels will be reneamed.
        If more than one channel as the same rename name, all channels will be checked
        until one available is found.
        Interpolation should not be used on digitial signal.
        The interpolation is linear and should be used on non digitial signals to
        improve accuracy lf signal in measurement with multiple time raster.

        :param channel: channel name
        :param rename: name to be renamed to
        :param inter: Set to True to interpolate missing values, default False.
        :return: None
        """
        if rename == "":
            rename = channel

        if channel in self.channels:
            return
        self.channels.append(channel)
        if rename not in self.rename.keys():
            self.rename[rename] = [channel]
        else:
            self.rename[rename].append(channel)
        self.interpolate[rename] = inter
        self.optional[rename] = optional

    def add_file(self, filename):
        """
        Add single file to the list of files to be processed

        :param file: file name path to the file
        :return: none
        """
        self.files.put(filename)
        # self.files.append(filename)
        # self.files = list(set(self.files))  # remove dual entries just in case

    def add_directory(self, pathname):
        """
        Add a directory recursively to the files to be processed.
        Files recognize are mdf and mf4 exensions

        :param path: path to be added
        :return: none
        """
        for file in glob.glob(pathname + "/**/*.mdf", recursive=True):
            self.add_file(file)

        for file in glob.glob(pathname + "/**/*.mf4", recursive=True):
            self.add_file(file)

        for file in glob.glob(pathname + "/**/*.dat", recursive=True):
            self.add_file()

    def extract(self):

        self.run()
        self.files.join()
        # results = []
        # while not self.data.empty():
        #     results.append(self.data.get())
        #     self.data.task_done()
        # return results

    def get_data(self, filename):
        """
        Read the MDF file and retrieved the requested data

        :param filename: filename ( with full path ) of the MDF file to open
        :return: polars dataframe containing the datas. The time offset for the
        channels is set to the column offset. The dataframe indes is based on the
        file timestamp with the measurement time offset. This allows datetime
        operation on the dataframe.
        """
            
        df = polars.DataFrame()
        try:
            self.mdf = mdfr.Mdf(filename)
            info = mdfr.MdfInfo()
            info.read_info(filename)
            
            # Unified timestamp extraction
            if self.mdf.MDFVersionNumber <= 300:
                s = info["HDBlock"]["Date"].split(":")
                timestamp = datetime.fromisoformat(f"{s[2]}-{s[1]}-{s[0]} {info['HDBlock']['Time']}")
            elif self.mdf.MDFVersionNumber < 400:
                timestamp = datetime.fromtimestamp(info["HDBlock"]["TimeStamp"] / 10**9)
            else:
                timestamp = datetime.fromtimestamp(info["HD"]["hd_start_time_ns"] / 10**9)

            for rename in self.rename.keys():
                data = self.get_rename(rename)
                if data is None:
                    if not self.optional[rename]:
                        logging.info(f"{rename} not in file {filename}")
                        return polars.DataFrame()
                    continue
                if rename not in df.columns:
                    df = data if df.is_empty() else df.join(data, on="offset", how="outer")

            # Apply interpolation or forward-fill
            for rename in self.rename.keys():
                if rename not in df.columns:
                    continue
                if self.interpolate[rename]:
                    df = df.with_columns(polars.col(rename).interpolate())
                else:
                    df = df.with_columns(polars.col(rename).forward_fill())

            df = df.unique().drop_nulls().sort("offset")
            rows, cols = df.shape
            logging.info(f"{filename}: {rows} rows")
            return df
        except Exception as e:
            logging.error(f"Error processing {filename}: {str(e)}")
            return polars.DataFrame()

    def get_rename(self, rename):
        try:
            for channel in self.rename[rename]:
                tmp = self.mdf.get_channel(channel)
                if tmp is None:
                    return None

                data = polars.DataFrame(
                    {
                        "offset": self.mdf.get_channel_data(self.mdf.get_channel_master(channel)) ,
                        rename: self.mdf.get_channel_data(channel),
                    }
                )
                #data= data.sort('offset')
                return data
        except Exception as e:
            logging.error(str(e))
            return None

    def __iter__(self):
        self.files.join()
        return self

    def __next__(self):
        if self.data.empty():
            raise StopIteration
        data = self.data.get()
        self.data.task_done()
        return data

    def start(self):
        super().start()
        return (self.files, self.data)

    def run(self):
        while True:
            filename = self.files.get()
            # if filename is None:  # Sentinel for stopping
            #     self.files.task_done()
            #     break
            data = self.get_data(filename)
            path, filename = os.path.split(filename)
            filename = filename.split(".")[0]
            self.data.put((filename, data))
            self.files.task_done()
