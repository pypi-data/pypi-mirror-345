from typing import List

from langchain_community.document_loaders.yuque import YuqueLoader

from whiskerrag_types.interface.loader_interface import BaseLoader
from whiskerrag_types.model.knowledge import KnowledgeSourceEnum, YuqueSourceConfig
from whiskerrag_types.model.multi_modal import Text
from whiskerrag_utils.registry import RegisterTypeEnum, register


@register(RegisterTypeEnum.KNOWLEDGE_LOADER, KnowledgeSourceEnum.YUQUE)
class WhiskerYuqueLoader(BaseLoader[Text]):

    async def load(self) -> List[Text]:
        if not isinstance(self.knowledge.source_config, YuqueSourceConfig):
            raise AttributeError("Invalid source config type for YuqueLoader")
        text_list: List[Text] = []
        try:
            loader = YuqueLoader(
                access_token=self.knowledge.source_config.auth_info,
                api_url=self.knowledge.source_config.api_url,
            )
            content = None
            # Extract book_id and document_id from source_config
            book_id = self.knowledge.source_config.book_id
            document_id = self.knowledge.source_config.document_id
            # Check if book_id and document_id are provided
            if book_id is not None and document_id is not None:
                try:
                    document = loader.get_document(int(book_id), int(document_id))
                    parsed_document = loader.parse_document(document)
                    content = loader.parse_document(document)
                    text_list.append(
                        Text(
                            content=parsed_document.page_content,
                            metadata=parsed_document.metadata,
                        )
                    )
                except Exception as e:
                    raise ValueError(f"Failed to get document: {e}")
            # Check if only book_id is provided
            elif book_id is not None:
                try:
                    documents = loader.get_books(user_id=loader.get_user_id())
                    for document in documents:
                        document_id = document.get("id")
                        if document_id is None:
                            print("Document ID is None, skipping...")
                            continue
                        document = loader.get_document(int(book_id), int(document_id))
                        parsed_document = loader.parse_document(document)
                        content = loader.parse_document(document)
                        text_list.append(
                            Text(
                                content=parsed_document.page_content,
                                metadata=parsed_document.metadata,
                            )
                        )
                except Exception as e:
                    raise ValueError(f"Failed to get book: {e}")

            if content is None:
                raise ValueError("No content found for the specified parameters")

            return text_list

        except Exception as e:
            raise Exception(f"Failed to load content from Yuque: {e}")
