import os
import sys

information_file = open("../information.txt", 'r')
while True:
    line = information_file.readline()
    if not line: 
        break
    # here
    arr = line.split(',')    
    #mongo_database = arr[0]
    #mongo_collection = arr[0]
    mongo_database = "nkdb"
    mongo_collection = "nkdb"
    execute_file_name = arr[1]
    os.chdir("/home/eunjiwon/crawlNKDB/crawlNKDB/spiders")
    command = "scrapy crawl " + execute_file_name
    os.system(command)
    print("Finish following command: " + command)

information_file.close()

'''
mongo_database = "nuacboard"
mongo_collection = "nuacboard"
execute_file_name = "crawlbinaryfile"

os.chdir("/home/eunjiwon/crawlNKDB/crawlNKDB/spiders")
command = "scrapy crawl " + execute_file_name
os.system(command)
'''

