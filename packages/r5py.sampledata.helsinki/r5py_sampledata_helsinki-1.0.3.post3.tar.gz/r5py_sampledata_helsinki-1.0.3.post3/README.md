# An *r5py* sample data set that covers the centre of Helsinki

This package contains the following data sets:

## `r5py.sampledata.helsinki.gtfs`

General Transit Feed Specification ([GTFS](https://developers.google.com/transit/gtfs/reference))
data representing the public transport schedules, stop locations, lines, etc.
The data was created by Helsinki Region Transport (HLS) and obtained from
[TransitFeeds.com](https://transitfeeds.com/p/helsinki-regional-transport/735).

This GTFS data set is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).


## `r5py.sampledata.helsinki.osm_pbf`

A sample dataset representing OpenStreetMap data in protocolbuffer binary format (PBF),
which was obtained from [Geofabrik](https://download.geofabrik.de/europe/finland.html).
The data is licensed under the [Open Data Commons Open Database License (ODbL)](https://www.openstreetmap.org/copyright).

We used [osmium](https://osmcode.org/osmium-tool/) to crop the data to the given extent.


## `r5py.sampledata.helsinki.population_grid`

A sample dataset representing the population of Helsinki.
The data is obtained from Helsinki Region Environmental Services (HSY).
The data is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The data is downloaded from the Helsinki Region Environmental Services’ (HSY)
*Web Feature Service (WFS)* endpoint (see the
[Helsinki Region Infoshare’s data description](https://hri.fi/data/en_GB/dataset/vaestotietoruudukko)).
We used [a script](scripts/download_population_grid.py), that we share with this package, to download
the data set and adapt it to the requirements of r5py’s documentation. Namely, we:

- reindexed the data,
- omitted some columns,
- renamed the remaining columns from Finnish to English
- reprojected the data to "EPSG:4326", and
- extracted centroids from the grid polygons (for the point data set)


## `r5py.sampledata.helsinki.elevation_model` 

A sample data set representing the terrain of Helsinki city centre.
The data was obtained from the City of Helsinki.
The data is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The data was downloaded from the City of Helsinki’s *Web Coverage Service
(WCS)*’ endpoint (see the [Helsinki Region Inforshare’s data
description](https://hri.fi/data/fi/dataset/helsingin-korkeusmalli)).  We used
[a script](scripts/download_elevation_model.py), that we share with this
package, to download an crop the data to the sample data extent.
