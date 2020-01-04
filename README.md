# python-sarch2
Python based tool for linux systems file management



Importing existin backup stuff:

1. Create local machine repository
1.1. Add all wanted files

2. Create remote repository - EMPTY
3. Do sync -- the sync is done with RSYNC so no extra files should be transferred 

BEWARE THIS WILL REMOVE ALL FILES THAT ARE NOT IN LOCAL MACHINE FROM REMOTE

( so you might first run rsync from remote to local to make sure you have the remote files at local )


