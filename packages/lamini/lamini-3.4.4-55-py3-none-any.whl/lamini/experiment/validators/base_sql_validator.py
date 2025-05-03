# TODO: This change is added so that we can support GPT call part of BaseGenerator
#        Please note that when this is pushed into SDK we need to have some filtering for external users

from lamini.experiment.validators import BaseValidator
from lamini.experiment.generators import BaseSQLGenerator


class BaseSQLValidator(BaseSQLGenerator, BaseValidator):
    """Base class for SQL validation that combines generator and validator capabilities."""

    def __init__(
        self,
        model,
        client=None,
        db_type=None,
        db_params=None,
        name="BaseSQLValidator",
        instruction=None,
        output_type=None,
        is_valid_field="is_valid",
        **kwargs,
    ):
        # Store the is_valid_field value
        self._is_valid_field = is_valid_field

        # If output_type is None, create an empty dict
        if output_type is None:
            output_type = {}

        # Make a copy to avoid modifying the original
        modified_output_type = dict(output_type)

        # Ensure output_type includes the is_valid_field with bool type
        modified_output_type[self._is_valid_field] = "bool"

        # First initialize BaseSQLGenerator
        BaseSQLGenerator.__init__(
            self,
            model=model,
            client=client,
            schema=kwargs.get("schema", None),
            db_type=db_type,
            db_params=db_params,
            name=name,
            instruction=instruction,
            output_type=modified_output_type,
            is_valid_field=self._is_valid_field,
        )

        BaseValidator.__init__(
            self,
            name=name,
            instruction=instruction or "",
            client=client,
            output_type=modified_output_type,
            model=model,
            role=kwargs.get("role", ""),
            instruction_search_pattern=kwargs.get("instruction_search_pattern", r"\{(.*?)\}"),
            is_valid_field=self._is_valid_field,
        )

    def __call__(self, prompt_obj, debug=False):
        """Base validation method to be implemented by subclasses."""
        return BaseValidator.__call__(self, prompt_obj, debug)
