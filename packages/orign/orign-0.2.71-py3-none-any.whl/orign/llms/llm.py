import time
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
)

import requests
from chatmux import ChatRequest
from nebu import V1ResourceMetaRequest, V1ResourceReference
from pydantic import BaseModel, TypeAdapter

from orign.buffers.models import V1ReplayBufferData, V1Trainer
from orign.config import GlobalConfig
from orign.llms.models import (
    V1OnlineLLM,
    V1OnlineLLMRequest,
    V1OnlineLLMs,
    V1OnlineLLMStatus,
    V1UpdateOnlineLLMRequest,
)
from orign.trainings.models import V1TrainingStatus
from orign.trainings.training import Training

InputType = TypeVar("InputType", bound=BaseModel)
OutputType = TypeVar("OutputType", bound=BaseModel)
ExampleType = TypeVar("ExampleType", bound=BaseModel)


class OnlineLLM(Generic[InputType, OutputType, ExampleType]):
    """
    Online LLMs can both learn and act.
    """

    # Use ClassVar to indicate this is intended as a class-level attribute
    # The type hint still uses the TypeVar OutputType
    output_model: ClassVar[Type[OutputType]]  # type: ignore

    def __init_subclass__(cls, **kwargs):  # type: ignore
        """
        Automatically called when a class inherits from OnlineLLM.
        It inspects the base classes to find the parameterized
        OnlineLLM generic and extracts the OutputType.
        """
        # Always call super() for cooperative multiple inheritance
        super().__init_subclass__(**kwargs)
        print("initializing subclass...")

        # Get the original base classes tuple if it exists
        orig_bases = getattr(cls, "__orig_bases__", None)
        print(f"orig_bases: {orig_bases}")
        if not orig_bases:
            # This might happen if the class is not directly inheriting
            # a parameterized generic, or in edge cases.
            # We might only want to enforce this for direct subclasses.
            if OnlineLLM in cls.__bases__:
                print(
                    f"Warning: Subclass {cls.__name__} inherits from OnlineLLM but "
                    f"could not find original parameterized base."
                )
            return  # Cannot determine types

        # Find the specific OnlineLLM[...] base class among the original bases
        online_llm_base = None
        for base in orig_bases:
            origin = getattr(base, "__origin__", None)
            print(f"origin: {origin}")
            if origin is OnlineLLM and hasattr(base, "__args__"):
                print("found online_llm_base")
                online_llm_base = base
                break

        if online_llm_base:
            args = get_args(online_llm_base)
            print(f"args: {args}")
            # Expected order: InputType, OutputType, ExampleType
            if len(args) >= 2:
                output_type_arg = args[1]
                # Check if it's a concrete type (not a TypeVar)
                # and preferably a BaseModel (matching the bound)
                if isinstance(output_type_arg, type) and issubclass(
                    output_type_arg, BaseModel
                ):
                    print(f"Setting {cls.__name__}.output_model = {output_type_arg}")
                    cls.output_model = output_type_arg  # type: ignore
                elif isinstance(output_type_arg, TypeVar):
                    print(
                        f"Warning: Output type for {cls.__name__} is still a TypeVar ({output_type_arg}). "
                        f"Subclass must provide a concrete type."
                    )
                else:
                    print(
                        f"Warning: Inferred output type {output_type_arg} for {cls.__name__} "
                        f"is not a concrete pydantic BaseModel."
                    )
                    # Decide if you want to assign anyway or raise an error
                    # cls.output_model = output_type_arg # Assigning might lead to runtime errors later
            else:
                print(
                    f"Warning: Parameterized base {online_llm_base} for {cls.__name__} "
                    f"does not have enough type arguments."
                )
        elif OnlineLLM in cls.__bases__:
            # Only raise error/warning if it's a *direct* subclass lacking parameterization
            raise TypeError(
                f"Class {cls.__name__} must inherit from a parameterized version of OnlineLLM, "
                f"e.g., OnlineLLM[MyInput, MyOutput, MyExample]"
            )

    def __init__(
        self,
        name: str,
        model: str,
        server: V1ResourceReference,
        trainer: V1Trainer,
        train_every: Optional[int] = None,
        sample_n: Optional[int] = None,
        sample_strategy: Optional[str] = None,
        num_epochs: Optional[int] = None,
        namespace: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        adapter: Optional[str] = None,
        config: Optional[GlobalConfig] = None,
        no_delete: bool = False,
        api_key: Optional[str] = None,
    ):
        self.config = config or GlobalConfig.read()
        current_server = self.config.get_current_server_config()
        if not current_server:
            raise ValueError("No current server config found.")
        self.api_key = api_key or current_server.api_key
        self.orign_host = current_server.server
        self.name = name
        self.namespace = namespace
        self.labels = labels
        self.model = model
        self.llms_url = f"{self.orign_host}/v1/llms"
        self.adapter = adapter

        # Parse name and namespace first
        name_parts = name.split("/")
        if len(name_parts) == 2:
            self.namespace = name_parts[0]
            self.name = name_parts[1]
        else:
            # Keep provided namespace if name doesn't contain one
            self.namespace = namespace
            self.name = name

        if not self.namespace:
            self.namespace = "-"

        print(f"Using namespace: {self.namespace}, name: {self.name}")

        # Attempt to fetch the specific LLM directly
        specific_llm_url = f"{self.llms_url}/{self.namespace}/{self.name}"
        response = requests.get(
            specific_llm_url, headers={"Authorization": f"Bearer {self.api_key}"}
        )

        self.llm: Optional[V1OnlineLLM] = None
        if response.status_code == 404:
            print(f"LLM {self.namespace}/{self.name} not found.")
            self.llm = None
        elif response.ok:
            self.llm = V1OnlineLLM.model_validate(response.json())
            print(f"Found existing LLM {self.namespace}/{self.name}")
        else:
            # Handle other errors (e.g., 500, 403)
            response.raise_for_status()

        # If not found, create
        if not self.llm:
            request = V1OnlineLLMRequest(
                metadata=V1ResourceMetaRequest(
                    name=self.name,
                    namespace=self.namespace,
                    labels=labels,
                ),
                model=model,
                server=server,
                trainer=trainer,
                train_every=train_every,
                sample_n=sample_n,
                sample_strategy=sample_strategy,
                num_epochs=num_epochs,
            )
            print("Request:")
            print(request.model_dump_json())

            create_response = requests.post(
                self.llms_url,
                json=request.model_dump(),
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            create_response.raise_for_status()

            self.llm = V1OnlineLLM.model_validate(create_response.json())
            print(f"Created LLM {self.llm.metadata.name}")
        else:
            # Else, update
            print(f"Found LLM {self.llm.metadata.name}, updating if necessary")
            update_request = V1UpdateOnlineLLMRequest(
                model=model,
                server=server,
                trainer=trainer,
                no_delete=no_delete,
                train_every=train_every,
                sample_n=sample_n,
                sample_strategy=sample_strategy,
                num_epochs=num_epochs,
            )
            print("Update request:")
            print(update_request.model_dump_json())

            patch_response = requests.patch(
                f"{self.llms_url}/{self.llm.metadata.namespace}/{self.llm.metadata.name}",
                json=update_request.model_dump(),
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            patch_response.raise_for_status()
            print(f"Updated LLM {self.llm.metadata.name}")

    def generate(self, data: InputType | Dict[str, Any]) -> OutputType:
        """
        Generate an output from the LLM.
        """
        if not self.llm or not self.llm.metadata.name:
            raise ValueError("LLM not found")

        # If the data is a ChatRequest, update its model field
        if isinstance(data, ChatRequest):
            data.model = f"{self.llm.metadata.namespace}/{self.llm.metadata.name}"

        # Handle the input data
        input_data: Dict[str, Any]
        if isinstance(data, dict):
            # Use the dictionary directly
            if "model" in data:
                data["model"] = (
                    f"{self.llm.metadata.namespace}/{self.llm.metadata.name}"
                )
            input_data = data
        elif hasattr(data, "model_dump") and callable(data.model_dump):
            # If it's a Pydantic model with model_dump method
            input_data = data.model_dump()
        else:
            # Handle unexpected input types
            raise TypeError(f"Input must be a dict or Pydantic model, got {type(data)}")

        url = f"{self.llms_url}/{self.llm.metadata.namespace}/{self.llm.metadata.name}/generate"

        print(f"Input data: {input_data}")

        response = requests.post(
            url,
            json=input_data,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        response.raise_for_status()
        response_json = response.json()
        print("response: ", response_json)
        adapter = TypeAdapter(self.output_model)
        print("adapter: ", adapter)

        # Rebuild the adapter
        adapter.rebuild()

        # Extract the content field if it exists in the response
        if isinstance(response_json, dict) and "content" in response_json:
            content = response_json["content"]
            print("content: ", content)
            val = adapter.validate_python(content)
            print("val: ", val)
            return val
        else:
            val = adapter.validate_python(response_json)
            print("val: ", val)
            return val

    def train(
        self,
        wait: bool = False,
        strategy: Optional[str] = None,
        n: Optional[int] = None,
        extra_args: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """
        Train the LLM.

        Args:
            wait: Whether to wait for training to complete
            strategy: Optional sample strategy
            n: Optional sample size
            extra_args: Optional additional arguments for training
        """
        if not self.llm or not self.llm.metadata.name:
            raise ValueError("LLM not found")

        url = f"{self.llms_url}/{self.llm.metadata.namespace}/{self.llm.metadata.name}/train"

        # Create request body
        request_body = {}
        if strategy is not None:
            request_body["strategy"] = strategy
        if n is not None:
            request_body["n"] = n
        if extra_args is not None:
            request_body["extra_args"] = extra_args

        response = requests.post(
            url, json=request_body, headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        # {
        #     "success": true,
        #     "stream_id": stream_id,
        #     "message_id": message.id
        # }
        message_id = response.json()["message_id"]
        print(f"Training message_id: {message_id}")
        if wait:
            if not self.namespace:
                raise ValueError("Namespace not found")
            ref = V1ResourceReference(
                namespace=self.namespace,
                name=self.name,
                kind="Adapter",
            )
            while True:
                trainings = Training.get(
                    adapter_ref=ref,
                    labels={"message_id": message_id},
                )
                if trainings:
                    training = trainings[0]
                    if training.status == V1TrainingStatus.COMPLETED:
                        print("Training completed!")
                        break
                    else:
                        print(f"Training status: {training.status.value}")
                else:
                    print("Wating for training to start...")
                time.sleep(5)
        return response.json()

    def learn(
        self,
        examples: Union[Dict[str, Any], List[Dict[str, Any]], List[ExampleType]],
        train: bool = False,
    ):
        """
        Learn from a list of examples.

        Examples can be:
        - A single dictionary representing a conversation.
        - A list of dictionaries, each representing a conversation.
        - An instance of the ExampleType model.
        """

        if not self.llm or not self.llm.metadata.name:
            raise ValueError("LLM not found")

        processed_examples: List[Dict[str, Any]] = []

        if isinstance(examples, dict):
            processed_examples = [examples]
        elif isinstance(examples, list):  # type: ignore
            # Process each item in the list - could be Dict or ExampleType
            for item in examples:
                if isinstance(item, dict):
                    processed_examples.append(item)
                elif hasattr(item, "model_dump") and callable(item.model_dump):
                    processed_examples.append(item.model_dump())
                else:
                    raise TypeError(f"Unsupported type in list: {type(item).__name__}")
        elif hasattr(examples, "model_dump") and callable(examples.model_dump):
            # If it's a Pydantic model with model_dump method
            processed_examples = [examples.model_dump()]
        else:
            # Raise an error for unexpected types
            raise TypeError(f"Unsupported type for examples: {type(examples).__name__}")

        url = f"{self.llms_url}/{self.llm.metadata.namespace}/{self.llm.metadata.name}/learn"

        print(f"Processed example: {processed_examples[0]}")
        # Now processed_examples is guaranteed to be List[Dict[str, Any]]
        request = V1ReplayBufferData(examples=processed_examples, train=train)

        response = requests.post(
            url,
            json=request.model_dump(),
            headers={"Authorization": f"Bearer {self.api_key}"},
        )

        response.raise_for_status()
        return response.json()

    @classmethod
    def load(
        cls,
        name: str,
        namespace: Optional[str] = None,
        config: Optional[GlobalConfig] = None,
    ):
        """
        Get an LLM from the remote server.
        """
        llms = cls.get(namespace=namespace, name=name, config=config)
        if not llms:
            raise ValueError("LLM not found")
        llm_v1 = llms[0]

        out = cls.__new__(cls)
        out.llm = llm_v1
        out.config = config or GlobalConfig.read()
        current_server = out.config.get_current_server_config()
        if not current_server:
            raise ValueError("No current server config found.")
        out.api_key = current_server.api_key
        out.orign_host = current_server.server
        out.llms_url = f"{out.orign_host}/v1/llms"
        out.name = name
        out.namespace = namespace
        out.model = llm_v1.model
        return out

    @classmethod
    def get(
        cls,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        config: Optional[GlobalConfig] = None,
        api_key: Optional[str] = None,
    ) -> List[V1OnlineLLM]:
        """
        Get a list of LLMs that match the optional name and/or namespace filters.
        """
        config = config or GlobalConfig.read()
        current_server = config.get_current_server_config()
        if not current_server:
            raise ValueError("No current server config found.")
        api_key = api_key or current_server.api_key
        llms_url = f"{current_server.server}/v1/llms"

        response = requests.get(
            llms_url, headers={"Authorization": f"Bearer {api_key}"}
        )
        response.raise_for_status()

        llms_response = V1OnlineLLMs.model_validate(response.json())
        filtered_llms = llms_response.llms

        if name:
            filtered_llms = [llm for llm in filtered_llms if llm.metadata.name == name]
        if namespace:
            filtered_llms = [
                llm for llm in filtered_llms if llm.metadata.namespace == namespace
            ]

        return filtered_llms

    def delete(self):
        """
        Delete the LLM.
        """
        if not self.llm or not self.llm.metadata.name:
            raise ValueError("LLM not found")

        url = f"{self.llms_url}/{self.llm.metadata.namespace}/{self.llm.metadata.name}"
        response = requests.delete(
            url, headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return

    def status(self) -> V1OnlineLLMStatus:
        """
        Get the status of the LLM.
        """
        if not self.llm or not self.llm.metadata.name:
            raise ValueError("LLM not found")

        llms = self.get(
            namespace=self.llm.metadata.namespace, name=self.llm.metadata.name
        )
        if not llms:
            raise ValueError("LLM not found")
        llm = llms[0]

        return llm.status

    def ref(self) -> str:
        """
        Get the resource ref for the container.
        """
        return f"{self.name}.{self.namespace}.Container"
