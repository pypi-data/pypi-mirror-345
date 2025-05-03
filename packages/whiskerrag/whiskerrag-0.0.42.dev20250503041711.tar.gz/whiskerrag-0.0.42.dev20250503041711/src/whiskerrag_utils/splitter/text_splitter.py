import re
from typing import List

from langchain_text_splitters import CharacterTextSplitter

from whiskerrag_types.interface.splitter_interface import BaseSplitter
from whiskerrag_types.model.knowledge import TextSplitConfig
from whiskerrag_types.model.multi_modal import Text
from whiskerrag_utils.registry import RegisterTypeEnum, register


@register(RegisterTypeEnum.SPLITTER, "text")
class TextSplitter(BaseSplitter[TextSplitConfig, Text]):
    def split(self, content: Text, split_config: TextSplitConfig) -> List[Text]:
        config_dict = split_config.model_dump(mode="json")
        separators = config_dict["separators"] or ["\n\n"]
        separator_pattern = "|".join(map(re.escape, separators))
        split_regex = config_dict["split_regex"]
        if split_regex:
            separator_pattern = split_regex
        splitter = CharacterTextSplitter(
            chunk_size=config_dict["chunk_size"],
            chunk_overlap=config_dict["chunk_overlap"],
            separator=separator_pattern,
            is_separator_regex=True,
            keep_separator=config_dict["keep_separator"],
            strip_whitespace=config_dict["strip_whitespace"],
        )
        split_texts = splitter.split_text(content.content)
        return [Text(content=text, metadata=content.metadata) for text in split_texts]

    def batch_split(
        self, content_list: List[Text], split_config: TextSplitConfig
    ) -> List[List[Text]]:
        return [self.split(content, split_config) for content in content_list]
