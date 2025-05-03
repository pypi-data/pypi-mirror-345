import re
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class BaseCharSplitConfig(BaseModel):
    """Base split configuration class"""

    chunk_size: int = Field(default=1500, ge=1, description="chunk max size")
    chunk_overlap: int = Field(
        default=150,
        ge=0,
        description="chunk overlap size, must be less than chunk_size",
    )
    separators: Optional[List[str]] = Field(
        default=None, description="separator list, if None, use default separators"
    )
    split_regex: Optional[str] = Field(
        default=None, description="split_regex,if set, use it instead of separators"
    )

    @field_validator("split_regex")
    @classmethod
    def validate_regex(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regular expression: {str(e)}")
        return v

    @model_validator(mode="after")
    def validate_config(self) -> "BaseCharSplitConfig":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        if self.separators and self.split_regex:
            raise ValueError("Cannot specify both separators and split_regex")
        return self


class MarkdownSplitConfig(BaseCharSplitConfig):
    type: Literal["markdown"] = "markdown"
    separators: List[str] = Field(
        default=["\n\n"],
        description="""List of separators to split the text. If None, uses default separators""",
    )


class PDFSplitConfig(BaseCharSplitConfig):
    """PDF document split configuration"""

    type: Literal["pdf"] = "pdf"
    split_by_page: bool = Field(default=False, description="Whether to split by pages")
    keep_layout: bool = Field(
        default=True, description="Whether to preserve the original layout"
    )
    extract_images: bool = Field(default=False, description="Whether to extract images")
    table_extract_mode: str = Field(
        default="text", description="Table extraction mode: 'text' or 'structure'"
    )


class TextSplitConfig(BaseCharSplitConfig):
    """Plain text split configuration"""

    type: Literal["text"] = "text"
    separators: Optional[List[str]] = Field(
        default=[
            "\n\n",
        ],
        description="""List of separators to split the text. If None, uses default separators""",
    )
    keep_separator: Optional[Union[bool, Literal["start", "end"]]] = Field(
        default=False,
        description="""Whether to keep the separator and where to place it in each corresponding chunk (True='start')""",
    )
    strip_whitespace: Optional[bool] = Field(
        default=False,
        description="""If `True`, strips whitespace from the start and end of every document""",
    )


class JSONSplitConfig(BaseModel):
    """
    JSON document split configuration
    @link {https://python.langchain.com/api_reference/text_splitters/json/langchain_text_splitters.json.RecursiveJsonSplitter.html}
    """

    type: Literal["json"] = "json"
    max_chunk_size: int = Field(
        default=2000,
        description=""" The maximum size for each chunk. Defaults to 2000 """,
    )
    min_chunk_size: Optional[int] = Field(
        default=200,
        description="""The minimum size for a chunk. If None,
                defaults to the maximum chunk size minus 200, with a lower bound of 50.""",
    )


class GeaGraphSplitConfig(BaseModel):
    """
    JSON document split configuration
    @link {https://python.langchain.com/api_reference/text_splitters/json/langchain_text_splitters.json.RecursiveJsonSplitter.html}
    """

    type: Literal["geagraph"] = "geagraph"
    schema_id: Optional[str] = Field(
        default=None,
        description=""" The maximum size for each chunk. Defaults to 2000 """,
    )
