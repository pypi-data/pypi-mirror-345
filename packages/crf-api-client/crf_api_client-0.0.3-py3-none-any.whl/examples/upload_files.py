import os

from crf_api_client.client import CRFAPIClient

client_local = CRFAPIClient(
    base_url="http://localhost:8000",
    token="***",
)

project_id = "bf32f18f-c4d5-4500-8571-7dd467834e47"

base_path = "/Users/max/Downloads/jobs_desc/"
files = os.listdir(base_path)
files_path = [base_path + f for f in files[-5:]]

# ['/Users/max/Downloads/jobs_desc/dili_founding_engineer__platform.pdf',
#  '/Users/max/Downloads/jobs_desc/tarsal_software_engineer__backend.pdf',
#  '/Users/max/Downloads/jobs_desc/drillbit_founding_engineer.pdf',
#  '/Users/max/Downloads/jobs_desc/kino_ai_front_end_engineer.pdf',
#  '/Users/max/Downloads/jobs_desc/enerjazz_phone_sales.pdf']

response = client_local.bulk_upload_files(project_id=project_id, files_paths=files_path)

print(response)
