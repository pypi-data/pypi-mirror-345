import sys
import os
import logging
from typing import List

import pandas as pd
from lamini.index.lamini_index import LaminiIndex

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

def build_index(
    records: pd.DataFrame,
    concat_cols: List[str],
    index_path: str = "faiss_indices/model_index",
) -> None:
    """Construct a faiss vector index

    Parameters
    ----------
    records: pd.DataFrame
        Q/A pairs to be stored in the index

    concat_cols: List[str]
        Columns to concatenate within the records dataframe

    index_path: str = "faiss_indices/model_index"
        Location to store the index

    Returns
    -------
    None
    """

    if not os.path.isdir(index_path):
        os.makedirs(index_path)
    index_chunks = []
    for _, record in records.iterrows():
        text = ""
        for col in concat_cols:
            text += f"\n{col}:\n{record[col]}\n"
        index_chunks.append([text])

    llm_index = LaminiIndex.build_index(index_chunks)
    llm_index.save_index(index_path)
