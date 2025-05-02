from lamini.experiment.generators.base_generator import BaseGenerator
from lamini.experiment.base_experiment_object import ExperimentObject
from copy import deepcopy
import re

class MultiValueGenerator(BaseGenerator):
    """A generator that takes a single prompt and returns a list of outputs.

    Main change from the base generator is that it returns a list of ExperimentObjects 
    from the postprocess method. All other functionality is the same as the base generator.

    Parameters
    ----------
    model : object
        The model to use for the generator.
    client : object, optional
        The client to use for the generator.
    name : str, optional
        The name of the generator.
    role : str, optional
        The role of the generator.
    instruction : str, optional
        The instruction to use for the generator.
    output_type : dict, optional
        The output type of the generator.
    subkey_output_type : str, optional
        The subkey output type of the generator.
    postprocess_delimiter : str, optional
        The delimiter to use for the postprocess method. Default is ",".
    **kwargs
        Additional keyword arguments.
    """

    def __init__(
        self,
        model,
        client=None,
        name=None,
        role=None,
        instruction=None,
        output_type=None,
        subkey_output_type=None,
        postprocess_delimiter=",",
        **kwargs,
    ):
        name = name or "MultiValueGenerator"

        output_type = output_type or {"list": "str"}
        self.subkey_output_type = subkey_output_type
        self.postprocess_delimiter = postprocess_delimiter
        self.output_key = list(output_type.keys())[0]
        super().__init__(
            client=client,
            model=model,
            name=name,
            role=role,
            instruction=instruction,
            output_type=output_type,
            **kwargs,
        )

    def postprocess(self, result):
        """Process a string result into a list of ExperimentObjects.

        Takes a string result formatted as a dictionary with a list-like string value
        and converts it into multiple ExperimentObjects, each containing one value
        from the list.

        Parameters
        ----------
        result : ExperimentObject
            An ExperimentObject containing a response that should be a dictionary
            with a list-like string value (e.g., {"facts_list": "fact1, fact2, fact3"})

        Returns
        -------
        list of ExperimentObject
            A list of new ExperimentObjects, each containing one value from the
            original list in their data dictionary under the subkey_output_type key.
            Returns an empty list if the response is invalid.

        Notes
        -----
        The method:
        1. Removes square brackets from the list string
        2. Splits the string on the postprocess_delimiter
        3. Strips whitespace from each value
        4. Removes empty strings
        5. Creates new ExperimentObjects with individual values
        """
        # Turn the string result, formatted as example: {"facts_list": "fact1, fact2, fact3"}, into a list of objects

        if isinstance(result.response, dict):
            if self.output_key not in result.response:
                values = []
            else:
                list_object = result.response.get(self.output_key, None)
                list_object = list_object.replace("[", "")  # remove square brackets
                list_object = list_object.replace("]", "")
        

                objects = re.split(self.postprocess_delimiter, list_object)  # split using regex pattern
        
                list_object = [obj.strip() for obj in objects]  # remove whitespace
                list_object = [
                    obj for obj in objects if obj
                ]  # remove empty strings
        
                # Create a list of concept PromptObjects, each with a concept field
                values = []
                for obj in list_object:
                    # Deep copy the history stored in result prompt object to avoid shared references
                    new_prompt_obj = ExperimentObject(
                        prompt=deepcopy(result.prompt),
                        data=deepcopy(result.data),
                        response=deepcopy(result.response),
                    )
                    new_prompt_obj.data[self.subkey_output_type] = obj
                    values.append(new_prompt_obj)
        else:
            print(f"Response result is not a dictionary: {result.response}")
            values = []
    
        return values