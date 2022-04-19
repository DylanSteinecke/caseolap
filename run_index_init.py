import json
from elasticsearch import Elasticsearch

# Index Parameters
INDEX_NAME = "pubmed"
TYPE_NAME = "pubmed_meta"
NUMBER_SHARDS = 1 # keep this as one if no cluster
NUMBER_REPLICAS = 0 
index_init_config_file = './config/index_init_config.json' # input file path
case_sensitive = True # True: Make the indexing case sensitive, False: Indexes text as lower case

# Start Indexing
if __name__ == '__main__':

    # Import index initial configuration file
    with open(index_init_config_file,'r') as f:
        index_init_config = json.load(f) 
    
    # Create a index request body
    request_body = {
        "settings": {
            "number_of_shards": NUMBER_SHARDS,
            "number_of_replicas": NUMBER_REPLICAS},
        "mappings": {
            TYPE_NAME: {
                "properties": index_init_config}}}
    if case_sensitive == True:
        request_body["settings"]["analysis"] = {
            "analyzer":{
                "casesensitive_text": {
                    "type":"custom",
                    "tokenizer":"standard",
                    "filter": ["stop"]}}}
       
    # Start elasticsearch
    es = Elasticsearch()
              
    # Delete old index if exist
    if es.indices.exists(INDEX_NAME):
             res = es.indices.delete(index = INDEX_NAME)
             print("Deleting index %s , Response: %s" % (INDEX_NAME, res))

    # Create new index   
    res = es.indices.create(index = INDEX_NAME, body = request_body)
    print("Successfully crested index %s , Response: %s" % (INDEX_NAME, res))
