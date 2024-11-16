import streamlit as st
import pandas as pd
from academic_chunker import AcademicDocumentChunker
import docx2txt
import tiktoken

def count_tokens(text: str) -> int:
    """Count tokens using tiktoken cl100k_base encoder"""
    encoder = tiktoken.get_encoding("cl100k_base")
    return len(encoder.encode(text))

def count_words(text: str) -> int:
    """Count words in text"""
    return len(text.split())

def calculate_avg_tokens_per_section(chunks):
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

    avg_tokens = {
        section: section_tokens[section] / section_counts[section]
        for section in section_tokens
    }

    return avg_tokens

st.set_page_config(layout="wide")
st.title("Academic Document Section Chunker")

uploaded_file = st.file_uploader("Upload a document", type=['docx', 'txt'])

if uploaded_file is not None:
    # Read and process the document
    try:
        if uploaded_file.name.endswith('.docx'):
            # Extract text from Word document
            text = docx2txt.process(uploaded_file)
        else:
            # Handle text files
            text = uploaded_file.read().decode('utf-8')

        # Process the text
        chunker = AcademicDocumentChunker()
        chunks = chunker.chunk_document(text)

        # Calculate average tokens per section
        avg_tokens_per_section = calculate_avg_tokens_per_section(chunks)

        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Chunk Overview", "Section Analysis", "Detailed View"])

        with tab1:
            st.header("Document Structure Overview")

            # Create DataFrame for overview with enhanced metrics
            overview_data = []
            for i, chunk in enumerate(chunks):
                content_length = len(chunk.content)
                word_count = count_words(chunk.content)
                token_count = count_tokens(chunk.content)
                section = chunk.section if chunk.section else "Unnamed Section"

                overview_data.append({
                    'Chunk #': i + 1,
                    'Chapter': chunk.chapter,
                    'Unit': chunk.unit,
                    'Section': section,
                    'Subsection': chunk.subsection,
                    'Content Length': f"{content_length} chars / {word_count} words",
                    'Token Count': token_count,
                    'Section Avg Tokens': f"{avg_tokens_per_section[section]:.1f}"
                })

            df = pd.DataFrame(overview_data)
            st.dataframe(df, use_container_width=True)

            # Display enhanced statistics
            total_chars = sum(len(chunk.content) for chunk in chunks)
            total_words = sum(count_words(chunk.content) for chunk in chunks)
            total_tokens = sum(count_tokens(chunk.content) for chunk in chunks)
            avg_tokens_per_chunk = total_tokens / len(chunks)

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Total Chunks", len(chunks))
            with col2:
                st.metric("Total Characters", f"{total_chars:,}")
            with col3:
                st.metric("Total Words", f"{total_words:,}")
            with col4:
                st.metric("Total Tokens", f"{total_tokens:,}")
            with col5:
                st.metric("Avg Tokens/Chunk", f"{avg_tokens_per_chunk:.1f}")

        with tab2:
            st.header("Section Token Analysis")

            # Create section analysis DataFrame
            section_analysis = pd.DataFrame([
                {
                    'Section': section,
                    'Average Tokens': f"{avg_tokens:.1f}"
                }
                for section, avg_tokens in avg_tokens_per_section.items()
            ])

            # Display section analysis
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("Average Tokens per Section")
                st.dataframe(section_analysis, use_container_width=True)

            with col2:
                st.subheader("Section Distribution")
                # Create a bar chart of average tokens per section
                st.bar_chart(
                    pd.DataFrame({
                        'Average Tokens': {k: float(v) for k, v in avg_tokens_per_section.items()}
                    })
                )

        with tab3:
            st.header("Detailed Chunk View")

            # Add chunk selection
            chunk_titles = [
                f"{i+1}. {chunk.section or chunk.subsection or 'Unnamed Section'}" 
                for i, chunk in enumerate(chunks)
            ]
            selected_chunk = st.selectbox(
                "Select chunk to view",
                range(len(chunks)),
                format_func=lambda x: chunk_titles[x]
            )

            if selected_chunk is not None:
                chunk = chunks[selected_chunk]
                content_length = len(chunk.content)
                word_count = count_words(chunk.content)
                token_count = count_tokens(chunk.content)
                section = chunk.section if chunk.section else "Unnamed Section"

                col1, col2 = st.columns([1, 2])

                with col1:
                    st.subheader("Chunk Metadata")
                    st.write(f"Chunk #: {selected_chunk + 1}")
                    if chunk.chapter:
                        st.write(f"Chapter: {chunk.chapter}")
                    if chunk.unit:
                        st.write(f"Unit: {chunk.unit}")
                    if chunk.section:
                        st.write(f"Section: {chunk.section}")
                    if chunk.subsection:
                        st.write(f"Subsection: {chunk.subsection}")

                    # Enhanced metrics display
                    st.write("Content Metrics:")
                    st.write(f"- Characters: {content_length:,}")
                    st.write(f"- Words: {word_count:,}")
                    st.write(f"- Tokens: {token_count:,}")
                    st.write(f"- Section Average Tokens: {avg_tokens_per_section[section]:.1f}")

                with col2:
                    st.subheader("Chunk Content")
                    st.text_area("Content", chunk.content, height=400)

                    # Add download button for individual chunk with enhanced metadata
                    chunk_text = f"""Metadata:
Chapter: {chunk.chapter}
Unit: {chunk.unit}
Section: {chunk.section}
Subsection: {chunk.subsection}

Content Metrics:
Characters: {content_length:,}
Words: {word_count:,}
Tokens: {token_count:,}
Section Average Tokens: {avg_tokens_per_section[section]:.1f}

Content:
{chunk.content}
"""
                    st.download_button(
                        label="Download This Chunk",
                        data=chunk_text.encode('utf-8'),
                        file_name=f'chunk_{selected_chunk+1}.txt',
                        mime='text/plain',
                    )

    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        st.write("Please make sure the document is properly formatted and not corrupted.")