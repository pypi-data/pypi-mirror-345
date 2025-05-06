import re
from typing import List
from tqdm import tqdm
import os
import glob

import numpy as np
from sklearn.model_selection import train_test_split
from datasets import load_dataset, Dataset

import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc

from .vars import TableCols as TC, DATA_COLS
from .preprocessing import Compose


class DatasetBuilder:
    """
    Main entrypoint class that holds the data and provides methods for data preprocessing and dataset creation.
    """
    
    def __init__(self, 
                 directory,
                 classes=[],
                 regexes=[],
                 norad_ids=None):
        """
        Initializes the DatasetBuilder

        Parameters
        ----------
        directory : str
            The data directory.
        classes : list of str, optional
            A list of class names (default is an empty list).
        regexes : list of str, optional
            A list of regex patterns corresponding to the classes (default is an empty list).
        norad_ids : list of int, optional
            A list of NORAD IDs to filter the data (default is None).
        
        Object are first selected by NORAD_IDs if provided, then by class names with corresponding regex patterns.
        """
        
        self.dir = directory
        self.norad_ids = norad_ids
        assert classes is not None or norad_ids is not None, "Either classes or norad_ids must be provided"

        self.classes = classes
        self.regexes = {}
        if regexes != []:
            self.regexes = {c:re.compile(r) for c,r in zip(classes, regexes)}
        elif classes != []:
            self.regexes = {c:re.compile(c) for c in classes}

        self.table = self.load_data()

        print(f"Loaded {len(self.table)} track")

    def load_data(self):
        """
        Loads the data from self.dir containing .parquet files into a pyarrow table (self.table).
        Filters the data by NORAD IDs and class names with corresponding regex patterns 
        if provided during initialization.
        
        A new columns are added to the original table:
        - 'label' : the class label of the track
        - 'range' : the range of indices from the original track
        """

        parquet_files = glob.glob(f"{self.dir}/*.parquet")
        dataset = pq.ParquetDataset(parquet_files)
        table = dataset.read()


        if self.norad_ids is not None:
            mask = pc.is_in(table[TC.NORAD_ID], value_set=pa.array(self.norad_ids))
            table = table.filter(mask)

        names = list(map(lambda x: x.as_py(), table[TC.NAME]))
        labels = list(map(self._get_label, names))
        table = table.append_column(TC.LABEL, pa.array(labels))

        if self.classes != []:
            table = table.filter(pc.field(TC.LABEL) != 'Unknown')

        ranges = [(0,len(x)-1) for x in table[TC.TIME]]
        table = table.append_column(TC.RANGE, pa.array(ranges))

        return table
    
    def _get_label(self, name):
        """
        Gets the label for a given name based on the regex patterns.

        Parameters
        ----------
        name : str
            The name to match against the regex patterns.

        Returns
        -------
        label : str
            The matched label or 'Unknown' if no match is found.
        """
        for c, r in self.regexes.items():
            if r.match(name) is not None:
                return c
        return 'Unknown'
    
    def split_train_test(self, ratio=0.8, seed=None):
        """
        Splits the dataset into training and testing sets.

        Parameters
        ----------
        ratio : float, optional
            The ratio of the training set size to the total dataset size (default is 0.8).
        seed : int, optional
            The random seed for reproducibility (default is None).

        Returns
        -------
        train_id : list of int
            List of training set IDs.
        test_id : list of int
            List of testing set IDs.
        """

        data = []
        table = self.table
        data = ( table.group_by(TC.ID, use_threads=False)
                      .aggregate([(TC.LABEL, "first")])
                      .to_pandas()
                      .to_numpy() )
        
        X = data[:,0]
        y = data[:, 1]

        train_id, test_id, _, _ = train_test_split(X, y, test_size=1-ratio, stratify=y, random_state=seed)

        return train_id, test_id
    
    def preprocess(self, ops=[]):
        """
        Applies preprocessing operations to the dataset.

        Parameters
        ----------
        ops : list of callable, optional
            List of preprocessing operations to apply (default is an empty list).
        """

        if ops == []:
            return 
        
        preprocessor = Compose(*ops)

        table = self.table
        new_table = None
        for i in tqdm(range(len(table)),desc="Preprocessing"):
            t = table.slice(i,1).to_pylist()[0]
            for c in DATA_COLS:
                if c in t:
                    t[c] = np.array(t[c])

            records = preprocessor(t)
            if records != []:
                if new_table is None:
                    new_table = pa.Table.from_pylist(records)
                else:
                    new_table = pa.concat_tables([new_table, pa.Table.from_pylist(records)])

        self.table = new_table 
    
    def build_dataset(self, split_ratio=None):
        """
        Builds the dataset, optionally splitting it into training and testing sets.

        Parameters
        ----------
        split_ratio : float, optional
            The ratio for splitting the dataset (default is None).

        Returns
        -------
        datasets : Union[Dataset, list of Dataset]
            The built dataset or a pair of train and test datasets if split_ratio is provided.
        """
        
        datasets = []
        if split_ratio is None:
            datasets = Dataset.from_dict(self.table.to_pydict())
        else:
            train_id, test_id = self.split_train_test(split_ratio)
            train_mask = pc.is_in(self.table[TC.ID], pa.array(train_id))
            train_table = self.table.filter(train_mask)
            test_mask = pc.is_in(self.table[TC.ID], pa.array(test_id))
            test_table = self.table.filter(test_mask)
            datasets = [
                Dataset.from_dict(train_table.to_pydict()),
                Dataset.from_dict(test_table.to_pydict())
            ]

        return datasets
    
    def to_file(self, path):
        """
        Saves the dataset to a Parquet file.

        Parameters
        ----------
        path : str
            The path to save the Parquet file.
        """
        pq.write_table(self.table, f"{path}.parquet")

    @staticmethod
    def from_file(path):
        """
        Loads a DatasetBuilder from a .parquet file.

        Parameters
        ----------
        path : str
            The path to the Parquet file.

        Returns
        -------
        instane : DatasetBuilder
            The DatasetBuilder with the loaded dataset.
        """

        table = pq.read_table(path)
        instance = DatasetBuilder.__new__(DatasetBuilder)
        instance.table = table
        instance.dir = None
        instance.classes = None
        instance.regexes = None
        instance.norad_ids = None
        return instance

