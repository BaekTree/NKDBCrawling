# -*- coding: utf-8 -*-
import os
import sys

def transport_from_mongo_to_index():
    # move to Transporter folder
    # print os.path.abspath(os.curdir)
    os.chdir("/usr/local/bin")
    # print os.path.abspath(os.curdir)
    os.system("transporter run pipeline.js")
    print("Success transporting the data from mongodb to ES index!")

if __name__ == "__main__":
    name = "nkdboard" # Only change this variable to the name of the bulletin board inside information.txt!
    os.environ['mongo_es_name'] = name
    command = "echo $mongo_es_name"
    os.system(command)
    # setting for transporting MongoDB to ES index
    os.system("curl -X PUT 'localhost:8080/" + name + "?pretty' -H 'Content-Type: application/json' -d @analyzer_index.json")
    os.system("curl -X PUT 'localhost:8080/" + name + "/" + name + "/_mapping?include_type_name=true' - H 'Content-Type: application/json' - d @update_index.json")
    # execute transporter
    transport_from_mongo_to_index()
