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

**Chapter Worker:**

Finds chapter wav files, splits them into verses and converts all to mp3 files  

`python chapter_worker.py --trace --verbose -i /path/to/input/directory`

**Verse Worker:**

Finds verse wav files and converts them into mp3 files  

`python verse_worker.py --trace --verbose -i /path/to/input/directory`

**TR Worker:**

Finds verse wav and mp3 files, groups them into books and chapters and creates TR files  

`python tr_worker.py --trace --verbose -i /path/to/input/directory`

**options:**  

`-t (--trace)` - (Optional) Enable tracing output  
`-v (--verbose)` - (Optional) Enable logs from subprocess  
`-i (--input-dir)` - Input directory (Normally ftp root dir)  