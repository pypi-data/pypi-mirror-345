from typing import Any, Dict, Generator
import nltk
from nltk import tokenize
import pprint
import hashlib
import re
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from tqdm import tqdm
import openai
import os
import fitz  
from copy import deepcopy


class BaseChunker:
    """Handler for loading in content of a PDF

    Parameters
    ----------
    chunk_size: int = 5
        Size of chunks, chunk content is defined by child class

    step_size: int = 5
        Step size in units of chunks that the Chunker traverses 
        through content
    
    """

    def __init__(self, chunk_size: int = 5, step_size: int = 5):
        self.chunk_size = chunk_size
        self.step_size = step_size

    def get_chunks(self, data: Dict[str, Any]) -> Generator[str, None, None]:
        """Generator yielding individual sentence level chunks of the provided data."""
        content = data["content"]
        sentences = tokenize.sent_tokenize(content)
        
        # Track sentence positions in original text
        sent_positions = []
        last_pos = 0
        for sent in sentences:
            start_pos = content.find(sent, last_pos)
            end_pos = start_pos + len(sent)
            sent_positions.append((start_pos, end_pos))
            last_pos = end_pos

        for i in range(0, len(sentences), self.step_size):
            max_size = min(self.chunk_size, len(sentences) - i)
            
            # Extract page number and format as 4 digits
            page_str = str(data['page'])
            if isinstance(data['page'], int):
                page_num = data['page']
            else:
                # Extract digits from strings like "Page 1"
                digits = ''.join(filter(str.isdigit, page_str))
                page_num = int(digits) if digits else 0
                
            # Generate hash from chunk content
            chunk_hash = hashlib.md5(" ".join(sentences[i:i + max_size]).encode('utf-8')).hexdigest()
            chunk_hash_split=chunk_hash[:6]
            # Create a new rich_chunk dictionary for each iteration
            rich_chunk = {
                "page": data["page"],
                "source": data["source"],
                "chunk_start_pos": sent_positions[i][0],
                "chunk_end_pos": sent_positions[i + max_size - 1][1],
                "chunk_text": " ".join(sentences[i:i + max_size]) + " \n",
                "chunk_id": f"{page_num:04d}_{sent_positions[i][0]:04d}_{self.chunk_size}_{chunk_hash_split}_{chunk_hash_split}",
                "num_sentences": max_size
            }

            yield rich_chunk

            if i + max_size >= len(sentences):
                break

class SentenceChunker(BaseChunker):
    """Sentence level text chunker

    Parameters
    ----------
    chunk_size: int = 5
        Number of sentences within chunks

    step_size: int = 5
        Sentence step size
    
    """

    def __init__(self,          
            chunk_size: int = 5, 
            step_size: int = 5
        ):
        super().__init__(
            chunk_size=chunk_size, 
            step_size=step_size
        )
        try: 
            nltk.data.find('tokenizers/punkt.zip')
            nltk.data.find('tokenizers/punkt_tab')
        except:
            nltk.download('punkt')
            nltk.download('punkt_tab')

    def get_chunks(self, data: Dict[str, Any]) -> Generator[str, None, None]:
        """Generator yielding individual sentence level chunks of the provided data.

        Parameters
        ----------
        data: Dict[str, Any]
            Dictionary storing metadata along with string content. The value associated
            with the key 'page' is stored within the output string. 
            'content' holds the page text.

        Yields
        -------
        rich_chunk: Dict[str, Any]
            Dictionary containing chunk metadata and text
        """
        sentences = tokenize.sent_tokenize(data["content"])
        
        # Track sentence positions in original text
        sent_positions = []
        last_pos = 0
        for sent in sentences:
            start_pos = data["content"].find(sent, last_pos)
            end_pos = start_pos + len(sent)
            sent_positions.append((start_pos, end_pos))
            last_pos = end_pos

        for i in range(0, len(sentences), self.step_size):
            max_size = min(self.chunk_size, len(sentences) - i)
            
            # Get character positions for this chunk
            chunk_start_pos = sent_positions[i][0]
            chunk_end_pos = sent_positions[i + max_size - 1][1]
            
            # Create chunk text
            chunk_sentences = sentences[i:i + max_size]
            chunk_text = " ".join(chunk_sentences) + " \n"
            
            # Extract page number and format as 4 digits
            page_str = str(data['page'])
            if isinstance(data['page'], int):
                page_num = data['page']
            else:
                # Extract digits from strings like "Page 1"
                digits = ''.join(filter(str.isdigit, page_str))
                page_num = int(digits) if digits else 0
                
            chunk_hash = hashlib.md5(" ".join(chunk_text).encode('utf-8')).hexdigest()
            chunk_hash_split=chunk_hash[:6]   
            chunk_id = f"{page_num:04d}_{chunk_start_pos:04d}_{self.chunk_size}_{chunk_hash_split}"
            
            rich_chunk = {
                "page": data["page"],
                "source": data["source"],
                "chunk_start_pos": chunk_start_pos,
                "chunk_end_pos": chunk_end_pos,
                "chunk_text": chunk_text,
                "chunk_id": chunk_id,
                "num_sentences": max_size
            }

            yield rich_chunk

            if i + max_size == len(sentences):
                break

class PDFSentenceChunker(BaseChunker):
    """Sentence level text chunker

    Parameters
    ----------
    chunk_size: int = 5
        Number of sentences within chunks

    step_size: int = 5
        Sentence step size
    
    """

    def __init__(self,          
            chunk_size: int = 5, 
            step_size: int = 5
        ):
        super().__init__(
            chunk_size=chunk_size, 
            step_size=step_size
        )
        try: 
            nltk.data.find('tokenizers/punkt.zip')
            nltk.data.find('tokenizers/punkt_tab')
        except:
            nltk.download('punkt')
            nltk.download('punkt_tab')

    def get_chunks(self, data: Dict[str, Any]) -> Generator[str, None, None]:
        """Generator yielding individual sentence level chunks of the provided data."""
        content = data["content"]
        sentences = tokenize.sent_tokenize(content)
        
        # Track sentence positions in original text
        sent_positions = []
        last_pos = 0
        for sent in sentences:
            start_pos = content.find(sent, last_pos)
            end_pos = start_pos + len(sent)
            sent_positions.append((start_pos, end_pos))
            last_pos = end_pos

        for i in range(0, len(sentences), self.step_size):
            max_size = min(self.chunk_size, len(sentences) - i)
            
            # Get character positions for this chunk
            chunk_start_pos = sent_positions[i][0]
            chunk_end_pos = sent_positions[i + max_size - 1][1]
            
            # Create chunk text (removed structural context references)
            chunk_sentences = sentences[i:i + max_size]
            chunk_text = " ".join(chunk_sentences) + " \n"
            
            chunk_hash = hashlib.md5(" ".join(chunk_text).encode('utf-8')).hexdigest()
            chunk_hash_split=chunk_hash[:6]   
            
            # Extract page number and format as 4 digits
            page_str = str(data['page'])
            if isinstance(data['page'], int):
                page_num = data['page']
            else:
                # Extract digits from strings like "Page 1"
                digits = ''.join(filter(str.isdigit, page_str))
                page_num = int(digits) if digits else 0
            
            
            chunk_id = f"{page_num:04d}_{chunk_start_pos:04d}_{self.chunk_size}_{chunk_hash_split}"
            
            # Create a new rich_chunk dictionary for each iteration
            rich_chunk = {
                "page": data["page"],
                "source": data["source"],
                "chunk_start_pos": chunk_start_pos,
                "chunk_end_pos": chunk_end_pos,
                "chunk_text": chunk_text,
                "chunk_id": chunk_id,
                "num_sentences": max_size
            }

            yield rich_chunk

            if i + max_size == len(sentences):
                break

    def get_structured_chunks(self, data: Dict[str, Any]) -> Generator[str, None, None]:
        """Generator yielding chunks that preserve section headers, questions, and examples.
        
        Parameters
        ----------
        data: Dict[str, Any]
            Dictionary storing metadata and content. Similar to get_chunks() but with
            special handling of structural elements.
            
        Yields
        -------
        rich_chunk: Dict[str, Any]
            Dictionary containing chunk metadata, text, and structural context
        """
        content = data["content"]
        sentences = tokenize.sent_tokenize(content)
        
        # Regular expressions for identifying structural elements
        section_pattern = r'^(?:Section\s+)?(?:\d+\.)*\d+\s+[A-Z][A-Za-z\s]+$'
        question_pattern = r'^Question\s+(?:\d+\.)*\d+'
        example_pattern = r'^Example\s+[A-Z]?\d+(?:\.\d+)*'
        scenario_pattern = r'^Scenario\s+\d+:?\s*.*$'
        excerpt_pattern = r'^Excerpt from ASC.*$'
        interpretive_pattern = r'^Interpretive response:'
        
        # Track sentence positions and their structural context
        sent_positions = []
        last_pos = 0
        current_section = None
        structural_elements = []  # List of (index, type, text, parent, excerpt, response) tuples
        current_example = None
        current_question = None
        current_excerpt = None
        
        # First pass: identify structural elements and positions
        for idx, sent in enumerate(sentences):
            start_pos = content.find(sent, last_pos)
            end_pos = start_pos + len(sent)
            sent_positions.append((start_pos, end_pos))
            last_pos = end_pos
            
            # Check for structural elements
            sent_stripped = sent.strip()
            
            if re.match(section_pattern, sent_stripped, re.MULTILINE):
                structural_elements.append((idx, "section", sent_stripped, None, None, None))
                current_example = None
                current_question = None
                current_excerpt = None
            elif re.match(question_pattern, sent_stripped, re.MULTILINE):
                current_question = sent_stripped
                current_example = None  # Reset example when entering a question
                current_excerpt = None
                # Store question without excerpt/response initially
                structural_elements.append((idx, "question", sent_stripped, None, None, None))
            elif re.match(excerpt_pattern, sent_stripped, re.MULTILINE):
                # Start collecting excerpt text
                current_excerpt = sent_stripped
                # Find the last question or scenario element and update it
                for i in range(len(structural_elements)-1, -1, -1):
                    if structural_elements[i][1] in ["question", "scenario"]:
                        elem_text = structural_elements[i][2]
                        structural_elements[i] = (structural_elements[i][0], structural_elements[i][1], 
                                               elem_text, structural_elements[i][3], current_excerpt, None)
                        break
            elif re.match(interpretive_pattern, sent_stripped, re.MULTILINE):
                # Find the last question or scenario element and update it with the response
                for i in range(len(structural_elements)-1, -1, -1):
                    if structural_elements[i][1] in ["question", "scenario"]:
                        elem_text = structural_elements[i][2]
                        excerpt_text = structural_elements[i][4]
                        structural_elements[i] = (structural_elements[i][0], structural_elements[i][1], 
                                               elem_text, structural_elements[i][3], excerpt_text, sent_stripped)
                        break
            elif re.match(example_pattern, sent_stripped, re.MULTILINE):
                current_example = sent_stripped
                structural_elements.append((idx, "example", sent_stripped, None, None, None))
            elif re.match(scenario_pattern, sent_stripped, re.MULTILINE):
                # Scenarios can belong to either examples or questions
                parent = current_example if current_example else current_question
                if parent:
                    structural_elements.append((idx, "scenario", sent_stripped, parent, None, None))

            # If we're in an excerpt section, keep collecting text
            if current_excerpt and not re.match(interpretive_pattern, sent_stripped, re.MULTILINE):
                # Update the excerpt text in the last structural element
                for i in range(len(structural_elements)-1, -1, -1):
                    if structural_elements[i][1] in ["question", "scenario"]:
                        elem_text = structural_elements[i][2]
                        current_excerpt += "\n" + sent_stripped
                        structural_elements[i] = (structural_elements[i][0], structural_elements[i][1], 
                                               elem_text, structural_elements[i][3], current_excerpt, None)
                        break

        # Main chunking loop
        for i in range(0, len(sentences), self.step_size):
            max_size = min(self.chunk_size, len(sentences) - i)
            
            # Create chunk text with structural context
            chunk_sentences = sentences[i:i + max_size]
            
            # Prepare prefix with relevant structural headers and content
            prefix = ""
            current_structure = None  # Define this based on structural_elements
            current_scenario = None   # Define this based on structural_elements
            struct_excerpt = None
            struct_response = None
            
            # Find relevant structural context for this chunk
            chunk_start_idx = i
            for struct_idx, struct_type, struct_text, parent, excerpt, response in structural_elements:
                if struct_idx <= chunk_start_idx:
                    current_structure = (struct_type, struct_text)
                    struct_excerpt = excerpt
                    struct_response = response
                    if struct_type == "scenario":
                        current_scenario = (struct_type, struct_text, parent)
            
            if current_structure:
                struct_type, struct_text = current_structure
                if struct_type == "question":
                    prefix += struct_text + "\n"
                    if struct_excerpt:
                        prefix += struct_excerpt + "\n"
                    if struct_response:
                        prefix += struct_response + "\n"
                elif struct_type == "example":
                    prefix += struct_text + "\n"
            
            if current_scenario:
                _, scenario_text, parent_example = current_scenario
                if parent and parent.startswith("Question"):
                    prefix += parent + "\n"
                prefix += scenario_text + "\n"
                if struct_excerpt:
                    prefix += struct_excerpt + "\n"
                if struct_response:
                    prefix += struct_response + "\n"
            
            # Combine prefix with chunk content
            chunk_text = prefix + " ".join(chunk_sentences) + " \n"
            
            # Extract page number and format as 4 digits
            page_str = str(data['page'])
            if isinstance(data['page'], int):
                page_num = data['page']
            else:
                # Extract digits from strings like "Page 1"
                digits = ''.join(filter(str.isdigit, page_str))
                page_num = int(digits) if digits else 0
                
            chunk_hash = hashlib.md5(" ".join(chunk_text).encode('utf-8')).hexdigest()
            chunk_hash_split=chunk_hash[:6]   
            
            chunk_id = f"{page_num:04d}_{sent_positions[i][0]:04d}_{self.chunk_size}_{chunk_hash_split}"
            
            # Build rich chunk with structural information
            rich_chunk = {
                "page": data["page"],
                "source": data["source"],
                "chunk_start_pos": sent_positions[i][0],
                "chunk_end_pos": sent_positions[i + max_size - 1][1],
                "chunk_text": chunk_text,
                "chunk_id": chunk_id,
                "num_sentences": max_size
            }
            
            # Add structural context if present
            if current_structure:
                struct_type, struct_text = current_structure
                rich_chunk["structure_type"] = struct_type
                rich_chunk["structure_text"] = struct_text
                
            # Add scenario context if present
            if current_scenario:
                scenario_type, scenario_text, parent_example = current_scenario
                rich_chunk["scenario_type"] = scenario_type
                rich_chunk["scenario_text"] = scenario_text
                rich_chunk["parent_example"] = parent_example
            
            yield rich_chunk
            
            if i + max_size >= len(sentences):
                break

class SemanticChunker:
    """
    A class for semantic chunking of text using embeddings to find natural breakpoints
    where the semantic meaning changes significantly.
    """
    
    def __init__(
        self, 
        api_key: str,
        api_base_url: str = "https://api.lamini.ai/inf",
        embedding_model: str = "text-embedding-3-small",
        window_size: int = 1,
        breakpoint_percentile: float = 95.0
    ):
        """
        Initialize the SemanticChunker.
        
        Args:
            api_key: API key for OpenAI
            api_base_url: Base URL for API (default is OpenAI's base URL)
            embedding_model: Name of the embedding model to use
            window_size: Number of sentences before and after to include in window (default=1)
            breakpoint_percentile: Percentile threshold for determining breakpoints (default=95)
        """

        # Initialize the OpenAI client
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=api_base_url,
        )
        
        self.embedding_model = embedding_model
        self.window_size = window_size
        self.breakpoint_percentile = breakpoint_percentile
        self.sentences = []
        self.distances = []
        self.breakpoints = []
        
    def split_into_sentences(self, text: str) -> List[Dict[str, Any]]:
        """Split text into sentences and create a list of sentence dictionaries."""
        # Simple regex-based sentence splitting (can be improved with better NLP techniques)
        single_sentences_list = re.split(r'(?<=[.?!])\s+', text)
        
        # Create dictionaries for each sentence
        return [{'sentence': x, 'index': i} for i, x in enumerate(single_sentences_list)]
    
    def create_sentence_windows(self, sentences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create a sliding window of sentences to capture context."""
        for i in range(len(sentences)):
            combined_sentence = ''
            
            # Add sentences before current one based on window size
            for j in range(i - self.window_size, i):
                if j >= 0:
                    combined_sentence += sentences[j]['sentence'] + ' '
            
            # Add current sentence
            combined_sentence += sentences[i]['sentence']
            
            # Add sentences after current one based on window size
            for j in range(i + 1, i + 1 + self.window_size):
                if j < len(sentences):
                    combined_sentence += ' ' + sentences[j]['sentence']
            
            # Store combined sentences in dictionary
            sentences[i]['combined_sentence'] = combined_sentence
            
        return sentences
    
    def get_embeddings(self, sentences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get embeddings for all combined sentences using the OpenAI API."""
        print("Generating embeddings...")
        
        # Process in batches to avoid API limits
        batch_size = 100  # Adjust based on API limits
        all_sentences = [x['combined_sentence'] for x in sentences]
        
        for i in range(0, len(sentences), batch_size):
            batch = all_sentences[i:i+batch_size]
            
            # Get embeddings for the current batch
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=batch,
                encoding_format="float"
            )
            
            # Extract embeddings from response
            for j, embedding_obj in enumerate(response.data):
                sentences[i+j]['combined_sentence_embedding'] = embedding_obj.embedding
        
        return sentences
    
    def calculate_distances(self, sentences: List[Dict[str, Any]]) -> Tuple[List[float], List[Dict[str, Any]]]:
        """Calculate cosine distances between sequential sentence embeddings."""
        distances = []
        
        for i in range(len(sentences) - 1):
            embedding_current = sentences[i]['combined_sentence_embedding']
            embedding_next = sentences[i + 1]['combined_sentence_embedding']
            
            # Calculate cosine similarity
            similarity = cosine_similarity([embedding_current], [embedding_next])[0][0]
            
            # Convert to cosine distance
            distance = 1 - similarity
            
            # Append distance to list
            distances.append(distance)
            
            # Store distance in sentence dictionary
            sentences[i]['distance_to_next'] = distance
        
        return distances, sentences
    
    def find_breakpoints(self, distances: List[float]) -> List[int]:
        """Find breakpoints where distance exceeds threshold."""
        threshold = np.percentile(distances, self.breakpoint_percentile)
        return [i for i, x in enumerate(distances) if x > threshold]
    
    def create_chunks(self, sentences: List[Dict[str, Any]], breakpoints: List[int]) -> List[str]:
        """Create text chunks based on breakpoints."""
        chunks = []
        start_index = 0
        
        for index in breakpoints:
            # End index is the current breakpoint
            end_index = index
            
            # Slice sentences from start to end index
            group = sentences[start_index:end_index + 1]
            combined_text = ' '.join([d['sentence'] for d in group])
            chunks.append(combined_text)
            
            # Update start index for next group
            start_index = index + 1
        
        # Add the final chunk if any sentences remain
        if start_index < len(sentences):
            combined_text = ' '.join([d['sentence'] for d in sentences[start_index:]])
            chunks.append(combined_text)
            
        return chunks
    
    def visualize_chunks(self, distances: List[float], breakpoints: List[int], save_path=None):
        """Visualize the chunks and breakpoints."""
        plt.figure(figsize=(12, 6))
        plt.plot(distances)
        
        # Set plot limits
        y_upper_bound = max(distances) * 1.2 if max(distances) > 0.2 else 0.2
        plt.ylim(0, y_upper_bound)
        plt.xlim(0, len(distances))
        
        # Draw threshold line
        threshold = np.percentile(distances, self.breakpoint_percentile)
        plt.axhline(y=threshold, color='r', linestyle='-')
        
        # Display number of chunks
        plt.text(x=(len(distances)*0.01), y=y_upper_bound/50, 
                 s=f"{len(breakpoints) + 1} Chunks")
        
        # Shade regions for each chunk
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        
        for i, breakpoint_index in enumerate(breakpoints):
            start_index = 0 if i == 0 else breakpoints[i - 1]
            end_index = breakpoint_index
            
            plt.axvspan(start_index, end_index, 
                        facecolor=colors[i % len(colors)], alpha=0.25)
            plt.text(x=np.average([start_index, end_index]),
                     y=threshold + (y_upper_bound)/20,
                     s=f"Chunk #{i}", horizontalalignment='center',
                     rotation='vertical')
        
        # Shade the final chunk
        if breakpoints:
            last_breakpoint = breakpoints[-1]
            if last_breakpoint < len(distances):
                plt.axvspan(last_breakpoint, len(distances), 
                            facecolor=colors[len(breakpoints) % len(colors)], alpha=0.25)
                plt.text(x=np.average([last_breakpoint, len(distances)]),
                         y=threshold + (y_upper_bound)/20,
                         s=f"Chunk #{len(breakpoints)}",
                         rotation='vertical')
        
        plt.title("Text Chunks Based On Embedding Breakpoints")
        plt.xlabel("Index of sentences in text (Sentence Position)")
        plt.ylabel("Cosine distance between sequential sentences")
        
        if save_path:
            plt.savefig(save_path)
        
        plt.show()
    
    def chunk_text(self, text: str, visualize: bool = False, save_viz_path=None) -> List[str]:
        """
        Main method to chunk text semantically.
        
        Args:
            text: The text to chunk
            visualize: Whether to produce a visualization (default=False)
            save_viz_path: Path to save visualization (optional)
            
        Returns:
            List of text chunks
        """
        # Process the text
        self.sentences = self.split_into_sentences(text)
        self.sentences = self.create_sentence_windows(self.sentences)
        self.sentences = self.get_embeddings(self.sentences)
        self.distances, self.sentences = self.calculate_distances(self.sentences)
        self.breakpoints = self.find_breakpoints(self.distances)
        
        # Create chunks
        chunks = self.create_chunks(self.sentences, self.breakpoints)
        
        # Visualize if requested
        if visualize:
            self.visualize_chunks(self.distances, self.breakpoints, save_viz_path)
        
        return chunks
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return metadata about the chunking process."""
        return {
            'num_sentences': len(self.sentences),
            'num_chunks': len(self.breakpoints) + 1,
            'breakpoints': self.breakpoints,
            'breakpoint_percentile': self.breakpoint_percentile,
            'window_size': self.window_size,
            'threshold': np.percentile(self.distances, self.breakpoint_percentile) if self.distances else None
        }
        

class PDFSemanticChunker(SemanticChunker):
    """
    A class for semantic chunking of PDF documents that inherits from SemanticChunker
    and adds PDF-specific functionality and rich metadata.
    """
    
    def __init__(
        self, 
        api_key: str,
        api_base_url: str = "https://api.lamini.ai/inf",
        embedding_model: str = "text-embedding-3-small",
        window_size: int = 1,
        breakpoint_percentile: float = 95.0,
        include_page_numbers: bool = True,
        include_document_info: bool = True
    ):
        """
        Initialize the PDFSemanticChunker.
        
        Args:
            api_key: API key for OpenAI
            api_base_url: Base URL for API (default is OpenAI's base URL)
            embedding_model: Name of the embedding model to use
            window_size: Number of sentences before and after to include in window (default=1)
            breakpoint_percentile: Percentile threshold for determining breakpoints (default=95)
            include_page_numbers: Whether to include page numbers in chunk metadata
            include_document_info: Whether to include document info in chunk metadata
        """
        # Initialize the parent class (SemanticChunker)
        super().__init__(
            api_key=api_key,
            api_base_url=api_base_url,
            embedding_model=embedding_model,
            window_size=window_size,
            breakpoint_percentile=breakpoint_percentile
        )
        
        # Additional PDF-specific attributes
        self.include_page_numbers = include_page_numbers
        self.include_document_info = include_document_info
        self.page_breaks = []
        self.document_info = {}
    
    def get_chunks(self, data: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        Convert the provided data into semantically chunked pieces with rich metadata.
        Compatible with the PDFLoader interface.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing at least a "content" key with text to chunk,
            and "source" and "page" keys.
            
        Yields
        ------
        Dict[str, Any]
            Rich chunk dictionaries with standardized keys matching PDFSentenceChunker output.
        """
        # Extract content and metadata
        content = data["content"]
        source = data.get("source", "unknown")
        page_info = data.get("page", "Page 1")
        
        # Process text using the semantic chunking method
        semantic_chunks = self.chunk_text(content, visualize=False)
        
        # Track sentence positions in original text for metadata
        sentences = tokenize.sent_tokenize(content)
        sent_positions = []
        last_pos = 0
        for sent in sentences:
            start_pos = content.find(sent, last_pos)
            end_pos = start_pos + len(sent)
            sent_positions.append((start_pos, end_pos))
            last_pos = end_pos
        
        # Convert semantic chunks to rich chunks with standardized format
        for i, chunk_text in enumerate(semantic_chunks):
            # Find the start and end position of chunk in the content
            chunk_start_pos = content.find(chunk_text)
            if chunk_start_pos == -1:
                # Try finding the first sentence of the chunk
                first_sentence = tokenize.sent_tokenize(chunk_text)[0]
                chunk_start_pos = content.find(first_sentence)
                if chunk_start_pos == -1:
                    # Fallback to approximate position based on chunk index
                    chunk_start_pos = i * (len(content) // max(1, len(semantic_chunks)))
            
            chunk_end_pos = chunk_start_pos + len(chunk_text)
            
            # Count sentences in this chunk
            chunk_sentences = tokenize.sent_tokenize(chunk_text)
            num_sentences = len(chunk_sentences)
            
            # Determine page number (use default if not multi-page content)
            if isinstance(page_info, str) and page_info.startswith("Page "):
                page_num = int(page_info.replace("Page ", ""))
            else:
                page_num = 1
                
            # Generate chunk hash for ID
            chunk_hash = hashlib.md5(chunk_text.encode('utf-8')).hexdigest()
            chunk_hash_split = chunk_hash[:6]
            
            # Create standardized rich chunk
            rich_chunk = {
                "page": page_info,
                "source": source,
                "chunk_start_pos": chunk_start_pos,
                "chunk_end_pos": chunk_end_pos,
                "chunk_text": chunk_text + " \n",  # Match format with trailing newline
                "chunk_id": f"{page_num:04d}_{chunk_start_pos:04d}_{self.window_size}_{chunk_hash_split}",
                "num_sentences": num_sentences
            }
            
            yield rich_chunk
    
    def get_structured_chunks(self, data: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        Placeholder for structured chunks method to maintain API compatibility.
        This implementation uses the same semantic chunking approach as get_chunks().
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing at least a "content" key with text to chunk,
            and "source" and "page" keys.
            
        Yields
        ------
        Dict[str, Any]
            Rich chunk dictionaries with standardized keys matching PDFSentenceChunker output.
        """
        # For now, just use the same implementation as get_chunks
        yield from self.get_chunks(data)
               
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, List[int], Dict[str, Any]]:
        """
        Extract text from a PDF file with page break indices.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple containing:
            - Full text of the PDF
            - List of character indices where page breaks occur
            - Dictionary with document metadata
        """
        # Open the PDF file
        doc = fitz.open(pdf_path)
        
        # Extract document metadata
        metadata = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "filename": os.path.basename(pdf_path),
            "filepath": pdf_path,
            "page_count": len(doc),
            "file_size_bytes": os.path.getsize(pdf_path)
        }
        
        # Extract text with page breaks
        full_text = ""
        page_breaks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            if page_num > 0:
                # Record the character position where this page starts
                page_breaks.append(len(full_text))
            
            # Extract text from the current page
            page_text = page.get_text()
            full_text += page_text
        
        doc.close()
        return full_text, page_breaks, metadata
    
    def determine_page_for_chunk(self, chunk: str, text: str, page_breaks: List[int]) -> List[int]:
        """
        Determine which page(s) a chunk comes from.
        
        Args:
            chunk: The text chunk
            text: The full text of the PDF
            page_breaks: List of character indices where page breaks occur
            
        Returns:
            List of page numbers (0-indexed) that the chunk spans
        """
        # Find the start and end position of the chunk in the full text
        # Note: This is a simple implementation that may not work for all cases,
        # especially if the chunk text appears multiple times in the document
        chunk_start = text.find(chunk)
        if chunk_start == -1:
            # Fallback if exact match fails - try to find the first sentence
            first_sentence = re.split(r'(?<=[.?!])\s+', chunk)[0]
            chunk_start = text.find(first_sentence)
            if chunk_start == -1:
                return []  # Couldn't find the chunk
        
        chunk_end = chunk_start + len(chunk)
        
        # Determine which pages this span covers
        pages = []
        
        # Check first page (before first page break)
        if chunk_start < page_breaks[0] if page_breaks else float('inf'):
            pages.append(0)
        
        # Check middle pages
        for i in range(len(page_breaks) - 1):
            if (chunk_start < page_breaks[i+1] and chunk_end > page_breaks[i]) or \
               (chunk_start >= page_breaks[i] and chunk_start < page_breaks[i+1]):
                pages.append(i + 1)
        
        # Check last page
        if page_breaks and chunk_end > page_breaks[-1]:
            pages.append(len(page_breaks))
            
        return pages
    
    def enrich_chunks_with_metadata(
        self, 
        chunks: List[str], 
        text: str, 
        page_breaks: List[int], 
        document_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Enrich chunks with metadata about their origin.
        
        Args:
            chunks: List of text chunks
            text: The full text of the PDF
            page_breaks: List of character indices where page breaks occur
            document_info: Dictionary with document metadata
            
        Returns:
            List of dictionaries with chunk text and metadata
        """
        enriched_chunks = []
        
        for i, chunk in enumerate(chunks):
            
            chunk_hash = hashlib.md5(" ".join(chunk).encode('utf-8')).hexdigest()
            chunk_hash_split=chunk_hash[:6]   
            word_c=len(chunk.split())
            chunk_metadata = {
                "chunk_id": f"{word_c:04d}_{chunk_hash_split}",
                "text": chunk,
                "char_count": len(chunk),
                "word_count": len(chunk.split()),
                "sentence_count": len(re.split(r'(?<=[.?!])\s+', chunk)),
            }
            
            # Add page information if requested
            if self.include_page_numbers:
                pages = self.determine_page_for_chunk(chunk, text, page_breaks)
                chunk_metadata["pages"] = [p + 1 for p in pages]  # Convert to 1-indexed
                chunk_metadata["page_span"] = f"{min(chunk_metadata['pages']) if chunk_metadata['pages'] else 'unknown'}-{max(chunk_metadata['pages']) if chunk_metadata['pages'] else 'unknown'}"
            
            # Add document information if requested
            if self.include_document_info:
                chunk_metadata["document"] = document_info["filename"]
                chunk_metadata["document_title"] = document_info["title"]
                # Add any other document metadata you want to include
            
            enriched_chunks.append(chunk_metadata)
            
        return enriched_chunks
    
    def chunk_pdf(
        self, 
        pdf_path: str, 
        visualize: bool = False, 
        save_viz_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a PDF file and return semantically chunked text with metadata.
        
        Args:
            pdf_path: Path to the PDF file
            visualize: Whether to produce a visualization (default=False)
            save_viz_path: Path to save visualization (optional)
            
        Returns:
            List of dictionaries containing chunks with standardized metadata
        """
        # Extract text and metadata from PDF
        text, page_breaks, document_info = self.extract_text_from_pdf(pdf_path)
        
        # Store for later use
        self.page_breaks = page_breaks
        self.document_info = document_info
        
        # Use the parent class's chunk_text method
        text_chunks = super().chunk_text(text, visualize, save_viz_path)
        
        # Create standardized rich chunks
        standardized_chunks = []
        
        for i, chunk in enumerate(text_chunks):
            # Create unique hash for chunk ID
            chunk_hash = hashlib.md5(chunk.encode('utf-8')).hexdigest()
            chunk_hash_split = chunk_hash[:6]
            
            # Determine page for the chunk
            pages = self.determine_page_for_chunk(chunk, text, page_breaks)
            page_num = min(pages) + 1 if pages else 1  # Convert to 1-indexed
            
            # Approximate chunk positions in text
            chunk_start_pos = text.find(chunk)
            if chunk_start_pos == -1:
                # Fallback if exact match fails
                first_sentence = re.split(r'(?<=[.?!])\s+', chunk)[0]
                chunk_start_pos = text.find(first_sentence)
                if chunk_start_pos == -1:
                    chunk_start_pos = 0
            chunk_end_pos = chunk_start_pos + len(chunk)
            
            # Count sentences
            num_sentences = len(re.split(r'(?<=[.?!])\s+', chunk))
            
            # Create standardized rich chunk
            rich_chunk = {
                "page": f"Page {page_num}",
                "source": os.path.basename(pdf_path),
                "chunk_start_pos": chunk_start_pos,
                "chunk_end_pos": chunk_end_pos,
                "chunk_text": chunk + " \n",  # Match format with trailing newline
                "chunk_id": f"{page_num:04d}_{chunk_start_pos:04d}_{self.window_size}_{chunk_hash_split}",
                "num_sentences": num_sentences
            }
            
            standardized_chunks.append(rich_chunk)
        
        return standardized_chunks
    
    def chunk_pdfs(
        self, 
        pdf_paths: List[str], 
        visualize: bool = False, 
        save_viz_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Process multiple PDF files and return semantically chunked text with metadata.
        
        Args:
            pdf_paths: List of paths to PDF files
            visualize: Whether to produce a visualization (default=False)
            save_viz_path: Path pattern to save visualizations (optional)
            
        Returns:
            List of dictionaries containing chunks with metadata
        """
        all_chunks = []
        
        for i, pdf_path in enumerate(pdf_paths):
            viz_path = None
            if visualize and save_viz_path:
                # Create a unique path for each PDF's visualization
                filename = os.path.basename(pdf_path).split('.')[0]
                viz_path = save_viz_path.replace('.png', f'_{filename}.png')
            
            # Process each PDF
            pdf_chunks = self.chunk_pdf(pdf_path, visualize, viz_path)
            
            # Add to the combined list
            all_chunks.extend(pdf_chunks)
        
        return all_chunks
    
    def get_pdf_metadata(self) -> Dict[str, Any]:
        """
        Get PDF-specific metadata.
        
        Returns:
            Dictionary with metadata about the PDF documents
        """
        pdf_metadata = {
            "document_info": self.document_info,
            "page_breaks": self.page_breaks,
        }
        
        return pdf_metadata
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get combined metadata about the chunking process and documents.
        
        Returns:
            Dictionary with metadata about chunking and documents
        """
        # Get chunking metadata from the parent class
        chunking_metadata = super().get_metadata()
        
        # Get PDF-specific metadata
        pdf_metadata = self.get_pdf_metadata()
        
        # Combine metadata
        combined_metadata = {
            **chunking_metadata,
            **pdf_metadata,
        }
        
        return combined_metadata