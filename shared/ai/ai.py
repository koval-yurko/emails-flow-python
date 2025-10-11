import json
import os
import re
import time
from typing import Type, TypeVar
from langchain_aws import ChatBedrock
from langchain_xai import ChatXAI
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import PromptTemplate

from .output import ResponseFormatter, PostItem
from .prompt import PROMPT_EMAIL_PROCESS

modelId = "eu.anthropic.claude-sonnet-4-20250514-v1:0"
# modelId = 'eu.amazon.nova-pro-v1:0'


class LLMEngine:

    def __init__(self):
        self.__llm1 = ChatBedrock(
            model=modelId,
            region_name="eu-central-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            model_kwargs={"max_tokens": 5000},
        )

        self.__llm = ChatXAI(
            xai_api_key=os.getenv("XAI_API_KEY"),
            model="grok-4-fast-non-reasoning",  # "grok-4-fast-reasoning",
        )

        self.__prompt_template = PromptTemplate.from_template(PROMPT_EMAIL_PROCESS)

        self.__output_parse = RunnableLambda(lambda x: self.__parse_nova_structured(x))

        self.__chain = self.__prompt_template | self.__llm | self.__output_parse

    def __parse_nova_structured(self, output: BaseMessage) -> ResponseFormatter:
        schema = ResponseFormatter
        response_content = output.content

        end_time = time.time()
        duration = end_time - self.__start_time
        print(f"get_email_summary completed in {duration:.2f} seconds")
        print(
            f"input_tokens - {output.usage_metadata['input_tokens']}, output_tokens - {output.usage_metadata['output_tokens']}"
        )

        """Custom parser for Nova models"""
        # Try to extract JSON from response
        content = response_content.strip()

        # Remove common prefixes
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        # Find JSON in response
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                data = json.loads(json_str)
                return schema(**data)
            except:
                pass

        # Fallback: try parsing the entire content
        try:
            data = json.loads(content)
            return schema(**data)
        except Exception as e:
            raise ValueError(f"Could not parse structured output: {e}")

    def get_email_summary(self, email_content: str) -> list[PostItem]:
        self.__start_time = time.time()

        res: ResponseFormatter = self.__chain.invoke(
            {
                "email_content": email_content,
                "json_schema": ResponseFormatter.model_json_schema(),
            }
        )

        return res.posts
