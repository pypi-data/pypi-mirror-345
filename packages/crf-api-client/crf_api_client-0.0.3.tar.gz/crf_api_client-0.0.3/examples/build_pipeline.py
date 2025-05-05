from crf_api_client.client import CRFAPIClient

client_local = CRFAPIClient(
    base_url="http://localhost:8000",
    token="***",
)

project_id = "bf32f18f-c4d5-4500-8571-7dd467834e47"
table_name = "neo4j_all_population"

response = client_local.build_table(
    project_id=project_id, table_name=table_name, pipeline_name="v0", mode="recreate"
)

print(response)
