from typing import List

from whiskerrag_types.model.chunk import Chunk
from whiskerrag_types.model.knowledge import Knowledge
from whiskerrag_types.model.multi_modal import Image, Text

from .registry import RegisterTypeEnum, get_register, init_register, register


async def get_chunks_by_knowledge(knowledge: Knowledge) -> List[Chunk]:
    """
    Convert knowledge into vectorized chunks

    Args:
        knowledge (Knowledge): Knowledge object containing source type, split configuration,
                             embedding model and other information

    Returns:
        List[Chunk]: List of vectorized chunks

    Process flow:
    1. Get corresponding loader based on knowledge source type
    2. Get text splitter
    3. Get embedding model
    4. Load content
    5. Split content
    6. Vectorize each split content
    7. Generate final list of Chunk objects
    """
    LoaderCls = get_register(RegisterTypeEnum.KNOWLEDGE_LOADER, knowledge.source_type)
    split_type = getattr(knowledge.split_config, "type", None) or "text"
    SplitterCls = get_register(RegisterTypeEnum.SPLITTER, split_type)
    EmbeddingCls = get_register(
        RegisterTypeEnum.EMBEDDING, knowledge.embedding_model_name
    )
    contents = await LoaderCls(knowledge).load()
    parse_results = []
    for content in contents:
        split_result = SplitterCls().split(content, knowledge.split_config)
        parse_results.extend(split_result)
    chunks = []
    for parseItem in parse_results:
        if isinstance(parseItem, Text):
            embedding = await EmbeddingCls().embed_text(parseItem.content, timeout=30)
        elif isinstance(parseItem, Image):
            embedding = await EmbeddingCls().embed_image(parseItem, timeout=30)
        else:
            print(f"[warn]: illegal split item :{parseItem}")
            continue
        chunk = Chunk(
            context=parseItem.content,
            metadata=parseItem.metadata,
            embedding=embedding,
            knowledge_id=knowledge.knowledge_id,
            embedding_model_name=knowledge.embedding_model_name,
            space_id=knowledge.space_id,
            tenant_id=knowledge.tenant_id,
        )
        chunks.append(chunk)
    return chunks


__all__ = [
    "get_register",
    "register",
    "RegisterTypeEnum",
    "init_register",
    "SplitterEnum",
    "get_chunks_by_knowledge",
]
