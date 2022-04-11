# facebookfriendsonmap
Not so easy. And forbidden by the ToS of Facebook. But I succeeded. It is a lot of copy, paste, trial and error, so I'm sure there will be a better way to program this. But the result counts doesn't it :)


Steps:
1) scrape
2) geocode
3) prepare the SQL statement with http://www.convertcsv.com/csv-to-sql.htm
4) import the data in your MySQL 
5) showmap

The code has to be adapted to your wishes, because I split up the facebookfriendslist into numbered files. Maybe I will make a one click solution one day.

I also saved the file produced at step one to my harddisk. 
By manipulating the html-file (don't ask me how, I think I replaced "<IMG SRC=" with xxx from the sourcefile, copied everything in a texteditor and did some manipulations, I could take the filenames of the profile photos. 

I resized the photofiles and uploaded them to my server.

I loaded the CSV file in Excel and added the filenames. I had some problems because of the accents in the names so take care! 

Excel doesn't allow you to save a CSV like we need in step 3, so I used the macro given in https://support.microsoft.com/en-us/help/291296/procedure-to-export-a-text-file-with-both-comma-and-quote-delimiters-i

At the end my table 'facebookfriends' looks like this. Take care, for column 4 (facebook-id) you need to choose for bigint, because they are large numbers!
	1	idPrimaire sleutel	int(11)			
	2	photo	varchar(55)		
	3	NAME_WITH_ACCENTS	varchar(38)		
	4	facebook_id	bigint(20)		
	5	name	varchar(38)		
	6	place	varchar(387)		
	7	accuracy	varchar(16)		
	8	formatted_address	varchar(68)		
	9	google_place_id	varchar(27)		
	10	input_string	varchar(387)		
	11	latitude	decimal(18,15)			
	12	longitude	decimal(21,17)			
	13	number_of_results	int(11)			
	14	postcode	varchar(7)		
	15	status	varchar(2)		
	16	type	varchar(77)		




