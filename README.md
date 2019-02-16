# atmos-rest-downloader
Very fast rest api based recursive atmos file downloader

This software leverages multi processing of python with rest api of atmos to recursively scan all files in the storage and download them. Only types that are supported are directory and regular. Other special types like taglink are not supported by this script.

## Configure 
### Target Conf
Set the pool size for multi processing. 
Set write location for data.
Set location to log errors
Information about the target atmos.(ip, port, uid , secret)

```write_location= "/data"
errorlogfile= "./err.txt"
host, port, uid, secret = "0.0.0.0", 80, "", ""
```
### Recursive Folder downloader

```
startingfolder= ""
```

Starting directory can be specified. Starts from root if empty

### Objects downloader
```
max_queue_length = 500
objects_list_file= "objects.txt"
```
File has a list of plaintext object ids.

## Requirements
EsuRestApi.py from https://github.com/EMCECS/atmos-python

After running the script, number of threads will be spawned. 


