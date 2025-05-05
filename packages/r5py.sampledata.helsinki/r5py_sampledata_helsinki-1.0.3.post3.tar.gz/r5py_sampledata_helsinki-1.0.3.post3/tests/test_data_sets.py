#!/usr/bin/env python3


try:
    from r5py.util.sample_data_set import SampleDataSet
except ImportError:
    from r5py.util.data_set import DataSet as SampleDataSet


class TestDataSets:
    def test_download_and_checksum(self, data_sets):
        for data_set in data_sets:
            assert isinstance(data_set, SampleDataSet)
            assert data_set.exists()
