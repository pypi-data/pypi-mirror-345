import re
import os
import sys
import logging
import json
from typing import Generator, List, Dict, Any, Optional, Tuple
from pypdf import PdfReader

from models.chunking.chunking import BaseChunker

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseLoader:
    """Hanlder for data loading through a generator
    """

    def load(self) -> Generator[Dict[str, Any], None, None]:
        """Template generator for data loading
        """
        pass


class DictLoader(BaseLoader):
    """Handler for loading in content of a JSON

    Parameters
    ----------
    chunker: BaseChunker
        Handler for breaking the text content into chunks

    json: str
        Location of json to load

    batch_size: int = 128
        Batch size of returned chunks from chunker
    
    """

    def __init__(
            self, 
            chunker: BaseChunker, 
        ):
        self.sources = []
        self.entries = {}
        self.chunker = chunker

    def load_json(self, json_name: str, json_path: str, extract_keys: Optional[List[str]] = []) -> None:
        """Loading function to iterate through a JSON and extract the contents.
        This builds an entries list property that contains dictionaries with either all
        available keys in the json or only the provided extract_keys if given.

        Parameters
        ----------
        json_name: str
            Name of json file
        
        json_path: str
            Path to the json to be loaded

        extract_keys: Optional[str] = {}
            Keys to only extract if provided

        Returns
        -------
        None
        """

        with open(json_path) as fp:
            self.sources.append(json_name)
            with open(json_path) as fp:
                contents = json.load(fp)

            if extract_keys:
                new_entry = {}
                for key_ in contents:
                    if key_ in extract_keys:
                        if isinstance(contents[key_], dict):
                            new_entry.update(contents[key_])
                        else:
                            new_entry[key_] = contents[key_]
            else:
                new_entry = contents
                
            self.entries[json_name] = new_entry

    def get_chunks(self, data: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """Getter which calls the provided chunker to build the chunking
        generator.

        Parameters
        ----------
        data: Dict[str, Any]
            Dictionary containing at least a "content" key with the text to be chunked.
            Optional keys include "source" and "page".

        Returns
        -------
        Generator:
            The chunking generator from the chunker yielding chunk dictionaries
        """
        if "content" not in data:
            raise ValueError("Input dictionary must contain a 'content' key")

        # Ensure required keys exist with defaults
        data.setdefault("source", "unknown")
        data.setdefault("page", 1)

        return self.chunker.get_chunks(data)

    def get_chunk_batches(self, file: str, content_keys: Optional[List[str]]) -> Generator[List[str], None, None]:
        """A generator that yields batches of chunks
        Each batch is a list of strings, each a substring of the text with length self.batch_size
        the last element of the list may be shorter than self.batch_size

        Parameters
        ----------
        content_key: Optional[str]
            If passed in, then self.load() will only be loading in the contents of this key

        Yields
        -------
        file: str
            file to load
        
        chunks: List[str]
            Batch of chunks of size self.batch_size
            
        """

        chunks = []
        for chunk in self.get_chunks(self.entries[file]):
            new_chunk = {
                "_id": file,
                "chunk": chunk
            }
            new_chunk.update({key_: self.entries[file][key_] for key_ in content_keys})
            chunks.append(new_chunk)

        return chunks

    def load(self, file: str, content_keys: List[str]) -> Dict[str, Any]:
        """Load the data from self.entries

        Parameters
        ----------
        file: str
            file to load
            
        content_key: Optional[str]
            If provided, then only the provided json key is loaded

        Yields
        -------
        chunks: List[str]
            Batch of chunks of size self.batch_size
        """

        return {key_: self.entries[file][key_] for key_ in content_keys}

    def __call__(self, content_keys: List[str]):
        """Intended for parameter driven iteration for calling self.get_chunk_batches()

        Parameters
        ----------
        content_keys: List[str]
            Keys to extract from the json

        Returns
        -------
        Generator[List[str], None, None]
            Output generator from self.get_chunk_batches()
        """
        for entry in self.entries:
             yield self.get_chunk_batches(entry, content_keys)

    def __len__(self) -> int:
        """Return the length as defined from the number of chunks

        Parameters
        ----------
        None

        Returns
        -------
        int
        """

        return len(list(self.get_chunks()))
    
class PDFLoader(BaseLoader):
    """Handler for loading in content of a PDF

    Parameters
    ----------
    pdf_path: str
        Location of pdf to load

    chunker: BaseChunker
        Handler for breaking the text content of a PDF into 
        chunks

    batch_size: int = 128
        Batch size of returned chunks from chunker

    limit: int  = 1000
        Chunk load limit
    
    """

    def __init__(
            self, 
            chunker: BaseChunker, 
            pdf_path: str = "",
            batch_size: int = 128, 
        ):
        super().__init__()
        self.sources = []
        self.pages = []
        self.rich_chunks = []
        self.structured_chunks = []  # New list for structured chunks
        self.batch_size = batch_size
        self.chunker = chunker
        self.all_chunks = []  # New combined list
        
        if pdf_path:
            if os.path.isdir(pdf_path):
                # Load all PDFs in directory
                for filename in os.listdir(pdf_path):
                    if filename.lower().endswith('.pdf'):
                        full_path = os.path.join(pdf_path, filename)
                        self.load_pdf(pdf_name=filename, pdf_path=full_path)
            elif os.path.isfile(pdf_path) and pdf_path.lower().endswith('.pdf'):
                # Load single PDF file
                filename = os.path.basename(pdf_path)
                self.load_pdf(pdf_name=filename, pdf_path=pdf_path)
            else:
                raise ValueError(f"Path {pdf_path} is neither a PDF file nor a directory containing PDFs")
            
            # Generate both types of chunks and combine them
            self.rich_chunks = list(self.get_chunks())
            
            # Generate structured chunks if the chunker supports it
            if hasattr(self.chunker, 'get_structured_chunks'):
                self.structured_chunks = list(self.get_structured_chunks())
                # Combine both types of chunks into all_chunks
                self.all_chunks = self.rich_chunks + self.structured_chunks
            else:
                logger.warning("Chunker does not support structured chunks")
                self.all_chunks = self.rich_chunks

    def load_pdf(self, pdf_name: str, pdf_path: str, page_range: Tuple[int, int] = None) -> None:
        """Loading function to iterate through a PDF and extract the content of a page.
        This builds an entries list property that contains dictionaries with both the
        page number in the key "page" and the content within the key "content".

        Parameters
        ----------
        pdf_name: str
            Name of pdf
        
        pdf_path: str
            Path to the pdf to be loaded

        page_range: Tuple[int, int]
            Inclusive start and end of the pages to use in loading

        Returns
        -------
        None
        """

        logger.info(f"<--UIMESSAGE-->Reading your PDF: Analyzing domain patterns and identifying key relationships in {pdf_name}...</--UIMESSAGE-->")

        with open(pdf_path, "rb") as fp:
            self.sources.append(pdf_name)
            reader = PdfReader(fp)
            for idx, page in enumerate(reader.pages):
                if page_range:
                    if idx < page_range[0] or idx > page_range[1]:
                        continue
                        
                text = page.extract_text()
                text = re.sub(' +', ' ', text.replace("\n","")).strip()
            
                new_entry = {
                    "source": pdf_name,
                    "page": f"Page {idx+1}",
                    "content": text
                }
                self.pages.append(new_entry)
            
    def get_first_pages(self, pdf_name: str, num_pages: int) -> str:
        """Loading function to iterate through a PDF and extract the content of a page.
        This builds an entries list property that contains dictionaries with both the
        page number in the key "page" and the content within the key "content".

        Parameters
        ----------
        pdf_name: str
            PDF name, this file should already exist in the loader

        num_pages: int
            Number of pages to load from the begining of the file
        Returns
        -------
        str
            Combined string of the first {num_pages} of the file {pdf_name}
        """

        if pdf_name not in self.sources:
            raise ValueError(f"{pdf_name} not present within the loader. Be sure to call 'load_pdf' before calling get_first_pages.")

        combined_entries = ""
        for entry in [entry for entry in self.pages if entry["source"] == pdf_name]:
            if entry["page"] <= f"Page {num_pages}":
                combined_entries += entry["content"] + "\n\n"

        return combined_entries

    def get_chunks(self, pdf_name: Optional[str] = None) -> Generator[str, None, None]:
        """Getter which calls the provided chunker to build the chunking
        generator.

        Parameters
        ----------
        pdf_name: Optional[str]
            If passed in, then only entries from this file are processed. 
            If None, processes all loaded PDFs.

        Returns
        -------
        Generator:
            The chunking generator from the chunker
        """
        if pdf_name is not None and pdf_name not in self.sources:
            raise ValueError(f"PDF '{pdf_name}' not found in loaded sources")

        # Process all pages or filter by PDF name
        pdf_pages = [page for page in self.pages if pdf_name is None or page["source"] == pdf_name]
        
        for page in pdf_pages:
            for chunk in self.chunker.get_chunks(page):
                yield chunk

    def get_chunk_batches(self, pdf_name: str = None) -> Generator[List[Dict[str, Any]], None, None]:
        """Generator yielding batches of chunks from PDFs.

        Parameters
        ----------
        pdf_name: str, optional
            Name of the PDF to process. If None, processes all loaded PDFs.

        Yields
        -------
        batch: List[Dict[str, Any]]
            List of chunk dictionaries containing metadata and text
        """
        if pdf_name is not None and pdf_name not in self.sources:
            raise ValueError(f"PDF '{pdf_name}' not found in loaded sources")

        batch = []
        # Process all pages or filter by PDF name
        pdf_pages = [page for page in self.pages if pdf_name is None or page["source"] == pdf_name]
        
        for page in pdf_pages:
            for chunk in self.chunker.get_chunks(page):
                batch.append(chunk)
                if len(batch) >= self.batch_size:
                    yield batch
                    batch = []
        
        if batch:  # Yield any remaining chunks
            yield batch

    def load(self, pdf_name: Optional[str]) -> Generator[Dict[str, Any], None, None]:
        """Load the data from self.entries

        Parameters
        ----------
        pdf_name: Optional[str]
            If provided, then only entries from this file are loaded

        Yields
        -------
        chunks: List[str]
            Batch of chunks of size self.batch_size
        """

        for _, obj in enumerate(self.pages):
            if pdf_name and obj["source"] != pdf_name:
                continue
            yield obj

    def __iter__(self) -> Generator[List[str], None, None]:
        """Iteration method handled by calling self.get_chunk_batches()

        Parameters
        ----------
        None

        Returns
        -------
        Generator[List[str], None, None]
            Output generator from self.get_chunk_batches()
        """

        return self.get_chunk_batches()

    def __len__(self) -> int:
        """Return the length as defined from the number of chunks

        Parameters
        ----------
        None

        Returns
        -------
        int
        """

        return len(list(self.get_chunks()))

    def get_structured_chunks(self, pdf_name: Optional[str] = None) -> Generator[str, None, None]:
        """Getter which calls the chunker's get_structured_chunks method.
        Combines all pages into a single document before chunking to preserve
        section structure across page boundaries.

        Parameters
        ----------
        pdf_name: Optional[str]
            If passed in, then only entries from this file are processed. 
            If None, processes all loaded PDFs.

        Returns
        -------
        Generator:
            The structured chunking generator from the chunker
        """
        if pdf_name is not None and pdf_name not in self.sources:
            raise ValueError(f"PDF '{pdf_name}' not found in loaded sources")

        # Process documents one at a time
        if pdf_name:
            pdf_names = [pdf_name]
        else:
            pdf_names = self.sources

        for current_pdf in pdf_names:
            # Get all content for this PDF using existing load() function
            full_document = ""
            for page_data in self.load(current_pdf):
                full_document += page_data["content"] + " "
            
            # Create combined document
            combined_document = {
                "source": current_pdf,
                "page": "Full Document",
                "content": full_document.strip()
            }
            
            # Process the entire document at once
            for chunk in self.chunker.get_structured_chunks(combined_document):
                yield chunk

    def get_all_chunks(self, pdf_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get both regular and structured chunks combined.

        Parameters
        ----------
        pdf_name: Optional[str]
            If passed in, then only entries from this file are returned.
            If None, returns chunks from all loaded PDFs.

        Returns
        -------
        List[Dict[str, Any]]
            Combined list of regular and structured chunks
        """
        if not self.rich_chunks:
            self.rich_chunks = list(self.get_chunks(pdf_name))
        
        if not self.structured_chunks and hasattr(self.chunker, 'get_structured_chunks'):
            self.structured_chunks = list(self.get_structured_chunks(pdf_name))
            
        # Filter by pdf_name if specified
        if pdf_name:
            regular_chunks = [c for c in self.rich_chunks if c['source'] == pdf_name]
            struct_chunks = [c for c in self.structured_chunks if c['source'] == pdf_name]
        else:
            regular_chunks = self.rich_chunks
            struct_chunks = self.structured_chunks
            
        return regular_chunks + struct_chunks
    