class Prompts:

    QUESTION = """
    Follow these steps closely:
    
    1. Consider the document collection: {product}
    2. Review the section title: {title}
    3. Read the overview of guidelines and procedures: {description}
    4. Keep the following keywords in mind: {keywords}
    5. Inspect the excerpt below:
       Page: {page}
       Source: {source}
       ---
       {chunk_text}
       ---
    6. Use any additional context as follows:
       Focus the question on the specific point highlighted by {question_chunk}, while leveraging the full excerpt above for context.
    
    7. Craft one clear, professionally phrased question that:
    - Can be answered exclusively using the excerpt above
    - Focuses on accounting definitions, recognition criteria, measurement methods, timing, or similar concepts
    - Requires a multi-sentence answer (avoid yes/no or single-word questions)
    
    Output only the question text, with no numbering or additional commentary.
    """

    ANSWER = """
    Follow these steps closely:
    
    1. Context:
       Document: {product}
       Title: {title}
       Description: {description}
    2. Excerpt to ground your answer:
       Page: {page}  Source: {source}
       ---
       {chunk_text}
       ---
    3. Question to answer:
       {question}
    
    Now provide a clear, concise answer in one to three paragraphs consider the full context provided above. Every statement must reference the excerpt with bracketed citations ([1], [2], etc.) corresponding to specific sentences or phrases. Paraphrase relevant text; do not quote large blocks. Do not include information outside the excerpt.
    
    Output only the answer text.
    """

    VALIDATOR = """
    Follow these steps:
    
    1. Document: {product}
       Title: {title}
       Description: {description}
    2. Excerpt (Page {page}, Source {source}):
       {chunk_text}
    3. Question: {question}
    4. Answer: {answer}
    
    Validate whether the answer:
    - Directly answers the question
    - Is fully supported by the excerpt and correctly cited
    - Is complete and multi-sentence
    - Uses bracketed citations ([n])
    
    Respond with 1 if all criteria are met; otherwise 0. Output only the digit.
    """
