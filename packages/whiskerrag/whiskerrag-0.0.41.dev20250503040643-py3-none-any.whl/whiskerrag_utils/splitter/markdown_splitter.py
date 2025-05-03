from typing import List

from langchain_text_splitters import MarkdownTextSplitter

from whiskerrag_types.interface.splitter_interface import BaseSplitter
from whiskerrag_types.model.knowledge import MarkdownSplitConfig
from whiskerrag_types.model.multi_modal import Text
from whiskerrag_utils.registry import RegisterTypeEnum, register


@register(RegisterTypeEnum.SPLITTER, "markdown")
class MarkdownSplitter(BaseSplitter[MarkdownSplitConfig, Text]):

    def split(self, content: Text, split_config: MarkdownSplitConfig) -> List[Text]:
        splitter = MarkdownTextSplitter(
            chunk_size=split_config.chunk_size,
            chunk_overlap=split_config.chunk_overlap,
        )
        split_texts = splitter.split_text(content.content)
        return [
            Text(content=text, metadata=content.metadata.copy()) for text in split_texts
        ]

    def batch_split(
        self, content_list: List[Text], split_config: MarkdownSplitConfig
    ) -> List[List[Text]]:
        return [self.split(text, split_config) for text in content_list]
