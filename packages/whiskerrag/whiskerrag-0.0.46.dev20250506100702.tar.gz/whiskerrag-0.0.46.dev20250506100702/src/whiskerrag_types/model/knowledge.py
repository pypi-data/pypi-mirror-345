from datetime import datetime, timezone
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from deprecated import deprecated
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from whiskerrag_types.model.splitter import (
    BaseCharSplitConfig,
    GeaGraphSplitConfig,
    JSONSplitConfig,
    MarkdownSplitConfig,
    PDFSplitConfig,
    TextSplitConfig,
)
from whiskerrag_types.model.utils import calculate_sha256, parse_datetime


class MetadataSerializer:
    @staticmethod
    def deep_sort_dict(data: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
        if isinstance(data, dict):
            return {
                k: MetadataSerializer.deep_sort_dict(data[k])
                for k in sorted(data.keys())
            }
        elif isinstance(data, list):
            return [MetadataSerializer.deep_sort_dict(item) for item in data]
        return data

    @staticmethod
    @lru_cache(maxsize=1024)
    def serialize(metadata: Optional[Dict]) -> Optional[Dict]:
        if metadata is None:
            return None
        sorted_metadata = MetadataSerializer.deep_sort_dict(metadata)
        return sorted_metadata if isinstance(sorted_metadata, dict) else None


class KnowledgeSourceEnum(str, Enum):
    """
    Specifies the source of knowledge, which influences the behavior of the resource loader
    """

    GITHUB_REPO = "github_repo"
    GITHUB_FILE = "github_file"
    USER_INPUT_TEXT = "user_input_text"
    USER_UPLOAD_FILE = "user_upload_file"
    YUQUE = "yuque"
    YOUTUBE = "youtube"
    DATABASE = "database"


class GithubRepoSourceConfig(BaseModel):
    repo_name: str = Field(..., description="github repo url")
    branch: Optional[str] = Field(None, description="branch name of the repo")
    commit_id: Optional[str] = Field(None, description="commit id of the repo")
    auth_info: Optional[str] = Field(None, description="authentication information")


class GithubFileSourceConfig(GithubRepoSourceConfig):
    path: str = Field(..., description="path of the file in the repo")


class S3SourceConfig(BaseModel):
    bucket: str = Field(..., description="s3 bucket name")
    key: str = Field(..., description="s3 key")
    version_id: Optional[str] = Field(None, description="s3 version id")
    region: Optional[str] = Field(None, description="s3 region")
    access_key: Optional[str] = Field(None, description="s3 access key")
    secret_key: Optional[str] = Field(None, description="s3 secret key")
    auth_info: Optional[str] = Field(None, description="s3 session token")


class YuqueSourceConfig(BaseModel):
    api_url: str = Field(
        default="https://www.yuque.com",
        description="the yuque api url",
    )
    group_id: str = Field(..., description="the yuque group id")
    book_id: Optional[str] = Field(
        default=None,
        description="the yuque book id, if not set, will use the group all book",
    )
    document_id: Optional[str] = Field(
        default=None,
        description="the yuque document id in book, if not set, will use the book id as document id",
    )
    auth_info: str = Field(..., description="authentication information")


class OpenUrlSourceConfig(BaseModel):
    url: str = Field(..., description="cloud storage url, such as oss, cos, etc.")


class OpenIdSourceConfig(BaseModel):
    id: str = Field(..., description="cloud storage file id, used for afts")


class TextSourceConfig(BaseModel):
    text: str = Field(
        default="",
        min_length=1,
        max_length=100000,
        description="Text content, length range 1-100000 characters",
    )


class KnowledgeTypeEnum(str, Enum):
    """
    mime type of the knowledge
    """

    TEXT = "text"
    IMAGE = "image"
    MARKDOWN = "markdown"
    JSON = "json"
    DOCX = "docx"
    PDF = "pdf"
    QA = "qa"
    YUQUEDOC = "yuquedoc"
    ONEAPIAPP = "openapi_app"
    """ such as github repo, zip """
    FOLDER = "folder"


class EmbeddingModelEnum(str, Enum):
    OPENAI = "openai"
    # 轻量级
    ALL_MINILM_L6_V2 = "sentence-transformers/all-MiniLM-L6-v2"
    # 通用性能
    all_mpnet_base_v2 = "sentence-transformers/all-mpnet-base-v2"
    # 多语言
    PARAPHRASE_MULTILINGUAL_MINILM_L12_V2 = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    # 中文
    TEXT2VEC_BASE_CHINESE = "shibing624/text2vec-base-chinese"


KnowledgeSplitConfig = Union[
    BaseCharSplitConfig,
    MarkdownSplitConfig,
    TextSplitConfig,
    JSONSplitConfig,
    PDFSplitConfig,
    GeaGraphSplitConfig,
]


@deprecated(
    reason="Use TextCreate, ImageCreate, JSONCreate, MarkdownCreate, PDFCreate, GithubRepoCreate,QACreate instead"
)
class KnowledgeCreate(BaseModel):
    """
    KnowledgeCreate model for creating knowledge resources.
    Attributes:
        knowledge_type (ResourceType): Type of knowledge resource.
        space_id (str): Space ID, example: petercat bot ID.
        knowledge_name (str): Name of the knowledge resource.
        file_sha (Optional[str]): SHA of the file.
        file_size (Optional[int]): Size of the file.
        split_config (Optional[dict]): Configuration for splitting the knowledge.
        source_data (Optional[str]): Source data of the knowledge.
        auth_info (Optional[str]): Authentication information.
        embedding_model_name (Optional[str]): Name of the embedding model.
        metadata (Optional[dict]): Additional metadata.
    """

    space_id: str = Field(
        ...,
        description="the space of knowledge, example: petercat bot id, github repo name",
    )
    knowledge_type: KnowledgeTypeEnum = Field(
        KnowledgeTypeEnum.TEXT, description="type of knowledge resource"
    )
    knowledge_name: str = Field(
        ..., max_length=255, description="name of the knowledge resource"
    )
    source_type: KnowledgeSourceEnum = Field(
        KnowledgeSourceEnum.USER_INPUT_TEXT, description="source type"
    )
    source_config: Union[
        GithubRepoSourceConfig, GithubFileSourceConfig, S3SourceConfig, TextSourceConfig
    ] = Field(
        ...,
        description="source config of the knowledge",
    )
    embedding_model_name: Union[EmbeddingModelEnum, str] = Field(
        EmbeddingModelEnum.OPENAI,
        description="name of the embedding model. you can set any other model if target embedding service registered",
    )
    split_config: KnowledgeSplitConfig = Field(
        ...,
        description="configuration for splitting the knowledge",
    )
    file_sha: Optional[str] = Field(None, description="SHA of the file")
    file_size: Optional[int] = Field(None, description="size of the file")
    metadata: dict = Field({}, description="additional metadata, user can update it")
    parent_id: Optional[str] = Field(None, description="parent knowledge id")
    enabled: bool = Field(True, description="is knowledge enabled")

    @field_serializer("metadata")
    def serialize_metadata(self, metadata: dict) -> Optional[dict]:
        if metadata is None:
            return None
        sorted_metadata = MetadataSerializer.deep_sort_dict(metadata)
        return sorted_metadata if isinstance(sorted_metadata, dict) else None

    @field_serializer("knowledge_type")
    def serialize_knowledge_type(
        self, knowledge_type: Union[KnowledgeTypeEnum, str]
    ) -> str:
        if isinstance(knowledge_type, KnowledgeTypeEnum):
            return knowledge_type.value
        return str(knowledge_type)

    @field_serializer("source_type")
    def serialize_source_type(
        self, source_type: Union[KnowledgeSourceEnum, str]
    ) -> str:
        if isinstance(source_type, KnowledgeSourceEnum):
            return source_type.value
        return str(source_type)

    @field_serializer("embedding_model_name")
    def serialize_embedding_model_name(
        self, embedding_model_name: Union[EmbeddingModelEnum, str]
    ) -> str:
        if isinstance(embedding_model_name, EmbeddingModelEnum):
            return embedding_model_name.value
        return str(embedding_model_name)

    @field_validator("enabled", mode="before")
    @classmethod
    def convert_tinyint_to_bool(cls, v: Any) -> bool:
        return bool(v)


class Knowledge(BaseModel):
    knowledge_id: str = Field(
        default_factory=lambda: str(uuid4()), description="knowledge id"
    )
    space_id: str = Field(
        ...,
        description="the space of knowledge, example: petercat bot id, github repo name",
    )
    tenant_id: str = Field(..., description="tenant id")
    knowledge_type: KnowledgeTypeEnum = Field(
        KnowledgeTypeEnum.TEXT, description="type of knowledge resource"
    )
    knowledge_name: str = Field(
        ..., max_length=255, description="name of the knowledge resource"
    )
    source_type: KnowledgeSourceEnum = Field(
        KnowledgeSourceEnum.USER_INPUT_TEXT, description="source type"
    )
    source_config: Union[
        GithubRepoSourceConfig,
        GithubFileSourceConfig,
        S3SourceConfig,
        OpenUrlSourceConfig,
        TextSourceConfig,
    ] = Field(
        ...,
        description="source config of the knowledge",
    )
    embedding_model_name: Union[EmbeddingModelEnum, str] = Field(
        EmbeddingModelEnum.OPENAI,
        description="name of the embedding model. you can set any other model if target embedding service registered",
    )
    split_config: KnowledgeSplitConfig = Field(
        ...,
        description="configuration for splitting the knowledge",
    )
    file_sha: Optional[str] = Field(None, description="SHA of the file")
    file_size: Optional[int] = Field(None, description="size of the file")
    metadata: dict = Field({}, description="additional metadata, user can update it")
    retrieval_count: int = Field(default=0, description="count of the retrieval")
    parent_id: Optional[str] = Field(None, description="parent knowledge id")
    enabled: bool = Field(True, description="is knowledge enabled")
    created_at: Optional[datetime] = Field(
        default=None,
        alias="gmt_create",
        description="creation time",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        alias="gmt_modified",
        description="update time",
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if (
            self.source_type == KnowledgeSourceEnum.USER_INPUT_TEXT
            and isinstance(self.source_config, TextSourceConfig)
            and self.source_config.text is not None
            and self.file_sha is None
        ):
            self.file_sha = calculate_sha256(self.source_config.text)
            self.file_size = len(self.source_config.text.encode("utf-8"))

    def update(self, **kwargs: Dict[str, Any]) -> "Knowledge":
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.updated_at = datetime.now()
        return self

    @field_validator("enabled", mode="before")
    @classmethod
    def convert_tinyint_to_bool(cls, v: Any) -> bool:
        return bool(v)

    @model_validator(mode="before")
    def pre_process_data(cls, data: dict) -> dict:
        for field, value in data.items():
            if isinstance(value, UUID):
                data[field] = str(value)
        field_mappings = {"created_at": "gmt_create", "updated_at": "gmt_modified"}
        for field, alias_name in field_mappings.items():
            val = data.get(field) or data.get(alias_name)
            if val is None:
                continue

            if isinstance(val, str):
                dt = parse_datetime(val)
                data[field] = dt
                data[alias_name] = dt
            else:
                if val and val.tzinfo is None:
                    dt = val.replace(tzinfo=timezone.utc)
                    data[field] = dt
                    data[alias_name] = dt

        return data

    @model_validator(mode="after")
    def set_defaults(self) -> "Knowledge":
        now = datetime.now(timezone.utc)
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
        return self

    @field_serializer("metadata")
    def serialize_metadata(self, metadata: dict) -> Optional[dict]:
        if metadata is None:
            return None
        sorted_metadata = MetadataSerializer.deep_sort_dict(metadata)
        return sorted_metadata if isinstance(sorted_metadata, dict) else None

    @field_serializer("knowledge_type")
    def serialize_knowledge_type(
        self, knowledge_type: Union[KnowledgeTypeEnum, str]
    ) -> str:
        if isinstance(knowledge_type, KnowledgeTypeEnum):
            return knowledge_type.value
        return str(knowledge_type)

    @field_serializer("source_type")
    def serialize_source_type(
        self, source_type: Union[KnowledgeSourceEnum, str]
    ) -> str:
        if isinstance(source_type, KnowledgeSourceEnum):
            return source_type.value
        return str(source_type)

    @field_serializer("embedding_model_name")
    def serialize_embedding_model_name(
        self, embedding_model_name: Union[EmbeddingModelEnum, str]
    ) -> str:
        if isinstance(embedding_model_name, EmbeddingModelEnum):
            return embedding_model_name.value
        return str(embedding_model_name)

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
