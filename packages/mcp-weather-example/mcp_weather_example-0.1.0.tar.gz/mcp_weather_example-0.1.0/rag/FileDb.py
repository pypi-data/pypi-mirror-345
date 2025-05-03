# _*_ coding : utf-8 _*_
# @Time : 2025-05-03 9:39
# @Author : liubiao
# @File : FileDb
# @Project : mcp-weather-example


import os

from llama_index.readers.dashscope.base import DashScopeParse
from llama_index.readers.dashscope.utils import ResultType

os.environ['DASHSCOPE_API_KEY'] = "sk-a34904e683b648b488f3bee9e979ba86"
os.environ['DASHSCOPE_WORKSPACE_ID'] = "llm-m6x8j8b3p1kfzlqt"

# # 多个独立文件
# file = [
#     # 需要解析的文件，支持pdf,doc,docx
#     "file_lib/3-绩效考核管理制度-2025.pdf",
#     "file_lib/4-定岗定级薪酬管理制度-2025.pdf",
#     "file_lib/博文OA-员工操作指南.docx"
# ]
# parse = DashScopeParse(result_type=ResultType.DASHSCOPE_DOCMIND)
# documents = parse.load_data(file_path=file)

## 文件解析
print("文件解析开始")
# 使用SimpleDirectoryReader读取文件夹下所有文件
from llama_index.core import SimpleDirectoryReader
parse = DashScopeParse(result_type=ResultType.DASHSCOPE_DOCMIND)
file_extractor = {".pdf": parse, '.doc': parse, '.docx': parse}
documents = SimpleDirectoryReader(
   "./file_lib", file_extractor=file_extractor
).load_data(num_workers=1)


print("文件解析完成")
print("将解析好的文件加载到索引中...开始")

from llama_index.indices.managed.dashscope import DashScopeCloudIndex

# create a new index
index = DashScopeCloudIndex.from_documents(
    documents,
    "my_first_index",
    verbose=True,
)
print("将解析好的文件加载到索引中...完成")
print("读取索引")

my_index = DashScopeCloudIndex("my_first_index")


# convert from index
retriever = index.as_retriever()

# or initialize from DashScopeCloudRetriever
# from llama_index.indices.managed.dashscope.retriever import DashScopeCloudRetriever
# retriever = DashScopeCloudRetriever("my_first_index")

nodes = retriever.retrieve("博文公司的考勤制度")

print("测试召回")
print(nodes)
#
#
# from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
#
# dashscope_llm = DashScope(
#   model_name=DashScopeGenerationModels.QWEN_MAX, api_key=os.environ["DASHSCOPE_API_KEY"]
# )
# query_engine = index.as_query_engine(llm=dashscope_llm)

#
# # add documents to index
# index.insert(documents)
#
# # delete documents from index
# doc_id = "doc_123"
# index.delete_ref_doc([doc_id])