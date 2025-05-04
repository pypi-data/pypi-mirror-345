import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from lancedb.index import FTS
from pydantic import Field
from opsmate.config import config
from typing import List, Any, Dict
import uuid
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
from functools import cache
from openai import AsyncOpenAI
from lancedb.rerankers import (
    OpenaiReranker,
    AnswerdotaiRerankers,
    CohereReranker,
    RRFReranker,
)
from opsmate.dbq.dbq import enqueue_task, dbq_task, Task as DbqTask
from opentelemetry import trace
from functools import cache
from datetime import timedelta, UTC
from sqlmodel import Session
import structlog

logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)


class Category(Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTENANCE = "maintenance"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    PRODUCTION = "production"
    OBSERVABILITY = "observability"
    PROMETHEUS = "prometheus"


class EmbeddingClient(ABC):
    @abstractmethod
    async def embed(self, query: str) -> List[float]:
        pass


class OpenAIEmbeddingClient(EmbeddingClient):
    def __init__(self, model_name: str = config.embedding_model_name):
        self.model_name = model_name

    async def embed(self, query: str) -> List[float]:
        response = await self.embed_client().embeddings.create(
            input=query, model=self.model_name
        )
        return response.data[0].embedding

    @cache
    def embed_client(self):
        return AsyncOpenAI()


class SentenceTransformersEmbeddingClient(EmbeddingClient):
    def __init__(self, model_name: str = config.embedding_model_name):
        self.model_name = model_name

    async def embed(self, query: str) -> List[float]:
        return self.model().encode(query)

    @cache
    def model(self):
        import sentence_transformers

        return sentence_transformers.SentenceTransformer(self.model_name)


@cache
def get_embedding_client():
    if config.embedding_registry_name == "openai":
        return OpenAIEmbeddingClient()
    elif config.embedding_registry_name == "sentence-transformers":
        return SentenceTransformersEmbeddingClient()
    else:
        raise ValueError(
            f"Unsupported embedding client: {config.embedding_registry_name}"
        )


@cache
def get_reranker():
    match config.reranker_name:
        case "answerdotai":
            try:
                import transformers  # noqa: F401

                logger.info("using answerdotai reranker")
                return AnswerdotaiRerankers(column="content", verbose=0)
            except ImportError:
                logger.info(
                    "answerdotai reranker not installed, using openai reranker",
                    model_name="gpt-4o-mini",
                )
                return OpenaiReranker(column="content", model_name="gpt-4o-mini")
        case "openai":
            logger.info("using openai reranker", model_name="gpt-4o-mini")
            return OpenaiReranker(column="content", model_name="gpt-4o-mini")
        case "cohere":
            logger.info("using cohere reranker", model_name="rerank-english-v3.0")
            return CohereReranker(
                column="content",
                model_name="rerank-english-v3.0",
            )
        case "rrf":
            logger.info("using rrf reranker")
            return RRFReranker()
        case _:
            logger.info("no reranker selected")
            return None


async def aconn():
    """
    Create an async connection to the lancedb based on the config.embeddings_db_path
    """
    return await lancedb.connect_async(config.embeddings_db_path)


def conn():
    """
    Create a connection to the lancedb based on the config.embeddings_db_path
    """
    return lancedb.connect(config.embeddings_db_path)


async def init_table():
    """
    init the knowledge store table based on the config.embeddings_db_path
    """
    with tracer.start_as_current_span("init_table") as span:
        span.set_attributes(
            {
                "embedding_registry_name": config.embedding_registry_name,
                "embedding_model_name": config.embedding_model_name,
            }
        )

        registry = get_registry()

        # embeddings is the embedding function used to embed the knowledge store
        embeddings = registry.get(config.embedding_registry_name).create(
            name=config.embedding_model_name
        )

        class KnowledgeStore(LanceModel):
            uuid: str = Field(
                description="The uuid of the runbook", default_factory=uuid.uuid4
            )
            id: int = Field(description="The id of the knowledge")
            # summary: str = Field(description="The summary of the knowledge")
            categories: List[str] = Field(description="The categories of the knowledge")
            data_source_provider: str = Field(
                description="The provider of the data source"
            )
            data_source: str = Field(description="The source of the knowledge")
            metadata: str = Field(
                description="The metadata of the knowledge json encoded"
            )
            path: str = Field(description="The path of the knowledge", default="")
            vector: Vector(embeddings.ndims()) = embeddings.VectorField()
            content: str = (
                embeddings.SourceField()
            )  # source field indicates the field will be embed
            created_at: datetime = Field(
                description="The created at date of the knowledge",
                default_factory=datetime.now,
            )

        db = await aconn()

        with tracer.start_as_current_span("create_table"):
            table = await db.create_table(
                "knowledge_store", schema=KnowledgeStore, exist_ok=True
            )
        with tracer.start_as_current_span("create_index"):
            await table.create_index("content", config=FTS())
            logger.info("knowledge store indexed", table=table)
        return table


class ReindexTableTask(DbqTask):
    async def on_success(self, task, ctx: Dict[str, Any]):
        session: Session = ctx["session"]
        enqueue_task(
            session,
            reindex_table,
            *task.args,
            wait_until=datetime.now(UTC) + timedelta(seconds=30),
            priority=100,
            **task.kwargs,
        )


@dbq_task(task_type=ReindexTableTask)
async def reindex_table(interval_seconds: int = 30, ctx: Dict[str, Any] = {}):
    """
    Reindex the knowledge store table
    """
    with tracer.start_as_current_span("reindex_table") as span:
        db = await aconn()
        table = await db.open_table("knowledge_store")
        await table.create_index("content", config=FTS())
        await table.optimize()

        next_run_at = datetime.now(UTC) + timedelta(seconds=interval_seconds)
        span.add_event("dbq.task.wait_until", {"wait_until": next_run_at.isoformat()})


async def schedule_reindex_table(session: Session, interval_seconds: int = 30):
    enqueue_task(
        session,
        reindex_table,
        interval_seconds=interval_seconds,
        priority=100,
    )
    logger.info("reindex table scheduled")
