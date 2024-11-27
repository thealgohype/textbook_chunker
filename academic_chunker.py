# academic_chunker.py
import re
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DocumentChunk:
    chapter: str
    unit: str
    section: str
    subsection: Optional[str]
    content: str
    metadata: Dict


class AcademicDocumentChunker:
    def __init__(self):
        self.chapter_pattern = r"CHAPTER\s+\d+"
        self.unit_pattern = r"UNIT\s*-?\s*\d+:"
        self.section_pattern = r"\n\d+\.\d+\s+[A-Z][A-Za-z\s\-]+\n"
        self.subsection_pattern = r"\n\d+\.\d+\.\d+\s+[A-Z][A-Za-z\s\-]+\n"

    def _find_all_matches(self, text: str, pattern: str) -> List[tuple]:
        return [(m.group(), m.start(), m.end()) for m in re.finditer(pattern, text)]

    def _extract_section_content(self, text: str, start: int, end: int) -> str:
        return text[start:end].strip()

    def _get_parent_section(
        self, position: int, sections: List[tuple]
    ) -> Optional[str]:
        for section, start, _ in reversed(sections):
            if start < position:
                return section
        return None

    def chunk_document(self, text: str) -> List[DocumentChunk]:
        chunks = []

        chapters = self._find_all_matches(text, self.chapter_pattern)
        units = self._find_all_matches(text, self.unit_pattern)
        sections = self._find_all_matches(text, self.section_pattern)
        subsections = self._find_all_matches(text, self.subsection_pattern)

        all_markers = []
        for chapter, start, end in chapters:
            all_markers.append(("chapter", chapter, start, end))
        for unit, start, end in units:
            all_markers.append(("unit", unit, start, end))
        for section, start, end in sections:
            all_markers.append(("section", section, start, end))
        for subsection, start, end in subsections:
            all_markers.append(("subsection", subsection, start, end))

        all_markers.sort(key=lambda x: x[2])

        for i in range(len(all_markers) - 1):
            current_marker = all_markers[i]
            next_marker = all_markers[i + 1]

            marker_type, title, start, _ = current_marker
            content = self._extract_section_content(text, start, next_marker[2])

            current_chapter = self._get_parent_section(start, chapters)
            current_unit = self._get_parent_section(start, units)
            current_section = self._get_parent_section(start, sections)

            chunk = DocumentChunk(
                chapter=current_chapter,
                unit=current_unit,
                section=current_section,
                subsection=title if marker_type == "subsection" else None,
                content=content,
                metadata={"type": marker_type, "position": start, "title": title},
            )
            chunks.append(chunk)

        last_marker = all_markers[-1]
        last_content = self._extract_section_content(text, last_marker[2], len(text))
        chunks.append(
            DocumentChunk(
                chapter=self._get_parent_section(last_marker[2], chapters),
                unit=self._get_parent_section(last_marker[2], units),
                section=self._get_parent_section(last_marker[2], sections),
                subsection=last_marker[1] if last_marker[0] == "subsection" else None,
                content=last_content,
                metadata={
                    "type": last_marker[0],
                    "position": last_marker[2],
                    "title": last_marker[1],
                },
            )
        )

        return chunks
