from lamini.experiment.generators.base_generator import BaseGenerator
import os
from pathlib import Path
import yaml
import re


class SubQuestionSQLGenerator(BaseGenerator):
    """Generates SQL for simpler sub-questions using original question context."""

    def __init__(
        self,
        model,
        client=None,
        name=None,
        role=None,
        instruction=None,
        output_type=None,
        syntax="sqlite",
        **kwargs,
    ):
        """
        Initialize the SubQuestionSQLGenerator with the specified parameters.

        Args:
            model: The model to use for generation.
            client: Optional; the client to use.
            name: Optional; the name of the generator.
            role: Optional; the role description of the generator.
            instruction: Optional; instruction set for the generator.
            output_type: Optional; the output type of the generator.
            syntax: A string indicating the SQL dialect; either "sqlite" or "snowflake".
            **kwargs: Additional keyword arguments.
        """

        base_instruction = """
        Task: Given the following schema, glossary, original question, original SQL query, and sub-question, write a complete and valid {syntax} query that answers the sub-question. Before providing the final query, perform a self-check loop to ensure the query adheres to the guidelines and is executable.

        Input Format:

        Schema: {schema}

        Glossary: {glossary}

        Original Question: {original_question}

        Original SQL: {original_sql}

        Sub Question: {question}

        Guidelines for the {syntax} Query:

            Schema References: Ensure that the query uses only columns and tables as defined in the provided schema. Cross-check all column names against the schema.

            Accurate Clause Usage: Include the relevant SQL clauses (e.g., SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY, JOIN, etc.) based on the sub-question.

            SQL Validity: The generated SQL query must be executable in a {syntax} environment. Follow proper {syntax} conventions and best practices.

            Use of Keywords: Use SQL keywords (e.g., SELECT, JOIN, WHERE, etc.) in uppercase for clarity.

            Specificity and Relevance: Ensure the query is specific to the sub-question without extraneous operations.

        Self-Check Loop:

            1. Query Completeness Check: Ensure all necessary clauses are present.
            2. Schema Reference Check: Validate that columns and tables exist in the schema.
            3. Syntax Check: Validate correct SQL syntax.
            4. Query Execution Check: Simulate running the query in a {syntax} environment.
            5. Refinement: Refine the query if issues are found.

            Final Output: Please provide ONLY the complete {syntax} query (after performing the self-check loop) without any explanation or markdown formatting.
            """

        # Use the provided instruction if available; otherwise, use our built instruction.
        instruction = instruction or base_instruction

        output_type = output_type or {"sql_query": "str"}

        super().__init__(
            client=client,
            model=model,
            name=name or "SubQuestionSQLGenerator",
            role=role
            or f"You are a SQL expert who writes precise {syntax.capitalize()} queries.",
            instruction=instruction,
            output_type=output_type,
            **kwargs,
        )
        self.syntax = syntax.lower()

    def postprocess(self, prompt_obj):
        """
        Process the SQL query response by ensuring proper statement termination.

        Args:
            prompt_obj: The object containing the response and data from the model.

        Returns:
            The modified prompt_obj with the generated SQL properly formatted.
        """
        if not prompt_obj.response or "sql_query" not in prompt_obj.response:
            return prompt_obj

        sql = prompt_obj.response["sql_query"].strip()
        if not sql.endswith(";"):
            sql += ";"
        prompt_obj.data["generated_sql"] = sql
        return prompt_obj
