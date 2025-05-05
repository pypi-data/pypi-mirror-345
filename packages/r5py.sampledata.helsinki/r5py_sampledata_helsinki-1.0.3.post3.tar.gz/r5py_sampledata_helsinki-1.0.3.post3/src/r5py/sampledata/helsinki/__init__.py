#!/usr/bin/env python3


"""Sample data set for r5py, covering Helsinki city centre, downloaded upon first access."""


__version__ = "1.0.3.post3"
__all__ = ["__version__"]


try:
    try:
        from r5py.util.sample_data_set import SampleDataSet
    except ImportError:
        from r5py.util.data_set import DataSet as SampleDataSet

    BASE_URL = (
        f"https://github.com/r5py/r5py.sampledata.helsinki/raw/v{__version__}/data/"
    )

    elevation_model = SampleDataSet(
        f"{BASE_URL}/elevation_model_2021.tif",
        "455c9ebdf4a7e44c265a1a7f5ca75634f438c3d80c6b0f22acbb7511199261a1",
    )
    gtfs = SampleDataSet(
        f"{BASE_URL}/helsinki_gtfs.zip",
        "8ecccde3e76441b47e90c7f311fc57a8d38df92e9ee592e8f440a9b7e3abf228",
    )
    osm_pbf = SampleDataSet(
        f"{BASE_URL}/kantakaupunki.osm.pbf",
        "94f1a86cb8defaca4b6eea64fba699fde957a848151642b2ad2599bd5ad1e858",
    )
    population_grid = SampleDataSet(
        f"{BASE_URL}/helsinki_population_grid_2020.gpkg",
        "b421cb753fa00771b0e1d853422a0f485abb81f1bb2961eb832fa498612d7cd4",
    )

    __all__ += [
        "gtfs",
        "osm_pbf",
        "population_grid",
    ]

except ImportError as exception:
    raise ImportError("Install r5py>=0.1.0 to use the sample data sets") from exception
