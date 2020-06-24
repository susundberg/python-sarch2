Sarch2 -  Simple ARCHiving 2
=========================================

Python based tool for linux systems file management


Features:
-----------
* System for storing (binary) files, no central repository required (but sure you can use it in centralized manner).
* Import files and sort them with date-time (sarch2 import) and remember previously deleted 
* Not version control -> near zero overhead, but you still get some information of the file (created, deleted)
* Simple command line interface 
* External backup repositories supported by RSYNC (sarch2 export)


Example use cases:
-----------
* Photo managment - import photos from SD-card - sort by date-time
* Document managment - archive with date-time

Importing existin backup stuff:
-----------
1. Create local machine repository
1.1. Add all wanted files

2. Create remote repository - EMPTY
3. Do sync -- the sync is done with RSYNC so no extra files should be transferred 

BEWARE THIS WILL REMOVE ALL FILES THAT ARE NOT IN LOCAL MACHINE FROM REMOTE

( so you might first run rsync from remote to local to make sure you have the remote files at local )


