from typing import List

from academic_chunker import AcademicDocumentChunker, DocumentChunk
from utils import count_tokens


def process_document(text: str) -> List[DocumentChunk]:
    chunker = AcademicDocumentChunker()
    return chunker.chunk_document(text)


def calculate_avg_tokens_per_section(chunks: List[DocumentChunk]) -> dict:
    """Calculate average tokens per section"""
    section_tokens = {}
    section_counts = {}

    for chunk in chunks:
        section = chunk.section if chunk.section else "Unnamed Section"
        tokens = count_tokens(chunk.content)

        if section in section_tokens:
            section_tokens[section] += tokens
            section_counts[section] += 1
        else:
            section_tokens[section] = tokens
            section_counts[section] = 1

    return {
        section: section_tokens[section] / section_counts[section]
        for section in section_tokens
    }
