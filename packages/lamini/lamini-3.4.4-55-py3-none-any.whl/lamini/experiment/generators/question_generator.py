from lamini.experiment.generators.base_generator import BaseGenerator


class QuestionGenerator(BaseGenerator):
    """
    Takes a chunk of text and returns a question that is relevant to the text.
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
        name = name or "QuestionGenerator"
        role = (
            role
            or "You are a helpful assistant that takes a chunk of text and returns a question that is relevant to the text."
        )
        instruction = (
            instruction
            or """Given the text, return a question that is relevant to the text.
        Text:
        {chunk}"""
        )

        output_type = output_type or {"question": "str"}

        super().__init__(
            client=client,
            model=model,
            name=name,
            role=role,
            instruction=instruction,
            output_type=output_type,
            **kwargs,
        )