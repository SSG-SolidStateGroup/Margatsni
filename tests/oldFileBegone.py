mport os
from datetime import datetime

## This script is designed to (a) provide an example of how to
## get the creation date (or last modified date) of a file
## or folder, (b) filter through the most recent modified date per
## file, and (c) delete the oldest files based off age (validity)

# Create the directory to search for files
# The syntax is folder = '/Path/to/yourDir/'
files = 'C:/Users/B.Cherry/Desktop'

# Create a list of those files based on the directory
fileList = os.listdir(files)

# Print an array of those file names and folder names alphabetically a -> z
print(fileList)

# For each of the files/folders in the fileList, print the creation date,
# or the most recent modified date
for plsWork in fileList:
    #print(os.stat(fileList).st_ctime)
    #print(os.stat('C:/Users.B.Cherry/Desktop/' + plsWork).st_ctime)
    try:
        modifiedTime = os.path.getmtime(plsWork) #.strftime('%Y-%m-%d %H:%M:%S')
        print(modifiedTime)
    except OSError:
        mtime = 0
        print("File wasn't found!")
    
