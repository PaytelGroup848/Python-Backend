import asyncio
import queue

from dataclasses import (
    dataclass,
)

from pathlib import (
    Path,
)

from collections.abc import (
    Iterator,
)

from tokenizers import (
    Tokenizer,
)

from tokenizers.decoders import (
    ByteLevel as ByteLevelDecoder,
)

from tokenizers.models import (
    BPE,
)

from tokenizers.normalizers import (
    Lowercase,
    Sequence as NormalizerSequence,
    Strip,
)

from tokenizers.pre_tokenizers import (
    ByteLevel,
)

from tokenizers.processors import (
    ByteLevel as ByteLevelProcessor,
)

from tokenizers.trainers import (
    BpeTrainer,
)

from app.modules.tokenizers.contracts.tokenizer_trainer import (
    TokenizerTrainer,
    TokenizerTrainerArtifact,
    TokenizerTrainerResult,
)

from app.modules.training_runtime.contracts.training_data_stream import (
    TrainingDataStream,
)


@dataclass(
    frozen=True,
)
class _ProducerFailure:

    exception: BaseException


class _EndOfStream:

    pass


_END_OF_STREAM = _EndOfStream()


class SubwordBPETokenizerTrainer(
    TokenizerTrainer
):

    async def train(
        self,
        training_data: TrainingDataStream,
        configuration: dict,
        output_directory: Path,
    ) -> TokenizerTrainerResult:

        if not isinstance(
            configuration,
            dict,
        ):
            raise ValueError(
                "Tokenizer trainer configuration "
                "must be an object."
            )

        vocabulary_size = (
            self._positive_integer(
                configuration=configuration,
                key="vocabulary_size",
            )
        )

        minimum_frequency = (
            self._positive_integer(
                configuration=configuration,
                key="minimum_frequency",
                default=2,
            )
        )

        bridge_capacity = (
            self._positive_integer(
                configuration=configuration,
                key="bridge_capacity",
                default=8,
            )
        )

        normalization = (
            configuration.get(
                "normalization",
                {},
            )
        )

        if not isinstance(
            normalization,
            dict,
        ):
            raise ValueError(
                "'normalization' must be an object."
            )

        lowercase = (
            normalization.get(
                "lowercase",
                False,
            )
        )

        strip = (
            normalization.get(
                "strip",
                False,
            )
        )

        if not isinstance(
            lowercase,
            bool,
        ):
            raise ValueError(
                "'lowercase' must be boolean."
            )

        if not isinstance(
            strip,
            bool,
        ):
            raise ValueError(
                "'strip' must be boolean."
            )

        special_tokens = (
            self._special_tokens(
                configuration.get(
                    "special_tokens",
                    {},
                )
            )
        )

        tokenizer = self._build_tokenizer(
            lowercase=lowercase,
            strip=strip,
            special_tokens=special_tokens,
        )

        trainer = BpeTrainer(
            vocab_size=vocabulary_size,
            min_frequency=minimum_frequency,
            special_tokens=[
                definition["token"]
                for definition
                in special_tokens.values()
            ],
            initial_alphabet=(
                ByteLevel.alphabet()
            ),
            show_progress=False,
        )

        bridge: queue.Queue = (
            queue.Queue(
                maxsize=bridge_capacity
            )
        )

        stop_event = (
            asyncio.Event()
        )

        counters = {
            "source_record_count": 0,
            "source_text_count": 0,
        }

        producer_task = (
            asyncio.create_task(
                self._produce_text_batches(
                    training_data=training_data,
                    bridge=bridge,
                    stop_event=stop_event,
                    counters=counters,
                )
            )
        )

        try:
            await asyncio.to_thread(
                self._train_from_bridge,
                tokenizer,
                trainer,
                bridge,
            )

            await producer_task

        except asyncio.CancelledError:

            stop_event.set()

            training_data.request_cancel()

            producer_task.cancel()

            await asyncio.gather(
                producer_task,
                return_exceptions=True,
            )

            raise

        except BaseException:

            stop_event.set()

            training_data.request_cancel()

            producer_task.cancel()

            await asyncio.gather(
                producer_task,
                return_exceptions=True,
            )

            raise

        finally:
            stop_event.set()

        if (
            counters["source_record_count"]
            <= 0
        ):
            raise ValueError(
                "Tokenizer training dataset "
                "must not be empty."
            )

        if (
            counters["source_text_count"]
            <= 0
        ):
            raise ValueError(
                "Tokenizer training dataset contains "
                "no non-empty text."
            )

        actual_vocabulary_size = (
            tokenizer.get_vocab_size(
                with_added_tokens=True
            )
        )

        if actual_vocabulary_size <= 0:
            raise ValueError(
                "Tokenizer training produced "
                "an empty vocabulary."
            )

        tokenizer.decoder = (
            ByteLevelDecoder()
        )

        tokenizer.post_processor = (
            ByteLevelProcessor(
                trim_offsets=True,
            )
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        artifact_path = (
            output_directory
            /
            "tokenizer.json"
        ).resolve()

        tokenizer.save(
            str(
                artifact_path
            )
        )

        if (
            not artifact_path.exists()
            or
            artifact_path.stat().st_size
            <= 0
        ):
            raise ValueError(
                "Tokenizer artifact was not created."
            )

        special_token_ids = (
            self._resolve_special_token_ids(
                tokenizer=tokenizer,
                special_tokens=special_tokens,
            )
        )

        return TokenizerTrainerResult(
            vocabulary_size=(
                actual_vocabulary_size
            ),
            artifacts=[
                TokenizerTrainerArtifact(
                    artifact_code=(
                        "tokenizer.json"
                    ),
                    artifact_type=(
                        "SUBWORD_BPE_TOKENIZER"
                    ),
                    local_path=(
                        artifact_path
                    ),
                    mime_type=(
                        "application/json"
                    ),
                    metadata={
                        "format_version": 1,
                        "source_record_count": (
                            counters[
                                "source_record_count"
                            ]
                        ),
                        "source_text_count": (
                            counters[
                                "source_text_count"
                            ]
                        ),
                        "vocabulary_size": (
                            actual_vocabulary_size
                        ),
                    },
                )
            ],
            runtime_configuration={
                "tokenizer_format": (
                    "TOKENIZERS_JSON"
                ),
                "artifact_code": (
                    "tokenizer.json"
                ),
                "special_tokens": (
                    special_token_ids
                ),
                "normalization": {
                    "lowercase": lowercase,
                    "strip": strip,
                },
            },
            metadata={
                "source_record_count": (
                    counters[
                        "source_record_count"
                    ]
                ),
                "source_text_count": (
                    counters[
                        "source_text_count"
                    ]
                ),
                "requested_vocabulary_size": (
                    vocabulary_size
                ),
                "actual_vocabulary_size": (
                    actual_vocabulary_size
                ),
                "minimum_frequency": (
                    minimum_frequency
                ),
                "bridge_capacity": (
                    bridge_capacity
                ),
            },
        )


    async def _produce_text_batches(
        self,
        training_data: TrainingDataStream,
        bridge: queue.Queue,
        stop_event: asyncio.Event,
        counters: dict,
    ) -> None:

        try:
            async for batch in (
                training_data.iter_batches()
            ):

                if stop_event.is_set():
                    return

                texts = []

                for record in batch.records:

                    if stop_event.is_set():
                        return

                    counters[
                        "source_record_count"
                    ] += 1

                    input_text = (
                        record.input_text
                    )

                    if not isinstance(
                        input_text,
                        str,
                    ):
                        raise ValueError(
                            "Tokenizer training input "
                            "text must be a string."
                        )

                    if input_text:
                        texts.append(
                            input_text
                        )

                        counters[
                            "source_text_count"
                        ] += 1

                    output_text = (
                        record.output_text
                    )

                    if output_text is not None:

                        if not isinstance(
                            output_text,
                            str,
                        ):
                            raise ValueError(
                                "Tokenizer training output "
                                "text must be a string."
                            )

                        if output_text:
                            texts.append(
                                output_text
                            )

                            counters[
                                "source_text_count"
                            ] += 1

                if texts:
                    await self._put_bridge_item(
                        bridge=bridge,
                        item=tuple(texts),
                        stop_event=stop_event,
                    )

            await self._put_bridge_item(
                bridge=bridge,
                item=_END_OF_STREAM,
                stop_event=stop_event,
            )

        except asyncio.CancelledError:
            raise

        except BaseException as exc:

            await self._put_bridge_item(
                bridge=bridge,
                item=_ProducerFailure(
                    exception=exc
                ),
                stop_event=stop_event,
                allow_after_stop=True,
            )


    @staticmethod
    async def _put_bridge_item(
        bridge: queue.Queue,
        item: object,
        stop_event: asyncio.Event,
        allow_after_stop: bool = False,
    ) -> None:

        while True:

            if (
                stop_event.is_set()
                and
                not allow_after_stop
            ):
                return

            try:
                bridge.put_nowait(
                    item
                )

                return

            except queue.Full:
                await asyncio.sleep(
                    0.01
                )


    @staticmethod
    def _train_from_bridge(
        tokenizer: Tokenizer,
        trainer: BpeTrainer,
        bridge: queue.Queue,
    ) -> None:

        tokenizer.train_from_iterator(
            SubwordBPETokenizerTrainer
            ._bridge_iterator(
                bridge=bridge
            ),
            trainer=trainer,
        )


    @staticmethod
    def _bridge_iterator(
        bridge: queue.Queue,
    ) -> Iterator[str]:

        while True:

            item = bridge.get()

            if item is _END_OF_STREAM:
                return

            if isinstance(
                item,
                _ProducerFailure,
            ):
                raise item.exception

            if not isinstance(
                item,
                tuple,
            ):
                raise TypeError(
                    "Tokenizer bridge received "
                    "an invalid item."
                )

            for text in item:

                if not isinstance(
                    text,
                    str,
                ):
                    raise TypeError(
                        "Tokenizer bridge received "
                        "non-string text."
                    )

                yield text


    @staticmethod
    def _build_tokenizer(
        lowercase: bool,
        strip: bool,
        special_tokens: dict,
    ) -> Tokenizer:

        unknown_definition = (
            special_tokens.get(
                "unk"
            )
        )

        unknown_token = (
            unknown_definition["token"]
            if unknown_definition
            is not None
            else None
        )

        tokenizer = Tokenizer(
            BPE(
                unk_token=unknown_token
            )
        )

        normalizers = []

        if strip:
            normalizers.append(
                Strip()
            )

        if lowercase:
            normalizers.append(
                Lowercase()
            )

        if normalizers:
            tokenizer.normalizer = (
                NormalizerSequence(
                    normalizers
                )
            )

        tokenizer.pre_tokenizer = (
            ByteLevel(
                add_prefix_space=False,
                use_regex=True,
            )
        )

        return tokenizer


    @staticmethod
    def _resolve_special_token_ids(
        tokenizer: Tokenizer,
        special_tokens: dict,
    ) -> dict:

        resolved = {}

        for name, definition in (
            special_tokens.items()
        ):

            token = (
                definition["token"]
            )

            token_id = (
                tokenizer.token_to_id(
                    token
                )
            )

            if token_id is None:
                raise ValueError(
                    "Trained tokenizer did not "
                    "preserve special token "
                    f"'{name}'."
                )

            resolved[name] = {
                "token": token,
                "id": token_id,
            }

        return resolved


    @staticmethod
    def _positive_integer(
        configuration: dict,
        key: str,
        default: int | None = None,
    ) -> int:

        value = (
            configuration.get(
                key,
                default,
            )
        )

        if (
            isinstance(
                value,
                bool,
            )
            or
            not isinstance(
                value,
                int,
            )
            or
            value <= 0
        ):
            raise ValueError(
                f"'{key}' must be a "
                "positive integer."
            )

        return value


    @staticmethod
    def _special_tokens(
        value: object,
    ) -> dict:

        if not isinstance(
            value,
            dict,
        ):
            raise ValueError(
                "'special_tokens' must be "
                "an object."
            )

        normalized = {}

        seen_tokens = set()

        for name, definition in (
            value.items()
        ):

            if (
                not isinstance(
                    name,
                    str,
                )
                or
                not name.strip()
            ):
                raise ValueError(
                    "Special token names must "
                    "be non-empty strings."
                )

            if isinstance(
                definition,
                str,
            ):
                token = (
                    definition
                )

            elif isinstance(
                definition,
                dict,
            ):
                token = (
                    definition.get(
                        "token"
                    )
                )

            else:
                raise ValueError(
                    "Special token definitions "
                    "must be strings or objects."
                )

            if (
                not isinstance(
                    token,
                    str,
                )
                or
                not token
            ):
                raise ValueError(
                    "Special token definition "
                    "must contain a non-empty token."
                )

            if token in seen_tokens:
                raise ValueError(
                    "Special token values must "
                    "be unique."
                )

            seen_tokens.add(
                token
            )

            normalized[
                name.strip()
            ] = {
                "token": token,
            }

        return normalized