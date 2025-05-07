import json
from typing import List

from langchain_text_splitters import RecursiveJsonSplitter

from whiskerrag_types.interface.splitter_interface import BaseSplitter
from whiskerrag_types.model.knowledge import JSONSplitConfig
from whiskerrag_types.model.multi_modal import Text
from whiskerrag_utils.registry import RegisterTypeEnum, register


@register(RegisterTypeEnum.SPLITTER, "json")
class JSONSplitter(BaseSplitter[JSONSplitConfig, Text]):

    def split(self, content: Text, split_config: JSONSplitConfig) -> List[Text]:
        """Splits JSON content into smaller chunks based on the provided configuration."""
        json_content = {}
        try:
            json_content = json.loads(content.content)
            if not isinstance(json_content, dict):
                raise ValueError("JSON content must be a dictionary.")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON content provided for splitting.")
        except ValueError as e:
            raise ValueError(f"Error processing JSON content: {str(e)}")
        splitter = RecursiveJsonSplitter(
            max_chunk_size=split_config.max_chunk_size,
            min_chunk_size=split_config.min_chunk_size,
        )
        split_texts = splitter.split_json(json_content)
        return [
            Text(content=str(text), metadata=content.metadata) for text in split_texts
        ]

    def batch_split(
        self, content: List[Text], split_config: JSONSplitConfig
    ) -> List[List[Text]]:
        return [self.split(text, split_config) for text in content]
