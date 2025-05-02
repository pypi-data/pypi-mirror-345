import json
from lamini.experiment.generators.base_generator import BaseGenerator
from typing import Optional, Dict
import os


class GlossaryGenerator(BaseGenerator):
    """
    A generator class for creating glossaries from database schemas and queries.

    Generates a comprehensive glossary of terms and abbreviations found in
    database schemas and SQL queries, with explanations of their meanings.
    """

    def __init__(
        self,
        model=None,
        client=None,
        name=None,
        role=None,
        instruction=None,
        output_type=None,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        **kwargs,
    ):
        """
        Initializes the GlossaryGenerator with the provided parameters.

        Args:
            model (str): The model to be used.
            client: The client used for the language model.
            name (str): The name of the generator.
            role (str): The role description of the generator.
            instruction (str): Instruction for generating glossary.
            output_type (dict): Expected output type.
            api_key (str): API key for authentication.
            api_url (str): API endpoint URL.
            **kwargs: Additional keyword arguments.
        """
        # Default instruction for generating a glossary
        instruction = (
            instruction
            or """
        Task: Given the following database schema and a list of questions and SQL pairs, and user provided glossary,
        generate a new glossary of terms and abbreviations that appear in the schema and queries.
        
        Input Format:
            Schema: {schema}
            Queries: {queries}
            Original Glossary: {input_glossary}

        Guidelines for Generating Glossary:
            1. Identify all technical terms, abbreviations, and domain-specific language in the schema and queries
            2. Provide clear, concise explanations for each term
            3. Include terms from table names, column names, and SQL functions
            4. Maintain any entries from the original glossary and add new ones
            5. Ensure explanations are accurate and contextually appropriate

        Please ONLY provide updated glossary in JSON format with a key 'glossary' that maps to a list of dictionaries,
        where each dictionary has 'input' and 'output' keys. Do not have any markdown formatting for output JSON.
        """
        )

        # Define the expected output structure
        output_type = output_type or {"glossary": "array"}

        # Define the expected input structure
        self.input = {"schema": "str", "queries": "str", "input_glossary": "str"}

        # Initialize the base generator with provided parameters
        super().__init__(
            client=client,
            model=model,
            name=name or "GlossaryGenerator",
            role=role
            or "You are an expert at generating glossaries from schemas and queries.",
            instruction=instruction,
            output_type=output_type,
            api_key=api_key,
            api_url=api_url,
            **kwargs,
        )

    def preprocess(self, prompt_obj):
        """
        Preprocesses the prompt object before sending to the model.

        Args:
            prompt_obj: The prompt object to preprocess.

        Returns:
            The preprocessed prompt object.
        """
        # Initialize empty glossary if not present
        if "input_glossary" not in prompt_obj.data:
            prompt_obj.data["input_glossary"] = ""
        return prompt_obj

    def postprocess(self, prompt_obj):
        """
        Processes the response from the language model.

        Args:
            prompt_obj: The prompt object containing the response.

        Returns:
            The prompt object with a processed response.
        """
        if not prompt_obj.response:
            self.logger.warning("Empty response from model for schema input.")
            prompt_obj.response = {"glossary": []}
            return prompt_obj

        generated_glossary = []

        # Handle string responses (possibly JSON strings)
        if isinstance(prompt_obj.response, str):
            response_text = prompt_obj.response.strip()

            # Remove markdown formatting if present
            if response_text.startswith("```"):
                lines = response_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                response_text = "\n".join(lines)

            try:
                parsed = json.loads(response_text)
                if isinstance(parsed, dict) and "glossary" in parsed:
                    generated_glossary = parsed["glossary"]
                elif isinstance(parsed, list):
                    generated_glossary = parsed
                else:
                    generated_glossary = []
            except json.JSONDecodeError as e:
                self.logger.error(f"Error decoding generated glossary: {e}")
                self.logger.error(f"Response text: {response_text}")
                generated_glossary = []

        # Handle dict responses
        elif (
            isinstance(prompt_obj.response, dict) and "glossary" in prompt_obj.response
        ):
            generated_glossary = prompt_obj.response["glossary"]

        # Handle list responses
        elif isinstance(prompt_obj.response, list):
            generated_glossary = prompt_obj.response

        # Handle all other cases
        else:
            generated_glossary = []

        # Format the glossary entries
        formatted_generated = []
        for entry in generated_glossary:
            inp = entry.get("input", "")
            out = entry.get("output", "")

            # Handle multi-line entries
            if "\n" in inp or "\n" in out:
                inputs = [i.strip() for i in inp.split("\n") if i.strip()]
                outputs = [o.strip() for o in out.split("\n") if o.strip()]
                for i, o in zip(inputs, outputs):
                    formatted_generated.append({"input": i, "output": o})
            else:
                formatted_generated.append(
                    {"input": inp.strip(), "output": out.strip()}
                )

        # Process the existing glossary
        existing_glossary = prompt_obj.data.get("input_glossary", [])
        if isinstance(existing_glossary, str):
            existing_glossary = existing_glossary.strip()
            if existing_glossary.startswith("["):
                try:
                    existing_glossary = json.loads(existing_glossary)
                except Exception as e:
                    self.logger.error(
                        f"Error parsing existing glossary as JSON array: {e}"
                    )
                    existing_glossary = []
            else:
                items = []
                for line in existing_glossary.splitlines():
                    line = line.strip()
                    if line:
                        try:
                            item = json.loads(line)
                            items.append(item)
                        except Exception as e:
                            self.logger.error(
                                f"Error parsing line in existing glossary: {e}"
                            )
                existing_glossary = items
        elif not isinstance(existing_glossary, list):
            existing_glossary = []

        # Combine existing and new glossary entries
        new_glossary = existing_glossary + formatted_generated
        prompt_obj.response = {"glossary": new_glossary}
        return prompt_obj
