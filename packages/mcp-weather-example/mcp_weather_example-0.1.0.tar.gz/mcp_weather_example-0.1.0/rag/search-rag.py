# _*_ coding : utf-8 _*_
# @Time : 2025-05-03 10:06
# @Author : liubiao
# @File : search-rag
# @Project : mcp-weather-example
from llama_index.indices.managed.dashscope import DashScopeCloudRetriever
from llama_index.indices.managed.dashscope import DashScopeCloudIndex

import os

from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels

os.environ['DASHSCOPE_API_KEY'] = "sk-a34904e683b648b488f3bee9e979ba86"
os.environ['DASHSCOPE_WORKSPACE_ID'] = "llm-m6x8j8b3p1kfzlqt"
my_index = DashScopeCloudIndex("my_first_index")


def search_doc(keyword:str) :
    # convert from index
    retriever = DashScopeCloudRetriever("my_first_index")
    # or initialize from DashScopeCloudRetriever
    # from llama_index.indices.managed.dashscope.retriever import DashScopeCloudRetriever
    # retriever = DashScopeCloudRetriever("my_first_index")

    nodes = retriever.retrieve("博文公司的考勤制度")
    return nodes