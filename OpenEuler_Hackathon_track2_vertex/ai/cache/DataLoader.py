import sys, os, random
import numpy as np
import pandas as pd

class DataLoader(object):
    def __init__(self):
        self.requests = []
        self.operations = []

    def get_requests(self):
        pass
    def get_operations(self):
        pass

class DataLoaderPintos(DataLoader):
    def __init__(self, progs, boot=False):
        super(DataLoaderPintos, self).__init__()

        if isinstance(progs, str): progs = [progs]
        for prog in progs:
            df = pd.read_csv(prog, header=0)
            if not boot: df = df.loc[df['boot/exec'] == 1, :]
            self.requests += list(df['blocksector'])
            self.operations += list(df['read/write'])

    def get_requests(self):
        return self.requests

    def get_operations(self):
        return self.operations


    def get_requests(self):
        return self.requests

    def get_operations(self):
        return self.operations