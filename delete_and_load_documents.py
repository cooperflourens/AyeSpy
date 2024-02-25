import argparse

import pandas as pd
from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)
from transformers import BertModel, BertTokenizer

import postgres_utils
import milvus_utils
import embedding_utils

def create_sub_dictionary(original_dict, keys_to_remove):
    return {key: value for key, value in original_dict.items() if key not in keys_to_remove}

# Take in data files as command line argument
# Redundancy check

# Prune vector database before query and fetch

data_path = "congressional_hearings_test2.csv"
pd.read_csv(data_path)

postgres_db_name = "seek"
postgres_user = "seek_user"
password = "secret"
host = "localhost"
postgres_db_table_name = "documents"
postgres_db_table_cols = {
    "id": "SERIAL PRIMARY KEY", 
    "date": "TIMESTAMP", 
    "name": "TEXT", 
    "quote": "TEXT", 
    "document": "TEXT", 
    "vector_id": "TEXT"
    }

milvus_collection_name = "seek_milvus"
milvus_alias = "default"
milvus_host = "localhost"
milvus_port = "19530"
# milvus_num_entities = 
milvus_vector_dimensionality = 768

model = BertModel.from_pretrained('bert-base-uncased')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Connect to your postgres DB
conn = postgres_utils.connect(postgres_db_name, postgres_user, password, host)
postgres_utils.remove_table(conn, postgres_db_table_name)

table_exists = postgres_db_table_name in postgres_utils.get_all_tables(conn)
if not table_exists:
    postgres_utils.create_table(conn, postgres_db_table_name, postgres_db_table_cols)

connections.connect(milvus_alias, host=milvus_host, port=milvus_port)
utility.drop_collection(collection_name=milvus_collection_name)

if not utility.has_collection(milvus_collection_name):
    milvus_collection = milvus_utils.create_milvus_collection(milvus_collection_name, milvus_vector_dimensionality)
else:
    milvus_collection = Collection(milvus_collection_name)

cong_hear_df = pd.read_csv(data_path)
# print(cong_hear_df)

postgres_utils.insert_document_data(conn, postgres_db_table_name, create_sub_dictionary(postgres_db_table_cols, ["id", "vector_id"]), cong_hear_df)

milvus_utils.insert_embeddings(conn, milvus_collection, tokenizer, model)

# print(postgres_utils.head_postgresql(conn, postgres_db_table_name, 10))
# print(milvus_utils.head_milvus(milvus_collection_name, 10))

query_vector = embedding_utils.generate_embedding("Abortion", tokenizer, model)
filtered_keys = postgres_utils.filter_by_name(conn, postgres_db_table_name, "Markwayne Mullin")
print(filtered_keys)
print(milvus_utils.search_with_primary_keys(conn, milvus_collection, query_vector, filtered_keys, 10))