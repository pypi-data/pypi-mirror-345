# ruff: noqa: E501, T201, S106
from typing import List

from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel, Field
from tqdm import tqdm

from crf_api_client.client import CRFAPIClient

client = CRFAPIClient(
    base_url="http://localhost:8000",
    token="***",
)

project_id = "dad401f0-33f5-49c8-ada0-ed141488b512"

table_name = "experiment_job_extraction"

columns = [
    {"name": "document_id", "type": "text"},
    {"name": "extracted_job4o", "type": "json"},
    {"name": "extracted_job4omini", "type": "json"},
]

table = client.create_table(project_id=project_id, table_name=table_name, columns=columns)
table_id = table.json()["id"]
tabble_id = ""
print(table.json())

version = client.create_table_version(project_id=project_id, table_id=table_id)

parsed_documents = client.get_table_data(project_id=project_id, table_name=table_name)


class JobDescriptionSchema(BaseModel):
    """Schema for extracting job description information."""

    job_title: str = Field(description="The title or name of the job position")
    company_name: str = Field(description="The name of the company offering the position")
    required_skills: List[str] = Field(
        description="List of skills, qualifications, or requirements needed for the job"
    )
    benefits: List[str] = Field(
        description="List of benefits, perks, or advantages offered with the position"
    )
    location_or_work_arrangement: str = Field(
        description="The location of the job or work arrangement (e.g., remote, hybrid, on-site in New York)"
    )


gtp4o_mini = OpenAI(model="gpt-4o-mini")
gtp4o_mini_structured = gtp4o_mini.as_structured_llm(output_cls=JobDescriptionSchema)

gtp4o = OpenAI(model="gpt-4o")
gtp4o_structured = gtp4o.as_structured_llm(output_cls=JobDescriptionSchema)

data = []


def extract_json_from_doc(doc):
    prompt_structured_extraction = """
    Extract structured information from the following job description:
    {text}
    """

    sample_job_description = doc["content"]

    input_msg = ChatMessage.from_str(
        prompt_structured_extraction.format(text=sample_job_description)
    )

    output = gtp4o_mini_structured.chat([input_msg])
    output2 = gtp4o_structured.chat([input_msg])
    # get actual object
    result = output.raw
    result2 = output2.raw
    result_json = result.model_dump_json()
    result2_json = result2.model_dump_json()
    return {
        "document_id": doc["document_id"],
        "extracted_job4o": result_json,
        "extracted_job4omini": result2_json,
    }


def main():
    for doc in tqdm(parsed_documents[:5]):
        data.extend(extract_json_from_doc(doc))

    client.write_table_data(
        project_id=project_id, table_name="experiment_job_extraction", data=data
    )


if __name__ == "__main__":
    main()
