# SoundCloud Track Scrapper
This script allows you to check the followers of a SoundCloud user and get the track count.  
If a follower has tracks, their track url and the first 5 tracks will be printed to the console and added to a database to avoid being checked again in the future.

## Usage

Install requirements first

Add your client_id in line 100 then run main.py

The script will prompt you to choose between entering a SoundCloud URL to check followers or viewing all entries in the database.  
If you choose to view all entries, the script will display all checked followers stored in the database.  

Enter a SoundCloud URL in the format:  

https://soundcloud.com/username/

For example:  
https://soundcloud.com/billieeilish  
or  
https://soundcloud.com/billieeilish/sets  
the text after the username gets ignored so you dont need to copy url from the mainpage
