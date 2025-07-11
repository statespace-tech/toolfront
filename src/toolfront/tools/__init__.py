from toolfront.tools.api import inspect_endpoint, request_api, search_endpoints
from toolfront.tools.database import inspect_table, query_database, sample_table, search_tables
from toolfront.tools.library import read_document, search_documents

database_tools = [inspect_table, query_database, sample_table, search_tables]

api_tools = [inspect_endpoint, request_api, search_endpoints]

library_tools = [search_documents, read_document]
