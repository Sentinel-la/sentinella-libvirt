Configure
*********


Create the tourbillon-uwsgi configuration file
===============================================

You must create the tourbillon-celery configuration file in order to use tourbillon-uwsgi.
By default, the configuration file must be placed in **/etc/tourbillon/conf.d** and its name
must be **uwsgi.conf**.

The tourbillon-uwsgi configuration file looks like: ::

	{
		"database": {
			"name": "uwsgi",
			"duration": "365d",
			"replication": "1"
		},
		"hostname": "localhost",
		"port": 9797,
		"frequency": 0.2
	}


You can customize the database name, the host and port where the uWSGI stats server listen to 
and the collect interval.


Enable the tourbillon-uwsgi metrics collector
==============================================

To enable the tourbillon-uwsgi metrics collector types the following command: ::

	$ sudo -i tourbillon enable tourbillon.uwsgi=get_uwsgi_stats


