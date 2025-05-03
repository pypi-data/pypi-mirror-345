from pathlib import Path
import logging
import tempfile
import os
import time
from openai import OpenAI
from tqdm import tqdm
import pandas as pd
from zipfile import ZipFile
import json
import shutil
from docling.datamodel.pipeline_options import smolvlm_picture_description, PdfPipelineOptions, AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)
from docling.datamodel.settings import settings
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
# from models.generators.table_description_generator import TableDescriptionGenerator
from lamini.experiment.generators.table_description_generator import TableDescriptionGenerator
from lamini.generation.base_prompt_object import PromptObject
import re

# ---------------------------
# Utility Functions
# ---------------------------

def combine_ingest_data(ingested_pdf_data):
    """
    Combines various components of ingested PDF data into a single content string.

    Parameters
    ----------
    ingested_pdf_data : dict
        A dictionary containing processed PDF data with keys "full_data_sections",
        "image_descriptions", "all_tables_df", and "all_tables_descriptions".

    Returns
    -------
    str
        A formatted string that includes:
        - Full document sections
        - Image descriptions in a JSON-like format
        - Tables with their corresponding descriptions
    """
    combined_content = ""
    
    # Append full data sections
    combined_content += "Full Data Sections:\n"
    for section_title, section_text in ingested_pdf_data["full_data_sections"].items():
        combined_content += f"Section: {section_title}\n{section_text}\n\n"
    
    # Append image descriptions
    combined_content += "Image Descriptions:\n"
    for key, desc in ingested_pdf_data["image_descriptions"].items():
        # Convert the image description dict to a formatted JSON string
        desc_text = json.dumps(desc, indent=2)
        combined_content += f"Image {key}:\n{desc_text}\n\n"
    
    # Append tables with their corresponding descriptions
    combined_content += "Tables and Descriptions:\n"
    all_tables = ingested_pdf_data["all_tables_df"]
    all_table_descriptions = ingested_pdf_data["all_tables_descriptions"]
    
    for idx, table in enumerate(all_tables):
        combined_content += f"Table {idx+1}:\n"
        # Append the table description if available
        if idx < len(all_table_descriptions):
            combined_content += f"Description: {all_table_descriptions[idx]}\n"
        else:
            combined_content += "Description: Not available\n"
        
        # Convert the table to a string for display
        if isinstance(table, pd.DataFrame):
            table_str = table.to_string(index=False)
        else:
            table_str = pd.DataFrame(table).to_string(index=False)
        combined_content += table_str + "\n\n"
    
    return combined_content

def add_table_descriptions(md_content, descriptions):
    # Regular expression for detecting table mentions and paragraphs in markdown
    table_regex = re.compile(r"(Table\s*[\d]+|table\s*[\d]+)", re.IGNORECASE)
    paragraph_regex = re.compile(r"(?:\r?\n){2,}")  # Detects paragraph boundaries by identifying two or more newlines

    matches = list(table_regex.finditer(md_content))

    # Dictionary to keep track of which tables have already had descriptions added
    tables_with_descriptions_added = set()

    for match in reversed(matches):
        # Extract table number
        table_number = re.search(r"[\d]+", match.group()).group()
        description_key = str(int(table_number))  # Convert to integer to match JSON keys

        # Find the end of the current paragraph
        paragraph_end_match = paragraph_regex.search(md_content, match.end())
        paragraph_end = paragraph_end_match.start() if paragraph_end_match else len(md_content)

        # Only add the description if it hasn't been added already
        if description_key in descriptions and description_key not in tables_with_descriptions_added:
            description_text = descriptions[description_key]['Descriptions']
            # Insert the description at the end of the paragraph containing the table mention
            insert_position = paragraph_end
            md_content = (
                md_content[:insert_position]
                + f"\n\n**Table {table_number} Description:** {description_text}\n\n"
                + md_content[insert_position:]
            )
            # Mark this table as having its description added
            tables_with_descriptions_added.add(description_key)

    return md_content

def add_figure_descriptions(md_content, descriptions):
    """
    Adds figure descriptions to markdown content in place of image references.

    Parameters
    ----------
    md_content : str
        The markdown content containing image references.
    descriptions : dict
        A dictionary with image descriptions keyed by description number.

    Returns
    -------
    str
        The markdown content with image descriptions inserted, replacing image references.
    """

    # Regular expression for detecting image patterns in markdown
    image_regex = re.compile(r"!\[Image\]\([^)]+\)")

    # Use an iterator to maintain order according to JSON
    description_iter = iter(sorted(descriptions.items(), key=lambda x: int(x[0])))

    matches = list(image_regex.finditer(md_content))
    images_with_descriptions_added = set()

    for match in matches:
        # Get the next image description if available
        try:
            description_key, description_data = next(description_iter)
        except StopIteration:
            break  # No more descriptions available

        if description_key not in images_with_descriptions_added:
            # Construct the replacement text to replace the image reference with the description
            description_text = description_data['Annotations']
            md_content = (
                md_content[:match.start()]
                + f"\n**Image {description_key} Description:** {description_text}\n\n"
                + md_content[match.end():]
            )
            # Mark this image as having its description added
            images_with_descriptions_added.add(description_key)

    return md_content

def load_and_split_markdown_file(file_path):
    """
    Loads a markdown file, splits it into sections based on headers, and removes image references.

    Parameters
    ----------
    file_path : str or Path
        The path to the markdown file to be loaded and processed.

    Returns
    -------
    dict
        A dictionary where keys are section titles and values are the content of those sections
        with image references removed.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Assuming sections start with a markdown header, e.g., "## Section Title"
    # Adjust this regex to match the exact pattern of your section headers
    sections = re.split(r'(?m)^##\s+', content)[1:]  # Skip the first split as it would be empty

    # Create a dictionary to store sections
    section_dict = {}
    for idx, section in enumerate(sections):
        # Use the first line as the key (i.e., section title)
        title, *body = section.splitlines()
        body_content = '\n'.join(body).strip()

        # Remove [Image] references and paths in parentheses from the body content
        body_content_cleaned = re.sub(r'\[Image\]\([^)]+\)', '', body_content)

        section_dict[title.strip()] = body_content_cleaned

    return section_dict

class PDFIngestor:
    """
    PDFIngestor processes all PDFs in a given input directory. For each PDF it extracts:
      - Image descriptions
      - Table data (as a list of dictionaries)
      - Table descriptions
      - Document sections (from a generated markdown file)
    
    For each PDF, a zip file of extracted files is created and moved to the provided output path.
    The final result is a nested dictionary keyed by PDF name.
    """

    def __init__(self, input_path: Path, output_path: Path, table_describer: TableDescriptionGenerator):
        """
        Parameters
        ----------
        input_path : Path
            Directory containing PDF files to ingest.
        output_path : Path
            Directory where zip files and final JSON results will be stored.
        table_describer : TableDescriptionGenerator
            An instance for generating table descriptions.
        """
        
        self.input_path = input_path
        self.output_path = output_path
        self.table_describer = table_describer
        
        # where to store your cache
        self.cache_file = self.output_path / "ingest_cache.json"
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self._log = logging.getLogger(__name__)

    def _ingest_single_pdf(self, pdf_file: Path):
        """
        Ingests a single PDF file and returns a tuple:
          (image_descriptions, all_tables_df, all_tables_descriptions, full_data_sections)
        
        DataFrames in all_tables_df are converted to list-of-dicts.
        """
        IMAGE_RESOLUTION_SCALE = 2.0
        main_path = Path(tempfile.gettempdir())
        # Create a temporary output folder for this PDF
        base_output_dir = main_path / pdf_file.stem
        tables_output_dir = base_output_dir / "tables"
        images_output_dir = base_output_dir / "images"
        tables_output_dir.mkdir(parents=True, exist_ok=True)
        images_output_dir.mkdir(parents=True, exist_ok=True)

        accelerator_options = AcceleratorOptions(num_threads=1, device=AcceleratorDevice.AUTO)
        pipeline_options = PdfPipelineOptions(enable_remote_services=False)
        pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
        pipeline_options.generate_page_images = True
        pipeline_options.do_table_structure = True
        pipeline_options.generate_picture_images = True
        pipeline_options.do_picture_description = True
        pipeline_options.do_formula_enrichment = True
        pipeline_options.accelerator_options = accelerator_options
        pipeline_options.picture_description_options = smolvlm_picture_description
        pipeline_options.picture_description_options.prompt = (
            "Describe the image in details. Be consise and accurate. I want to use your description for RAG"
        )

        doc_converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
        )

        start_time = time.time()
        conv_res = doc_converter.convert(pdf_file)

        # ---------------------------
        # Table Extraction & Export
        # ---------------------------
        all_tables_df = []
        for table_ix, table in tqdm(enumerate(conv_res.document.tables), desc=f"Processing tables in {pdf_file.name}"):
            table_df: pd.DataFrame = table.export_to_dataframe()
            self._log.info(f"Extracting table {table_ix+1} from {pdf_file.name}")
            print(f"## Table {table_ix+1}")
            print(table_df.to_markdown())
            csv_filename = tables_output_dir / f"{pdf_file.stem}-table-{table_ix+1}.csv"
            self._log.info(f"Saving CSV table to {csv_filename}")
            table_df.to_csv(csv_filename, index=False)
            all_tables_df.append(table_df)
            html_filename = tables_output_dir / f"{pdf_file.stem}-table-{table_ix+1}.html"
            self._log.info(f"Saving HTML table to {html_filename}")
            with html_filename.open("w") as fp:
                fp.write(table.export_to_html())
        
        # ---------------------------
        # Figure & Image Extraction
        # ---------------------------
        
        for page_no, page in tqdm(conv_res.document.pages.items(), desc=f"Processing pages in {pdf_file.name}"):
            page_image_filename = images_output_dir / f"{pdf_file.stem}-page-{page_no}.png"
            with page_image_filename.open("wb") as fp:
                page.image.pil_image.save(fp, format="PNG")
            self._log.info(f"Saved page image to {page_image_filename}")
        
        table_counter = 0
        picture_counter = 0
        for element, _level in tqdm(conv_res.document.iterate_items(), desc=f"Processing items in {pdf_file.name}"):
            if isinstance(element, TableItem):
                table_counter += 1
                element_image_filename = images_output_dir / f"{pdf_file.stem}-table-{table_counter}.png"
                with element_image_filename.open("wb") as fp:
                    element.get_image(conv_res.document).save(fp, "PNG")
                self._log.info(f"Saved table image to {element_image_filename}")
            elif isinstance(element, PictureItem):
                picture_counter += 1
                element_image_filename = images_output_dir / f"{pdf_file.stem}-picture-{picture_counter}.png"
                with element_image_filename.open("wb") as fp:
                    element.get_image(conv_res.document).save(fp, "PNG")
                self._log.info(f"Saved picture image to {element_image_filename}")

        md_embedded_filename = images_output_dir / f"{pdf_file.stem}-with-images.md"
        conv_res.document.save_as_markdown(md_embedded_filename, image_mode=ImageRefMode.EMBEDDED)
        self._log.info(f"Saved markdown with embedded images to {md_embedded_filename}")
        
        html_embedded_filename = images_output_dir / f"{pdf_file.stem}-with-images.html"
        conv_res.document.save_as_html(md_embedded_filename, image_mode=ImageRefMode.EMBEDDED)
        self._log.info(f"Saved html with embedded images to {html_embedded_filename}")
        
        md_ref_filename = images_output_dir / f"{pdf_file.stem}-with-image-refs.md"
        conv_res.document.save_as_markdown(md_ref_filename, image_mode=ImageRefMode.REFERENCED)
        self._log.info(f"Saved markdown with referenced images to {md_ref_filename}")
        
        html_ref_filename = images_output_dir / f"{pdf_file.stem}-with-image-refs.html"
        conv_res.document.save_as_html(html_ref_filename, image_mode=ImageRefMode.REFERENCED)
        self._log.info(f"Saved HTML with referenced images to {html_ref_filename}")
        
        end_time = time.time() - start_time
        self._log.info(f"{pdf_file.name} converted and exported in {end_time:.2f} seconds.")
        
        # ---------------------------
        # Generate Descriptions
        # ---------------------------
        image_descriptions = {}
        table_descriptions = {}
        all_tables_descriptions = []
        ID = 0
        ID_tables = 0
        for element, _level in conv_res.document.iterate_items():
            if isinstance(element, PictureItem):
                ID += 1
                image_descriptions[str(ID)] = {
                    'Picture': element.self_ref,
                    'Caption': element.caption_text(doc=conv_res.document),
                    'Annotations': element.annotations[0].text
                }
            elif isinstance(element, TableItem):
                ID_tables += 1
                df = element.export_to_dataframe()
                df_string = df.to_string()
                table_prompt = PromptObject("", data={"dataframe": df_string})
                try: 
                    table_result = self.table_describer(table_prompt)
                    resp = getattr(table_result, "response", {}) or {}
                    # Try the common keys in priority order
                    response_text = (
                        resp.get("table_description")
                        or resp.get("description")
                        or resp.get("text")
                        or ""                     # empty string triggers fallback
                    )
                except Exception as e:
                    self._log.warning(f"Table‑description generator threw: {e!r}")
                    response_text = ""
                table_descriptions[str(ID_tables)] = {'Descriptions': response_text}
                all_tables_descriptions.append(response_text)
        
        json_filename = images_output_dir / f"{pdf_file.stem}-image-descriptions.json"
        with json_filename.open("w") as json_file:
            json.dump(image_descriptions, json_file, indent=4)
        json_filename_table = tables_output_dir / f"{pdf_file.stem}-table-descriptions.json"
        with json_filename_table.open("w") as json_file:
            json.dump(table_descriptions, json_file, indent=4)
        
        # ---------------------------
        # Zip Extracted Files
        # ---------------------------
        images_dir = os.path.join(base_output_dir, 'images')
        images_paths = [os.path.join(images_dir, x)
                        for x in os.listdir(images_dir) if x.endswith('png') and 'table' not in x]
        md_files = [os.path.join(images_dir, x)
                    for x in os.listdir(images_dir) if x.endswith('md')]
        md_main = [x for x in md_files if 'with-image-refs' in x]
        if md_main:
            md_main = md_main[0]
        else:
            md_main = None

        if md_main is not None:
            markdown_content = Path(md_main).read_text(encoding='utf-8')
        else:
            markdown_content = ""
            
        # Load table descriptions from the JSON file
        table_descriptions_file = tables_output_dir / f"{pdf_file.stem}-table-descriptions.json"
        if table_descriptions_file.exists():
            with table_descriptions_file.open("r", encoding="utf-8") as json_file:
                table_descriptions = json.load(json_file)
        else:
            table_descriptions = {}

        markdown_content_table = add_table_descriptions(markdown_content, table_descriptions)
        markdown_content_with_descriptions = add_figure_descriptions(markdown_content_table,image_descriptions)

        shutil.rmtree(base_output_dir)
       
        return markdown_content_with_descriptions
    
    def ingest(self):
        """
        Loops over all PDFs in the input directory, processes each one,
        and returns a nested dictionary with PDF names as keys.
        """
        results = {}

        if os.path.exists(os.path.join(Path(__file__).parent.parent.parent,'temp','temp.json')):
            os.makedirs(os.path.join(Path(__file__).parent.parent.parent, 'temp'), exist_ok=True)
            with open(os.path.join(Path(__file__).parent.parent.parent,'temp','temp.json'), 'r', encoding='utf-8') as temp_file:
                results = json.load(temp_file)
        pdf_files = list(self.input_path.glob("*.pdf"))
        if not pdf_files:
            self._log.warning(f"No PDF files found in {self.input_path}")
            return results

        for pdf_file in tqdm(pdf_files):
            if pdf_file.stem in results:
                continue
            self._log.info(f"Processing {pdf_file.name}")
            result = self._ingest_single_pdf(pdf_file)
            results[pdf_file.stem] = result
            
            temp_folder_path = Path(os.path.join(Path(__file__).parent.parent.parent, 'temp'))
            if not temp_folder_path.exists():
                temp_folder_path.mkdir(parents=True, exist_ok=True)
            with open(os.path.join(temp_folder_path, 'temp.json'), 'w', encoding='utf-8') as temp_file:
                json.dump(results, temp_file, indent=4)

        return results
    
class PDFSemanticLoader:
    """
    A loader that integrates PDF ingestion with semantic chunking.
    It uses PDFIngestor to ingest PDFs into combined text (markdown) and then processes
    that text with a semantic chunker (which returns rich chunks).
    """
    def __init__(self, chunker, input_path: Path, output_path: Path, table_describer: TableDescriptionGenerator):
        """
        Parameters
        ----------
        chunker : SemanticChunker
            An instance of a semantic chunker (e.g. PDFSemanticChunker) implementing get_chunks().
        input_path : Path
            Directory containing PDFs.
        output_path : Path
            Directory where temporary outputs are stored.
        table_describer : TableDescriptionGenerator
            Instance for generating table descriptions.
        """
        self.chunker = chunker
        if isinstance(input_path, str):
            input_path = Path(input_path)
        if isinstance(output_path, str):
            output_path = Path(output_path)
        self.input_path = input_path
        self.output_path = output_path
        self.table_describer = table_describer
        self.ingestor = PDFIngestor(input_path, output_path, table_describer)
        self._log = logging.getLogger(__name__)
    
    def load(self):
        """
        Ingest PDFs and yield rich semantic chunks.
        """
        # Ingest PDFs. The ingest() method returns a dict keyed by PDF stem, with combined markdown text.
        results = self.ingestor.ingest()

        for pdf_name, combined_content in results.items():
            data = {
                "content": combined_content,
                "source": pdf_name,
                "page": "Full Document"
            }
            # Use the semantic chunker's rich chunk interface.
            for chunk in self.chunker.get_chunks(data):
                yield chunk