from crf_api_client.client import CRFAPIClient

client_local = CRFAPIClient(
    base_url="http://localhost:8000",
    api_key="***",
)

client_prod = CRFAPIClient(
    base_url="https://api.crf.ai",
    api_key="***",
)

project_id = "bf32f18f-c4d5-4500-8571-7dd467834e47"
table_name = "chunks"

chunks = client_prod.get_table_data(project_id, table_name)

print("[+] Retrieved %d chunks from production" % len(chunks))

client_local.write_table_data(
    project_id=project_id, table_name=table_name, data=chunks, override=True
)

print("[+] Wrote %d chunks to local" % len(chunks))

local_chunks = client_local.get_table_data(project_id, table_name)

print("[+] Retrieved %d chunks from local" % len(local_chunks))
