from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from whiskerrag_types.interface.splitter_interface import BaseSplitter
from whiskerrag_types.model.multi_modal import Text
from whiskerrag_types.model.splitter import BaseCharSplitConfig
from whiskerrag_utils.registry import RegisterTypeEnum, register


@register(RegisterTypeEnum.SPLITTER, "base")
class BaseSplitterRegistry(BaseSplitter[BaseCharSplitConfig, Text]):
    def split(self, content: Text, split_config: BaseCharSplitConfig) -> List[Text]:
        print("BaseSplitterRegistry split", content, split_config)
        separators = split_config.separators or [
            # First, try to split along Markdown headings (starting with level 2)
            "\n#{1,6} ",
            # Note the alternative syntax for headings (below) is not handled here
            # Heading level 2
            # ---------------
            # End of code block
            "```\n",
            # Horizontal lines
            "\n\\*\\*\\*+\n",
            "\n---+\n",
            "\n___+\n",
            # Note that this splitter doesn't handle horizontal lines defined
            # by *three or more* of ***, ---, or ___, but this is not handled
            "\n\n",
            "\n",
            " ",
        ]
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=split_config.chunk_size,
            chunk_overlap=split_config.chunk_overlap,
            separators=separators,
            keep_separator=False,
        )
        split_texts = splitter.split_text(content.content)
        return [Text(content=text, metadata=content.metadata) for text in split_texts]

    def batch_split(
        self, content_list: List[Text], split_config: BaseCharSplitConfig
    ) -> List[List[Text]]:
        return [self.split(content, split_config) for content in content_list]
