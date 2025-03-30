import os
import uuid
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model
from langchain_elasticsearch import ElasticsearchRetriever
from sentence_transformers import SentenceTransformer
from langchain.prompts import PromptTemplate
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages


# ================== Elasticsearch Config ===================
class ElasticsearchConfig:
    USERNAME = "elastic"
    PASSWORD = "changeme"
    URL = f"http://{USERNAME}:{PASSWORD}@localhost:9200"
    INDEX = "data"
    DENSE_VECTOR_FIELD = "embeddingVector"
    TEXT_FIELD = "Tittle"

# ================== Embedding Model ===================
class EmbeddingModel:
    def __init__(self, model_name="dangvantuan/vietnamese-embedding"):
        self.model = SentenceTransformer(model_name)
    
    def get_embedding(self, text):
        if not text or not isinstance(text, str) or text.strip() == "":
            return None
        return self.model.encode(text).tolist()

# ================== LLM Service ===================
class LLMService:
    def __init__(self, model_name="llama3-8b-8192", provider="groq"):
        os.environ["GROQ_API_KEY"] = "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"
        self.llm = init_chat_model(model_name, model_provider=provider)
    
    def generate_answer(self, question, context):
        prompt = PromptTemplate.from_template(
            """
            Bạn là một chatbot trợ giúp về ngôn ngữ lập trình Python. Hãy trả lời câu hỏi dựa theo ngữ cảnh là những câu trả lời có liên quan đến câu hỏi cộng với hiểu biết của bạn.
            Nếu cảm thấy không chắc chắn hãy hỏi lại người dùng để làm rõ câu hỏi.

            Câu hỏi: {question}

            Ngữ cảnh : {context}

            Đưa ra câu trả lời bằng tiếng Việt hoàn toàn không được dính một tí tiếng Anh nào
            """
        )
        return self.llm.invoke(prompt.format(question=question, context=context))

# ================== BotLLM ===================
class BotLLM:
    class State(TypedDict):
        messages: Annotated[list, add_messages]
        question: str
        context: str

    def __init__(self):
        # Embedding
        self.embedding_model = EmbeddingModel()

        # Retriever
        self.retriever = ElasticsearchRetriever.from_es_params(
            index_name=ElasticsearchConfig.INDEX,
            body_func=self._hybrid_query,
            content_field="Answer 1",
            url=ElasticsearchConfig.URL
        )

        # LLM
        self.llm_service = LLMService()

        # Memory
        self.memory = MemorySaver()

        # Workflow
        self.workflow = StateGraph(state_schema=self.State)
        self._build_workflow()
        self.app = self.workflow.compile(checkpointer=self.memory)

    def _hybrid_query(self, search_query):
        vector = self.embedding_model.get_embedding(search_query)
        return {
            "retriever": {
                "rrf": {
                    "retrievers": [
                        {"standard": {"query": {"match": {ElasticsearchConfig.TEXT_FIELD: search_query}}}},
                        {"knn": {"field": ElasticsearchConfig.DENSE_VECTOR_FIELD, "query_vector": vector, "k": 5, "num_candidates": 10}}
                    ],
                    "rank_constant": 60
                }
            },
            "size": 1
        }

    def _retrieve_context(self, state: State):
        retrieved_docs = self.retriever.invoke(state["question"])
        context = " ".join([doc.page_content for doc in retrieved_docs])
        return {"context": context}

    def _generate_answer(self, state: State):
        response = self.llm_service.generate_answer(state["question"], state["context"])
        return {"messages": [response]}

    def _build_workflow(self):
        self.workflow.add_node("retrieve_context", self._retrieve_context)
        self.workflow.add_edge(START, "retrieve_context")
        self.workflow.add_node("generate_answer", self._generate_answer)
        self.workflow.add_edge("retrieve_context", "generate_answer")
        self.workflow.add_edge("generate_answer", END)

    def get_response(self, user_input, thread_id=None):
        if not thread_id:
            thread_id = uuid.uuid4()
        config = {"configurable": {"thread_id": thread_id}}
        result = self.app.invoke(
            {"messages": user_input, "question": user_input, "context": ""},
            config
        )
        message = result["messages"][-1].content if "messages" in result else "Xin lỗi, tôi chưa hiểu câu hỏi của bạn."
        return message