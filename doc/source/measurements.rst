Measurements
************

tourbillon-uwsgi collects metrics about workers.

Please refers to  `https://uwsgi-docs.readthedocs.org/en/latest/StatsServer.html <https://uwsgi-docs.readthedocs.org/en/latest/StatsServer.html>`_ and `https://github.com/unbit/uwsgitop <https://github.com/unbit/uwsgitop>`_ for more information.


uWSGI stats
===========

tourbillon-uwsgi query the stats server and store metrics in the ``uwsgi_stats`` series. 
Each datapoint is tagged with the worker id and the hostname and the values collected are:


Tags
----
	* **host**: hostname
	* **worker** the id of the worker

Fields
------

	* **requests**: number of requests processed by the worker since the last datapoint
	* **exceptions**: number of exceptions since the last datapoint
	* **tx**: data transmitted by the worker since the last datapoint
	* **rss**: current rss memory used by the worker
	* **vsz**: current vsz memory used by the worker
	* **avg_rt**: average request time 
	* **wid**: worker id
	* **status**: current worker status (idle, busy)


