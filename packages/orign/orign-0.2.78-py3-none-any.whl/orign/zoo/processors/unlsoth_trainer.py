import os
import random
import string
from typing import Dict, List, Optional

from nebu import Message, Processor, processor
from nebu.config import GlobalConfig as NebuGlobalConfig
from nebu.containers.models import V1EnvVar
from nebu.errors import RetriableError
from nebu.processors.models import (
    V1Scale,
    V1ScaleDown,
    V1ScaleUp,
    V1ScaleZero,
)
from pydantic import BaseModel

from orign import V1TrainingStatus


class TrainingRequest(BaseModel):
    adapter: str
    dataset: str
    model: str = "unsloth/Qwen2.5-VL-32B-Instruct"
    max_length: int = 65536
    epochs: int = 2
    batch_size: int = 2
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    weight_decay: float = 0.01
    warmup_steps: int = 5
    logging_steps: int = 1
    save_steps: int = 5
    lora_alpha: int = 128
    lora_rank: int = 64
    lora_dropout: float = 0
    optimizer: str = "adamw_8bit"
    owner: Optional[str] = None
    labels: Optional[Dict[str, str]] = None


class TrainingResponse(BaseModel):
    loss: float
    train_steps_per_second: float
    train_samples_per_second: float
    train_runtime: float
    adapter: str
    adapter_uri: str


scale = V1Scale(
    up=V1ScaleUp(above_pressure=10, duration="5m"),
    down=V1ScaleDown(below_pressure=2, duration="10m"),
    zero=V1ScaleZero(duration="10m"),
)

setup_script = """
apt update
apt install -y git
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
pip install trl peft transformers bitsandbytes sentencepiece accelerate orign
pip uninstall -y xformers
pip install -U xformers --index-url https://download.pytorch.org/whl/cu126
pip install -e git+https://github.com/pbarker/unsloth-zoo.git#egg=unsloth_zoo
pip install -e git+https://github.com/pbarker/unsloth.git#egg=unsloth
pip install huggingface_hub[hf_xet]
"""


def train_unsloth_sft(message: Message[TrainingRequest]) -> TrainingResponse:
    import json
    import time

    import requests
    from unsloth import FastVisionModel, is_bf16_supported  # type: ignore # isort: skip
    from unsloth.trainer import UnslothVisionDataCollator  # type: ignore # isort: skip

    # Perform a comprehensive state reset at the beginning of each message processing
    # This helps prevent issues with meta tensors between consecutive runs
    import gc

    import torch  # type: ignore
    from chatmux import oai_to_unsloth
    from nebu import (
        Bucket,
        ContainerConfig,
        V1ResourceReference,
        find_latest_checkpoint,
        is_allowed,
    )
    from trl import SFTConfig, SFTTrainer  # type: ignore

    from orign import Adapter, Training, V1LoraParams

    # First ensure CUDA cache is cleared
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

    # Force garbage collection multiple times to ensure all tensors are released
    gc.collect()

    print("message", message)
    if not message.content:
        raise ValueError("No training request provided")
    training_request: TrainingRequest = message.content

    container_config = ContainerConfig.from_env()
    print("container_config", container_config)

    bucket = Bucket()

    print("loading model...")
    adapter_uri = (
        f"{container_config.namespace_volume_uri}/adapters/{training_request.adapter}"
    )
    time_start_load = time.time()
    model = None
    tokenizer = None  # Initialize tokenizer to None

    adapter_parts = training_request.adapter.split("/")
    if len(adapter_parts) == 2:
        adapter_namespace = adapter_parts[0]
        adapter_name = adapter_parts[1]
    else:
        adapter_name = training_request.adapter
        if training_request.owner:
            adapter_namespace = training_request.owner
        else:
            adapter_namespace = message.handle

    # Ensure adapter_namespace is set
    if not adapter_namespace:
        raise ValueError("Could not determine adapter namespace for training log")

    if training_request.labels:
        training_labels = training_request.labels.copy()
    else:
        training_labels = {}
    training_labels["message_id"] = message.id
    training_labels["container_id"] = os.getenv("NEBU_CONTAINER_ID", "unknown")
    random_chars = "".join(random.choices(string.ascii_letters + string.digits, k=5))

    adapter_ref = V1ResourceReference(
        name=adapter_name,
        namespace=adapter_namespace,
        kind="Adapter",
    )
    print("adapter_ref: ", adapter_ref)

    training = None
    try:
        print("creating training with api_key", message.api_key)
        training = Training(
            name=adapter_name + "-" + random_chars,
            namespace=adapter_namespace,
            config_data=message.model_dump(),
            adapter=adapter_ref,
            labels=training_labels,
            unique_adapter_active=True,
            api_key=message.api_key,
        )
        print("\n >> marking initial training as running")
        training.update(status=V1TrainingStatus.RUNNING)
    except Exception as e:
        print(
            f"FATAL: Failed to create or update Training resource for {adapter_ref}: {e}  --- retrying..."
        )
        # Raise a specific exception type that the consumer can catch
        raise RetriableError(
            f"Failed to set up Training resource: {e}  --- retrying..."
        ) from e

    failure = False
    try:
        print("adapter_namespace", adapter_namespace)
        print("adapter_name", adapter_name)

        adapter = None
        try:
            adapters = Adapter.get(
                adapter_namespace, adapter_name, api_key=message.api_key
            )
        except Exception:
            adapters = []
        print("found adapters", adapters)

        if adapters:
            adapter = adapters[0]

        is_continue = False
        epochs_trained = 0
        checkpoint_path = None
        if adapter:
            print("Found adapter: ", adapter)

            epochs_trained = adapter.epochs_trained

            if not is_allowed(adapter.metadata.owner, message.user_id, message.orgs):
                raise ValueError("You are not allowed to train this existing adapter")

            # Store the local path where the adapter will be synced
            local_adapter_path = (
                f"/latest/{adapter.metadata.namespace}/{adapter.metadata.name}"
            )
            print(f"Local adapter path for sync: {local_adapter_path}")

            time_start = time.time()
            bucket.sync(adapter.uri, local_adapter_path)
            print(f"Synced in {time.time() - time_start} seconds")

            model, tokenizer = FastVisionModel.from_pretrained(
                local_adapter_path,  # Use the local path
                load_in_4bit=False,
                use_gradient_checkpointing="unsloth",
                max_seq_length=65_536,
                dtype=torch.bfloat16,
            )
            is_continue = True
            checkpoint_path = local_adapter_path  # Set the checkpoint path for resuming
            print("Model loaded from adapter path.")
            # Check if the loaded model has PEFT adapters active
            if hasattr(model, "print_trainable_parameters"):
                model.print_trainable_parameters()
            else:
                print(
                    "Model does not have PEFT structure or print_trainable_parameters method."
                )

        if not model:
            print("Loading model from scratch")
            model, tokenizer = FastVisionModel.from_pretrained(
                training_request.model,
                load_in_4bit=False,  # Use 4bit to reduce memory use. False for 16bit LoRA.
                use_gradient_checkpointing="unsloth",  # True or "unsloth" for long context
                dtype=torch.bfloat16,
                max_seq_length=65_536,
            )

            print("getting peft model...")
            # This is only called when NO existing adapter was found
            print("\n*** Initializing NEW PEFT model layers ***\n")
            model = FastVisionModel.get_peft_model(
                model,
                finetune_vision_layers=True,  # False if not finetuning vision layers
                finetune_language_layers=True,  # False if not finetuning language layers
                finetune_attention_modules=True,  # False if not finetuning attention layers
                finetune_mlp_modules=True,  # False if not finetuning MLP layers
                r=training_request.lora_rank,  # The larger, the higher the accuracy, but might overfit
                lora_alpha=training_request.lora_alpha,  # Recommended alpha == r at least
                lora_dropout=training_request.lora_dropout,
                bias="none",
                random_state=3407,
                use_rslora=False,  # We support rank stabilized LoRA
                loftq_config=None,  # And LoftQ
                use_fast=True,
                # target_modules = "all-linear", # Optional now! Can specify a list if needed
            )
        print(f"Loaded model in {time.time() - time_start_load} seconds")

        # Print the model architecture
        print("\n=== Model Architecture ===")
        print(model)
        print("========================\n")

        print("Downloading dataset")
        time_start_download = time.time()
        response = requests.get(training_request.dataset)
        response.raise_for_status()  # optional: raises if request failed
        print(f"Downloaded dataset in {time.time() - time_start_download} seconds")

        # Decode and split into lines
        lines = response.content.decode("utf-8").splitlines()

        # Parse and convert each JSON line
        time_start_convert = time.time()
        converted_dataset = [
            oai_to_unsloth(json.loads(line)) for line in lines if line.strip()
        ]
        print(f"Converted dataset in {time.time() - time_start_convert} seconds")
        print("dataset example", converted_dataset[:1])

        FastVisionModel.for_training(model)  # Enable for training!

        train_epochs = epochs_trained + training_request.epochs
        print("training_request.epochs", training_request.epochs)
        print("epochs_trained", epochs_trained)
        print(f"train_epochs: {train_epochs}")

        # When continuing training, skip token embedding correction to avoid meta tensor issues
        skip_token_correction = is_continue

        output_dir = "outputs"

        # Monkey patch should handle init errors, remove try/except here
        # try:
        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,  # type: ignore
            data_collator=UnslothVisionDataCollator(model, tokenizer),  # type: ignore
            train_dataset=converted_dataset,
            args=SFTConfig(
                per_device_train_batch_size=training_request.batch_size,
                gradient_accumulation_steps=training_request.gradient_accumulation_steps,
                warmup_steps=training_request.warmup_steps,
                # max_steps=training_request.max_steps,
                num_train_epochs=train_epochs,
                learning_rate=training_request.learning_rate,
                fp16=not is_bf16_supported(),
                bf16=is_bf16_supported(),
                logging_steps=training_request.logging_steps,
                optim=training_request.optimizer,
                weight_decay=training_request.weight_decay,
                lr_scheduler_type="linear",
                seed=3407,
                output_dir=output_dir,  # Use the variable defined above
                report_to="none",  # For Weights and Biases
                # You MUST put the below items for vision finetuning:
                remove_unused_columns=False,
                dataset_text_field="",
                dataset_kwargs={
                    "skip_prepare_dataset": True,
                    "skip_token_correction": skip_token_correction,
                },
                dataset_num_proc=4,
                max_seq_length=training_request.max_length,
            ),
        )

        # Set environment variable for Unsloth to return logits
        os.environ["UNSLOTH_RETURN_LOGITS"] = "1"

        time_start_train = time.time()
        try:
            print("Starting trainer.train()...")
            # Pass True if resuming, Trainer will look in output_dir
            # trainer_stats = trainer.train(resume_from_checkpoint=is_continue)
            trainer_stats = trainer.train(
                resume_from_checkpoint=checkpoint_path if is_continue else None
            )
            print(trainer_stats)
        except NotImplementedError as e:
            if "Cannot copy out of meta tensor" in str(e):
                print(
                    "Meta tensor error encountered - this might occur when training the same adapter twice in succession"
                )
                print("Error details:", str(e))
                print("Try running the training in a new process or container")
                # Set a default value for trainer_stats
                trainer_stats = {"train_runtime": time.time() - time_start_train}
                # Still allow the function to complete and return some metrics
            else:
                # Re-raise if it's a different NotImplementedError
                raise
        print(f"Trained in {time.time() - time_start_train} seconds")

        latest_checkpoint = find_latest_checkpoint("outputs")
        print("latest checkpoint")

        # Initialize metrics dict as empty
        training_metrics = {}

        if latest_checkpoint:
            print("Copying latest checkpoint to bucket")
            bucket.copy(
                latest_checkpoint,
                adapter_uri,
            )
            # Try to load the entire trainer_state.json
            trainer_state_path = os.path.join(latest_checkpoint, "trainer_state.json")
            if os.path.exists(trainer_state_path):
                try:
                    with open(trainer_state_path, "r") as f:
                        state_data = json.load(f)
                    training_metrics = state_data  # Use the entire loaded state
                    print(f"Loaded full state from {trainer_state_path}")
                except Exception as e:
                    print(
                        f"Warning: Failed to read/parse {trainer_state_path}: {e}. Proceeding without metrics from state file."
                    )
            else:
                print(
                    f"Warning: {trainer_state_path} not found. Proceeding without metrics from state file."
                )
        else:
            print(
                "Warning: No checkpoint found. Proceeding without metrics from state file."
            )

        adapter = Adapter(
            name=adapter_name,
            namespace=adapter_namespace,
            uri=adapter_uri,
            owner=message.content.owner if message.content.owner else message.user_id,  # type: ignore
            base_model=training_request.model,
            epochs_trained=train_epochs,
            last_trained=int(time.time()),
            lora=V1LoraParams(
                r=training_request.lora_rank,
                alpha=training_request.lora_alpha,
                dropout=training_request.lora_dropout,
            ),
            labels=training_request.labels,
            api_key=message.api_key,
        )

        training.log(data=training_metrics)
        training.update(status=V1TrainingStatus.COMPLETED)

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

        return TrainingResponse(
            loss=training_metrics.get("loss", 0.0),
            train_steps_per_second=training_metrics.get("train_steps_per_second", 0.0),
            train_samples_per_second=training_metrics.get(
                "train_samples_per_second", 0.0
            ),
            train_runtime=training_metrics.get("train_runtime", 0.0),
            adapter=training_request.adapter,
            adapter_uri=adapter_uri,
        )
    except Exception as e:
        print(f"Error training unsloth: {e}")
        failure = True
        if training:
            print("\n >> marking final training as failed")
            training.update(status=V1TrainingStatus.FAILED)
        raise
    finally:
        if training and not failure:
            print("\n >> marking final training as completed")
            training.update(status=V1TrainingStatus.COMPLETED)


def UnslothSFT(
    platform: str = "runpod",
    accelerators: List[str] = ["1:A100_SXM"],
    image: str = "pytorch/pytorch:2.6.0-cuda12.6-cudnn9-devel",
    scale: V1Scale = scale,
    namespace: Optional[str] = None,
    env: Optional[List[V1EnvVar]] = None,
    config: Optional[NebuGlobalConfig] = None,
    hot_reload: bool = True,
    debug: bool = False,
) -> Processor[TrainingRequest, TrainingResponse]:
    decorate = processor(
        image=image,
        setup_script=setup_script,
        accelerators=accelerators,
        platform=platform,
        scale=scale,
        namespace=namespace,
        env=env,
        execution_mode="subprocess",
        config=config,
        hot_reload=hot_reload,
        debug=debug,
    )
    return decorate(train_unsloth_sft)
