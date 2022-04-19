
import time
import re
import sys
import os
import json
from collections import defaultdict
from elasticsearch import Elasticsearch


def populate_index(inputFilePath,logfile,INDEX_NAME,TYPE_NAME,index_populate_config):
    
    es = Elasticsearch()

    ic = 0
    ir = 0
    
    with open(inputFilePath, "r") as fin: 
        
            start = time.time()
            bulk_size = 500    # number of document processed in each bulk index
            bulk_data = []     # data in bulk index
            cnt = 0

            # Iterate through all "lines"/documents
            for line in fin: 
                    # Get information on each document (e.g., title, abstract, date)
                    cnt += 1
                    paperInfo = json.loads(line.strip())
                    data_dict = {}
                    data_dict["pmid"] = paperInfo.get("PMID", "-1")                                 # update PMID
                    data_dict["title"] = paperInfo.get("ArticleTitle")                              # ...... title
                    data_dict["abstract"] = paperInfo.get("Abstract", "").lower().replace('-', ' ') # ...... abstract
                    data_dict["full_text"] = paperInfo["full_text"].lower()                         # ...... full text
                    if index_populate_config['date']:                                               # ...... date
                        data_dict["date"] = str(paperInfo['PubDate'])
                    if index_populate_config['MeSH']:                                               # ...... MeSH metadata
                        data_dict["MeSH"] = paperInfo['MeshHeadingList']
                    if index_populate_config['location']:                                           # ...... location
                        data_dict["location"] = paperInfo['Country']
                    if index_populate_config['author']:                                             # ...... author
                        data_dict["author"] = paperInfo['AuthorList']
                    if index_populate_config['journal']:                                            # ...... journal
                        data_dict["journal"] = paperInfo['Journal']
                    
                    # Put current data into the bulk 
                    op_dict = {
                        "index": {
                            "_index": INDEX_NAME,
                            "_type": TYPE_NAME,
                            "_id": data_dict["pmid"]
                        }
                    }
                    bulk_data.append(op_dict)
                    bulk_data.append(data_dict) 

                    # Start Bulk indexing
                    if cnt % bulk_size == 0 and cnt != 0:
                        ic += 1
                        tmp = time.time()
                        es.bulk(index=INDEX_NAME, body=bulk_data, request_timeout = 500)
                        logfile.write("bulk indexing... %s, escaped time %s (seconds) \n" % ( cnt, tmp - start ) )
                        if ic%100 ==0:
                            print(" i bulk indexing... %s, escaped time %s (seconds) " % ( cnt, tmp - start ) )
                        bulk_data = []

            # indexing the remaining papers
            if bulk_data:
                ir +=1
                tmp = time.time()
                es.bulk(index=INDEX_NAME, body=bulk_data, request_timeout = 500)
                logfile.write("bulk indexing... %s, escaped time %s (seconds) \n" % ( cnt, tmp - start ) )
                if ir%100 ==0:
                    print(" r bulk indexing... %s, escaped time %s (seconds) " % ( cnt, tmp - start ) )
                bulk_data = []


            end = time.time()
            logfile.write("Finish PubMed meta-data indexing. Total escaped time %s (seconds) \n" % (end - start) )
            print("Finish PubMed meta-data indexing. Total escaped time %s (seconds) " % (end - start) )                    
