# fetcher-pipeline

### Requirements

Python 3.7

### How to use  

#### worker.sh script:  

`./worker.sh -t -v -i /path/to/input/directory`  

**options:**  

`-t (--trace)` - (Optional) Enable tracing output  
`-v (--verbose)` - (Optional) Enable logs from subprocess  
`-i (--input-dir)` - Input directory (Normally ftp root dir)  

An example to write log to a file:  

`./worker.sh -t -v -i /path/to/input/directory 2>> path/to/file.log`

Recommended to run scripts as an ftp user to preserve permissions and ownership. For example:  

`sudo -u ftpuser ./worker.sh -t -v -i /path/to/input/directory`

Alternatively you can run every python script separately  

#### python scripts:  

`python chapter_worker.py --trace --verbose -i /path/to/input/directory`

`python verse_worker.py --trace --verbose -i /path/to/input/directory`

`python tr_worker.py --trace --verbose -i /path/to/input/directory`

**options:**  

`-t (--trace)` - (Optional) Enable tracing output  
`-v (--verbose)` - (Optional) Enable logs from subprocess  
`-i (--input-dir)` - Input directory (Normally ftp root dir)  