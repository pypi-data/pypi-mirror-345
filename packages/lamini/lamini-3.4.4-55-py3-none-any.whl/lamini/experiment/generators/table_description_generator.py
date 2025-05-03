from lamini.experiment.generators import BaseGenerator


class TableDescriptionGenerator(BaseGenerator):
    """
    TableDescriptionGenerator extends the functionality of BaseGenerator to create a detailed description
    of a table from its dataframe representation. The generation is handled entirely by the base generator's
    GPT logic, ensuring consistency across different generator types.
    """

    def __init__(
        self,
        model,
        client=None,
        name=None,
        role=None,
        instruction=None,
        output_type=None,
        **kwargs,
    ):
        """
        Initializes the TableDescriptionGenerator with specific model parameters, instructions,
        and the expected input/output structures.

        :param model: The model used for generating table descriptions.
        :param client: Optional client instance.
        :param name: Optional name of the generator.
        :param role: Describes the role of the table description generator.
        :param instruction: Custom instructions (if provided).
        :param output_type: Expected output structure.
        :param kwargs: Additional keyword arguments.
        """
        instruction = instruction or (
            "You are given the content of a dataframe in CSV or tabular format below. "
            "Your task is to analyze this data and provide a comprehensive description of what the table represents. "
            "Include details about the columns, their data types, value ranges if applicable, and what information "
            "the table is conveying. This description will be used for information retrieval, so focus "
            "on capturing the essence and key characteristics of the dataset. "
            "Start your description with 'This table...' and be thorough."
            "\n\nDataframe content:\n{dataframe}"
        )

        output_type = output_type or {"table_description": "string"}

        super().__init__(
            name=name or "TableDescriptionGenerator",
            instruction=instruction,
            client=client,
            model=model,
            role=role
            or "You are an expert at analyzing and describing tabular data structures.",
            output_type=output_type,
            **kwargs,
        )

        # Store input types
        self.input = {"dataframe": "str"}

    def preprocess(self, prompt_obj):
        """
        Prepares the input data by checking if the dataframe content is actually provided.

        Args:
            prompt_obj (PromptObject): Contains the input dataframe.

        Returns:
            PromptObject: Preprocessed prompt object.
        """
        # Check if the dataframe input is just a filename or actual content
        dataframe = prompt_obj.data.get("dataframe", "")

        # If it's just a filename or very short string, try to add a warning
        if len(dataframe.strip().split("\n")) <= 1 and len(dataframe) < 100:
            prompt_obj.prompt += (
                "\n\nWARNING: The provided input appears to be a filename or insufficient data. "
                "Please provide the actual contents of the dataframe for a proper description. "
                "If this is indeed the complete data, please describe it as best as possible."
            )

        return prompt_obj

    def postprocess(self, prompt_obj):
        """
        Processes the model response to ensure the table description is formatted consistently.

        Args:
            prompt_obj (PromptObject): Contains the model response with a 'table_description' field.

        Returns:
            PromptObject: Updated prompt object with a cleaned 'table_description'.
        """
        if not prompt_obj.response:
            print("Warning: Empty response from model for the provided dataframe.")
            return prompt_obj

        try:
            description = prompt_obj.response.get("table_description", "").strip()

            # Check if the description is just returning the filename or is very short
            dataframe = prompt_obj.data.get("dataframe", "")
            if description == dataframe or len(description) < 20:
                description = (
                    "Unable to generate a proper description because the input appears to be just a filename "
                    "or insufficient data. Please provide the actual contents of the dataframe for analysis."
                )

            prompt_obj.response = {"table_description": description}
            return prompt_obj

        except Exception as e:
            print(f"Error during postprocessing: {str(e)}")
            print(f"Dataframe: {prompt_obj.data.get('dataframe', 'Unknown')}")
            print(f"Model response: {prompt_obj.response}")
            prompt_obj.response = {
                "table_description": "Error in processing table description."
            }
            return prompt_obj
