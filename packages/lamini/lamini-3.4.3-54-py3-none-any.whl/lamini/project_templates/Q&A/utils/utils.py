from lamini.generation.base_prompt_object import PromptObject
from lamini.experiment.base_experiment_object import ExperimentObject
import duckdb
import pandas as pd
from pathlib import Path
from lamini import Lamini
import os 
from openai import OpenAI
import yaml
import re
import hashlib
import shutil
from lamini.experiment.base_experiment_object import ExperimentObject
import duckdb
import pandas as pd
from models.analysis.analysis import ResultsAnalyzer
from pathlib import Path
from lamini import Lamini
import copy
from openai import OpenAI
import yaml
import hashlib
from copy import deepcopy
import numpy as np
from typing import List, Union, Dict
from openai import OpenAI

from fuzzywuzzy import fuzz as fuzz_wuzzy
from rapidfuzz import fuzz as fuzz_rapid
import jaro 
import json
from sklearn.decomposition import PCA
import umap
from sklearn.manifold import TSNE
import torch
from transformers import AutoTokenizer, AutoModel

def reduce_dimensionality(x: np.ndarray, method: str = "pca", dim: int = 2) -> np.ndarray:
    """
    Reduces the dimensionality of the embeddings using the specified method.
    Options for `method`: 'pca', 'umap', or 'tsne'. Target dimension must be 2 or 3.
    """
    if dim not in (2, 3):
        raise ValueError("The target dimension 'dim' must be either 2 or 3.")

    method = method.lower()

    if method == "pca":
        reducer = PCA(n_components=dim)
    elif method == "umap":
        reducer = umap.UMAP(n_components=dim)
    elif method == "tsne":
        reducer = TSNE(n_components=dim)
    else:
        raise ValueError("Method must be either 'pca', 'umap', or 'tsne'.")

    x_reduced = reducer.fit_transform(x)
    return x_reduced

def similarity_check(str1: str, str2: str, method: str) -> float:
    """
    Computes the similarity score between two strings using different fuzzy matching methods.
    Parameters:
    str1 (str): First string to compare.
    str2 (str): Second string to compare.
    method (str): Method of fuzzy matching. Options:
            - 'fuzzywuzzy': Uses fuzzywuzzy's ratio() for similarity score.
            - 'rapidfuzz': Uses rapidfuzz's ratio() for similarity score.
            - 'jarowinkler': Uses Jaro-Winkler metric for similarity score.
            - 'all': Averages the scores from 'fuzzywuzzy', 'rapidfuzz', and 'jarowinkler'.
    Returns:
    float: Similarity score (float between 0 and 100).
    """
    if method == 'fuzzywuzzy':
        score = fuzz_wuzzy.ratio(str1, str2)  # Calculate similarity using fuzzywuzzy
    elif method == 'rapidfuzz':
        score = fuzz_rapid.ratio(str1, str2)  # Calculate similarity using rapidfuzz
    elif method == 'jarowinkler':
        score = 100 * jaro.jaro_winkler_metric(str1, str2)  # Calculate similarity using Jaro-Winkler
    elif method == 'all':
        # Calculate average similarity using all methods
        score = np.mean([
            fuzz_wuzzy.ratio(str1, str2),
            fuzz_rapid.ratio(str1, str2),
            100 * jaro.jaro_winkler_metric(str1, str2)
        ])
    else:
        raise ValueError("Invalid method! Choose from 'fuzzywuzzy', 'rapidfuzz', 'jarowinkler', or 'all'.")

    return score  # Return the calculated similarity score

from typing import List, Dict
import numpy as np

def combine_relevant_chunks(
    rich_chunks: List[Dict],
    api_key: str,
    api_base_url: str,
    model: str,
    batch_size: int = 32,
    similarity_threshold: float = 0.8,
) -> List[Dict]:
    """
    Group and merge rich_chunks whose embeddings have cosine similarity >= threshold.
    Returns a new list of chunks (merged where relevant).
    """
    # 1) Embed all chunks
    texts = [chunk["chunk_text"] for chunk in rich_chunks]
    embeddings = get_text_embeddings(texts, api_key, api_base_url, model, batch_size)
    embs = np.vstack(embeddings)  # shape (n_chunks, dim)

    # 2) Compute cosine-similarity matrix
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    sim_matrix = (embs @ embs.T) / (norms * norms.T + 1e-12)

    # 3) Union-Find to cluster indices with sim >= threshold
    n = len(rich_chunks)
    parent = list(range(n))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    def union(i, j):
        pi, pj = find(i), find(j)
        if pi != pj:
            parent[pj] = pi

    for i in range(n):
        for j in range(i+1, n):
            if sim_matrix[i, j] >= similarity_threshold:
                union(i, j)

    # 4) Collect clusters and build merged chunks
    clusters: Dict[int, List[int]] = {}
    for i in range(n):
        root = find(i)
        clusters.setdefault(root, []).append(i)

    merged_chunks: List[Dict] = []
    for idxs in clusters.values():
        if len(idxs) == 1:
            # no merge needed
            merged_chunks.append(rich_chunks[idxs[0]].copy())
        else:
            # build one combined chunk
            combined = {
                "chunk_text": "\n".join(rich_chunks[i]["chunk_text"] for i in idxs),
                "chunk_start_pos": min(rich_chunks[i]["chunk_start_pos"] for i in idxs),
                "chunk_end_pos":   max(rich_chunks[i]["chunk_end_pos"]   for i in idxs),
                "page": sorted({rich_chunks[i]["page"] for i in idxs}),
                "source": sorted({rich_chunks[i]["source"] for i in idxs}),
                "chunk_id": "_".join(rich_chunks[i]["chunk_id"] for i in idxs),
                "num_sentences": sum(rich_chunks[i]["num_sentences"] for i in idxs),
            }
            merged_chunks.append(combined)

    return merged_chunks

def get_text_embeddings(
    texts: List[str],
    api_key: str,
    api_base_url: str,
    model: str,
    batch_size: int = 512,
) -> List[List[float]]:
    """
    Convert a list of texts into embeddings.

    Args:
        texts: List of strings to embed.
        api_key: Your OpenAI API key.
        api_base_url: Base URL for the OpenAI API.
        model: The embedding model name (e.g. "text-embedding-3-small").
        batch_size: Number of texts to send in each batch.

    Returns:
        A list of embedding vectors (one per input text).
    """
    client = OpenAI(api_key=api_key, base_url=api_base_url)
    all_embeddings: List[List[float]] = []

    # Process in batches to avoid request-size limits
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(
            model=model,
            input=batch,
            encoding_format="float"
        )
        # Each resp.data item has an `.embedding` field
        for item in resp.data:
            all_embeddings.append(item.embedding)

    return all_embeddings

def filter_relevant_chunks(
    topics: List[str],
    chunks: List[Dict],
    api_key: str,
    api_base_url: str,
    model: str,
    threshold: float = 0.8,
    batch_size: int = 512,
) -> List[Dict]:
    """
    Return only those chunks whose text is semantically similar to at least one topic.

    Args:
        topics: List of topic strings.
        chunks: List of dicts, each having at least a 'chunk_text' key.
        api_key: OpenAI API key.
        api_base_url: Base URL for OpenAI API.
        model: Embedding model name.
        threshold: Cosine similarity threshold (0–1) for relevance.
        batch_size: How many texts to embed per API call.

    Returns:
        A filtered list of chunk dicts deemed relevant.
    """
    # 1) Embed your topics
    topic_embeddings = get_text_embeddings(
        texts=topics,
        api_key=api_key,
        api_base_url=api_base_url,
        model=model,
        batch_size=batch_size
    )

    # 2) Extract and embed all chunk texts
    chunk_texts = [c["chunk_text"] for c in chunks]
    chunk_embeddings = get_text_embeddings(
        texts=chunk_texts,
        api_key=api_key,
        api_base_url=api_base_url,
        model=model,
        batch_size=batch_size
    )
    
    # 3) Compute cosine similarities and filter
    relevant = []
    for chunk, emb in zip(chunks, chunk_embeddings):
        # cosine similarity vs each topic
        sims = [
            np.dot(emb, top_emb) / (np.linalg.norm(emb) * np.linalg.norm(top_emb))
            for top_emb in topic_embeddings
        ]
        if max(sims) >= threshold:
            relevant.append(chunk)
    return relevant

def generate_question_chunks(objs: List, chunk_size: int) -> List:
    """
    Processes a list of PromptObject instances and splits the 'chunk_text' inside
    the data dict into non-overlapping chunks that end at sentence boundaries.
    A new key 'question_chunk' is added to each new object.

    Args:
        objs (List): A list of PromptObject instances.
        chunk_size (int): Maximum size of each split chunk.

    Returns:
        List: A flat list of new PromptObject instances with updated 'question_chunk'.
    """
    import re
    
    results = []
    for obj in objs:
        # Get the original text from the 'chunk_text' field.
        text = obj.data.get("chunk_text", "")
        
        # Define sentence endings pattern
        sentence_end_pattern = r'[.!?](\s|$)'
        
        # Start position in the text
        current_pos = 0
        
        while current_pos < len(text):
            # Determine potential end position based on chunk_size
            potential_end = min(current_pos + chunk_size, len(text))
            
            # If we're at the end of the text, use what remains
            if potential_end >= len(text):
                end_pos = len(text)
            else:
                # Get the current chunk
                current_chunk = text[current_pos:potential_end]
                
                # Find all sentence endings within the chunk
                sentence_ends = [m.end() for m in re.finditer(sentence_end_pattern, current_chunk)]
                
                if sentence_ends:
                    # Adjust the end position to the last complete sentence in the chunk
                    end_pos = current_pos + sentence_ends[-1]
                else:
                    # If no sentence end is found within the chunk, look ahead for the next one
                    next_sentence_end = re.search(sentence_end_pattern, text[potential_end:])
                    if next_sentence_end:
                        end_pos = potential_end + next_sentence_end.end()
                    else:
                        # If no sentence end is found ahead, use the entire remaining text
                        end_pos = len(text)
            
            # Extract the chunk
            chunk = text[current_pos:end_pos]
            
            if chunk.strip():
                new_obj = PromptObject(prompt=obj.prompt, response=obj.response, data=obj.data.copy())
                new_obj.data['question_chunk'] = chunk
                results.append(new_obj)
            
            # Move the current position to the end of the current chunk
            # This ensures no overlap between chunks
            current_pos = end_pos
    
    return results

def experiment_to_csv(experiment_name):
    analyzer = ResultsAnalyzer(experiment_name)
    qa_pairs = analyzer.get_qa_pairs_with_validity(limit=20)  # get first 20 pairs
    all_pairs = analyzer.get_qa_pairs_with_validity()
    
    print("\nExperiment Summary:")
    print("=" * 50)
    print(f"Experiment Name: {experiment_name}")

    # Optional: Show a sample of valid Q&A pairs
    print("\nSample of valid Q&A pairs:")
    print("-" * 50)
    valid_pairs = analyzer.get_valid_qa_pairs(limit=3)
    print(valid_pairs)

    # Export all pairs to CSV
    csv_path = analyzer.export_to_csv(all_pairs, filename_prefix="all_qa_pairs")
    print(f"\nFull results exported to: {csv_path}")
    
def generate_prompts_class_from_yml(yml_path: str, output_path: str = "prompts.py"):
    # Load prompts.yml
    
    with open(yml_path, "r", encoding="utf-8") as f:
        prompt_yml = yaml.safe_load(f)
    
    prompts = prompt_yml.get("prompts", {})
    
    # Start building the class as a string
    class_code = "class Prompts:\n"

    for key in prompts:
        prompt_name = key.upper()
        template = prompts[key].get("template", "").strip()
        
        # Replace {{var}} with {var} to make Python f-string compatible
        formatted_template = template.replace("{{", "{").replace("}}", "}")
        
        # Indent each line by 4 spaces for class formatting
        indented_template = "\n".join(f"    {line}" for line in formatted_template.splitlines())
        
        class_code += f"\n    {prompt_name} = \"\"\"\n{indented_template}\n    \"\"\"\n"

    # Save to .py file
    output_file = Path(output_path)
    output_file.write_text(class_code.strip() + "\n", encoding="utf-8")
    print(f"`{output_file}` generated successfully from `{yml_path}`.")
    
def create_prompts_yml(focus_area: str, output_path: str = "ymls/prompts.yml"):
    content = """prompts:
  question:
    description: Prompt for generating high-quality, context-grounded questions from document chunks
    template: |
      Follow these steps closely:

      1. Consider the document collection: {{product}}
      2. Review the section title: {{title}}
      3. Read the overview of guidelines and procedures: {{description}}
      4. Keep the following keywords in mind: {{keywords}}
      5. Inspect the excerpt below:
         Page: {{page}}
         Source: {{source}}
         ---
         {{chunk_text}}
         ---
      6. Use any additional context as follows:
         Focus the question on the specific point highlighted by {{question_chunk}}, while leveraging the full excerpt above for context.

      7. Craft one clear, professionally phrased question that:
      - Can be answered exclusively using the excerpt above
      - Focuses on accounting definitions, recognition criteria, measurement methods, timing, or similar concepts
      - Requires a multi-sentence answer (avoid yes/no or single-word questions)

      Output only the question text, with no numbering or additional commentary.

  answer:
    description: Prompt for generating answers to given questions from document chunks
    template: |
      Follow these steps closely:

      1. Context:
         Document: {{product}}
         Title: {{title}}
         Description: {{description}}
      2. Excerpt to ground your answer:
         Page: {{page}}  Source: {{source}}
         ---
         {{chunk_text}}
         ---
      3. Question to answer:
         {{question}}

      Now provide a clear, concise answer in one to three paragraphs consider the full context provided above. Every statement must reference the excerpt with bracketed citations ([1], [2], etc.) corresponding to specific sentences or phrases. Paraphrase relevant text; do not quote large blocks. Do not include information outside the excerpt.

      Output only the answer text.

  validator:
    description: Prompt for validating a question and its answer based on document content
    template: |
      Follow these steps:

      1. Document: {{product}}
         Title: {{title}}
         Description: {{description}}
      2. Excerpt (Page {{page}}, Source {{source}}):
         {{chunk_text}}
      3. Question: {{question}}
      4. Answer: {{answer}}

      Validate whether the answer:
      - Directly answers the question
      - Is fully supported by the excerpt and correctly cited
      - Is complete and multi-sentence
      - Uses bracketed citations ([n])

      Respond with 1 if all criteria are met; otherwise 0. Output only the digit.
"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content, encoding="utf-8")
    print(f"`{output_file}` created successfully with focus area: '{focus_area}'")
    
def read_roles_yml_to_dict(path="ymls/roles.yml"):
    """
    Reads a roles.yml file and returns a dictionary with role names and their descriptions.

    Parameters
    ----------
    path : str, optional
        Path to the roles.yml file.

    Returns
    -------
    dict
        Dictionary with role names as keys and their role descriptions as values.
    """
    with open(path, "r") as f:
        roles_yaml = yaml.safe_load(f)

    roles_dict = {}
    for role, role_info in roles_yaml.get("roles", {}).items():
        roles_dict[role] = role_info.get("reference", "")

    return roles_dict

def write_roles_yml(roles_dict, output_path="ymls/roles.yml", topic="aia insurance brochures"):
    """
    Create a roles.yml file from a dictionary of role descriptions.

    Parameters
    ----------
    roles_dict : dict
        Dictionary containing role names as keys and descriptions as values.
    output_path : str, optional
        Path where the roles.yml will be saved.
    topic : str, optional
        The topic associated with the roles.
    """
    roles_yaml = {
        "topic": topic,
        "roles": {}
    }

    for role, description in roles_dict.items():
        roles_yaml["roles"][role] = {
            "reference": description,
            "description_task": description.split("Your", 1)[-1].strip().capitalize() if "Your" in description else description
        }

    with open(output_path, "w") as f:
        yaml.dump(roles_yaml, f, sort_keys=False, default_flow_style=False, width=1000)

    print(f"roles.yml written to: {output_path}")      

def generate_document_metadata(topic: str, api_key: str) -> dict:
    # Initialize the client with your API key and base URL
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.lamini.ai/inf"
    )

    # Generate Product Name
    product_prompt = (
        f"Generate a short product name for a research paper on the topic of {topic}. "
        "Make sure the name sounds professional and suitable for academic publishing."
    )
    product_output = client.completions.create(
        model="gpt-4o",
        prompt=product_prompt,
        max_tokens=1000
    )
    product = product_output.choices[0].text.strip()

    # Generate Keywords (as a comma-separated list; we then convert to a list)
    keywords_prompt = (
        f"Generate a comma-separated list of 5 to 7 concise keywords relevant to the topic '{topic}' for a research paper."
    )
    keywords_output = client.completions.create(
        model="gpt-4o",
        prompt=keywords_prompt,
        max_tokens=500
    )
    keywords_raw = keywords_output.choices[0].text.strip()
    keywords = [kw.strip() for kw in keywords_raw.split(",") if kw.strip()]

    # Generate Title
    title_prompt = (
        f"Generate a concise and engaging title for a research paper on the topic of {topic}. "
        "Ensure the title reflects the core essence of the research."
    )
    title_output = client.completions.create(
        model="gpt-4o",
        prompt=title_prompt,
        max_tokens=500
    )
    title = title_output.choices[0].text.strip()

    # Generate Description (or abstract)
    description_prompt = (
        f"Generate a detailed and well-organized abstract for a research paper on the topic of {topic}. "
        "Outline the research objectives, methods, and potential findings in an academic tone."
    )
    description_output = client.completions.create(
        model="gpt-4o",
        prompt=description_prompt,
        max_tokens=1500
    )
    description = description_output.choices[0].text.strip()

    # Construct and return the metadata dictionary
    metadata = {
        "document_metadata": {
            "product": product,
            "keywords": keywords,
            "title": title,
            "description": description
        }
    }
    
    return metadata

def generate_role_descriptions(topic: str, api_key: str) -> dict:
    # Initialize the client with your API key and base URL
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.lamini.ai/inf"
    )
    
    roles = {}
    
    # Question Generator Role
    question_reference = (
        "You are an accounting expert at Cisco specializing in best practices for financial reporting. "
        "Your task is to generate precise questions based solely on the provided Cisco accounting documentation."
    )
    question_prompt = (
        f"Generate me a short role description for an agent who is an expert in the topic of {topic} with a task of question generation based on the provided context only. "
        f"Make sure to only provide the role description and no other information.\n"
        f"You can use this as a reference as an example for the topic 'accounting at Cisco': {question_reference}"
    )
    question_output = client.completions.create(
        model="gpt-4o",
        prompt=question_prompt,
        max_tokens=10000
    )
    roles["question_generator"] = question_output.choices[0].text.strip()
    
    # Answer Generator Role
    answer_reference = (
        "You are an accounting expert at Cisco with deep expertise in financial practices. "
        "Your role is to provide detailed and accurate answers strictly derived from the provided Cisco accounting text."
    )
    answer_prompt = (
        f"Generate me a short role description for an agent who is an expert in the topic of {topic} with a task of answer generation based on the provided context only. "
        f"Make sure to only provide the role description and no other information.\n"
        f"You can use this as a reference as an example for the topic 'accounting at Cisco': {answer_reference}"
    )
    answer_output = client.completions.create(
        model="gpt-4o",
        prompt=answer_prompt,
        max_tokens=10000
    )
    roles["answer_generator"] = answer_output.choices[0].text.strip()
    
    # Fact Validator Role
    validator_reference = (
        "You are a veteran accounting professional at Cisco with over 20 years of experience. "
        "You validate that all generated documentation strictly adheres to Cisco's accounting standards."
    )
    validator_prompt = (
        f"Generate me a short role description for an agent who is an expert in the topic of {topic} with a task of fact validation based on the provided context only. "
        f"Make sure to only provide the role description and no other information.\n"
        f"You can use this as a reference as an example for the topic 'accounting at Cisco': {validator_reference}"
    )
    validator_output = client.completions.create(
        model="gpt-4o",
        prompt=validator_prompt,
        max_tokens=10000
    )
    roles["validator"] = validator_output.choices[0].text.strip()
    
    # Guardrails Role
    guardrails_reference = (
        "You are the final line of defense for Cisco’s accounting documentation. "
        "Ensure the documentation is flawless and compliant with Cisco’s standards, as any mistakes could lead to major issues."
    )
    guardrails_prompt = (
        f"Generate me a short role description for an agent who is an expert in the topic of {topic} with a task of guardrails enforcement based on the provided context only. "
        f"Make sure to only provide the role description and no other information.\n"
        f"You can use this as a reference as an example for the topic 'accounting at Cisco': {guardrails_reference}"
    )
    guardrails_output = client.completions.create(
        model="gpt-4o",
        prompt=guardrails_prompt,
        max_tokens=10000
    )
    roles["guardrails"] = guardrails_output.choices[0].text.strip()
    
    return roles

def retreive_sample(json_files: dict, sample_size: int, job_id: int):
    start = sample_size * job_id
    end = sample_size * (job_id + 1)
    if end >= (len(json_files) - 50):
        end = len(json_files)
    sampled_json_files = list(json_files.keys())[start:end]
    return {file_: json_files[file_] for file_ in sampled_json_files}

def build_exp_obj_from_dataframe(
    df,  
    extract_columns,
    additional_data,
):
    """Build prompts from dataframe with optional additional data.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the chunks data
    extract_columns : List[str]
        Columns to extract from the dataframe
    additional_data : Dict[str, Any], optional
        Additional key-value pairs to add to each prompt's data
        
    Returns
    -------
    List[PromptObject]
        List of prompt objects with combined data
    """
    prompts = []
    
    for _, row in df.iterrows():
        # Start with the extracted columns
        data = {key_: row[key_] for key_ in extract_columns}
        
        # Add any additional data
        if additional_data:
            data.update(additional_data)
            
        prompts.append(ExperimentObject(
            experiment_step=None,#prompt = "",
            data = data
        ))
    
    print(prompts[0].data)
    return prompts

def build_prompts_from_dataframe(
    df,  
    extract_columns,
    additional_data,
):
    """Build prompts from dataframe with optional additional data.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the chunks data
    extract_columns : List[str]
        Columns to extract from the dataframe
    additional_data : Dict[str, Any], optional
        Additional key-value pairs to add to each prompt's data
        
    Returns
    -------
    List[PromptObject]
        List of prompt objects with combined data
    """

    prompts = []
    
    for _, row in df.iterrows():
        # Start with the extracted columns
        data = {key_: row[key_] for key_ in extract_columns}
        
        # Add any additional data
        if additional_data:
            data.update(additional_data)
            
        prompts.append(PromptObject(
            prompt = "",
            data = data
        ))
    
    print(prompts[0].data)
    return prompts

def save_chunks(rich_chunks, experiment_name, base_dir="./local-db"):
    """
    Save rich chunks to a single parquet file using DuckDB, adding experiment_name as a column.
    Skips chunks with exact matching chunk_ids or with identical content.
    
    Parameters
    ----------
    rich_chunks : List[Dict]
        List of dictionaries containing chunk data. Each dictionary must contain a 'chunk_id'
        and a 'content' key.
    experiment_name : str
        Name of the experiment to be added as a column.
    base_dir : str, optional
        Base directory for the database, defaults to './local-db'.
        
    Returns
    -------
    str
        Path to the saved parquet file.
    """
    base_dir=os.path.join(Path(__file__).parent.parent,base_dir)
    # Convert rich_chunks to DataFrame and add experiment_name
    chunks_df = pd.DataFrame(rich_chunks)
    chunks_df['experiment_name'] = experiment_name

    # Compute a content hash for each chunk (using the 'content' field)
    if 'chunk_text' in chunks_df.columns:
        chunks_df['content_hash'] = chunks_df['chunk_text'].apply(
            lambda x: hashlib.sha256(x.encode('utf-8')).hexdigest()
        )
    else:
        # Fallback: hash the entire row if 'content' column is not available.
        chunks_df['content_hash'] = chunks_df.apply(
            lambda row: hashlib.sha256(row.to_json().encode('utf-8')).hexdigest(), axis=1
        )

    # Initialize DuckDB connection
    conn = duckdb.connect()

    # Create output directory if it doesn't exist
    output_dir = Path(base_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    parquet_path = output_dir / "chunks.parquet"

    if parquet_path.exists():
        # Read existing data and get duplicate identifiers
        existing_df = conn.execute(
            f"SELECT * FROM read_parquet('{parquet_path}')"
        ).df()
        existing_chunk_ids = set(existing_df['chunk_id'].values)
        existing_content_hashes = set(existing_df['content_hash'].values)
        
        # Identify new chunks: skip if either chunk_id or content_hash already exists
        new_chunks_mask = (~chunks_df['chunk_id'].isin(existing_chunk_ids)) & \
                        (~chunks_df['content_hash'].isin(existing_content_hashes))
        new_chunks_df = chunks_df[new_chunks_mask]
        if len(new_chunks_df) > 0:
            # Combine with existing data
            combined_df = pd.concat([existing_df, new_chunks_df], ignore_index=True)
            # Register the combined DataFrame with DuckDB and write back to parquet
            conn.register("combined_df", combined_df)
            conn.execute("CREATE OR REPLACE TABLE chunks AS SELECT * FROM combined_df")
            conn.execute(f"COPY chunks TO '{parquet_path}' (FORMAT PARQUET)")
            print(f"Added {len(new_chunks_df)} new chunks")
            print(f"Skipped {len(chunks_df) - len(new_chunks_df)} duplicate chunks")
        else:
            print("No new chunks to add - all chunk_ids or contents already exist in the database")
            combined_df = existing_df
    else:
        # No existing file, so write all chunks to a new parquet file
        conn.register("chunks_df", chunks_df)
        conn.execute("CREATE TABLE chunks AS SELECT * FROM chunks_df")
        conn.execute(f"COPY chunks TO '{parquet_path}' (FORMAT PARQUET)")
        new_chunks_df = chunks_df
        print(f"Created new database with {len(chunks_df)} chunks")
    
    # Verify the data
    total_chunks = conn.execute(
        f"SELECT COUNT(*) FROM read_parquet('{parquet_path}')"
    ).fetchone()[0]
    
    print(f"Chunks saved to {parquet_path}")
    print(f"Total chunks in database: {total_chunks}")
    
    return str(parquet_path)

def save_results(results_df, experiment_name, base_dir="./local-db"):
    """
    Save experiment results to a single parquet file using DuckDB, adding experiment_name as a column.
    
    Parameters
    ----------
    results_df : pandas.DataFrame
        DataFrame containing the experiment results
    experiment_name : str
        Name of the experiment to be added as a column
    base_dir : str, optional
        Base directory for the database, defaults to ./local-db
        
    Returns
    -------
    str
        Path to the saved parquet file
    """
    base_dir=os.path.join(Path(__file__).parent.parent,base_dir)
    # Add experiment name to results
    results_df['experiment_name'] = experiment_name
    
    # Initialize DuckDB connection
    conn = duckdb.connect()
    
    # Create output directory if it doesn't exist
    output_dir = Path(base_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    parquet_path = output_dir / "results.parquet"
    
    if parquet_path.exists():
        # Read existing data
        existing_df = conn.execute(f"SELECT * FROM read_parquet('{parquet_path}')").df()
        # Combine with new data
        combined_df = pd.concat([existing_df, results_df], ignore_index=True)
        # Write back to parquet
        conn.execute("CREATE TABLE results AS SELECT * FROM combined_df")
    else:
        # Create new parquet file
        conn.execute("CREATE TABLE results AS SELECT * FROM results_df")
    
    conn.execute(f"COPY results TO '{parquet_path}' (FORMAT PARQUET)")
    
    # Verify the data
    total_results = conn.execute(f"SELECT COUNT(*) FROM read_parquet('{parquet_path}')").fetchone()[0]
    new_results = len(results_df)
    
    print(f"Results saved to {parquet_path}")
    print(f"New results added: {new_results}")
    print(f"Total results in database: {total_results}")
    
    return str(parquet_path)

def clean_pycache():
    """
    Recursively deletes all __pycache__ directories in the current working directory
    and its subdirectories.
    """
    current_dir = os.getcwd()
    for root, dirs, files in os.walk(current_dir):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"Deleted: {pycache_path}")
            except Exception as e:
                print(f"Error deleting {pycache_path}: {str(e)}")

