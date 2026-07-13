import hashlib
import json

from copy import deepcopy

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tokenizers.repositories.tokenizer_training_lifecycle_repository import (
    tokenizer_training_lifecycle_repository,
)

from app.modules.storage_runtime.services.storage_resolution_service import (
    storage_resolution_service,
)

from app.modules.training_runtime.contracts.training_tokenizer import (
    TrainingTokenizer,
)

from app.modules.training_runtime.schemas.formatted_training_sample import (
    FormattedTrainingSample,
)

from app.modules.training_runtime.schemas.tokenized_training_sample import (
    TokenizedTrainingSample,
)

from app.shared.runtime.dynamic_class_resolver import (
    dynamic_class_resolver,
)


class TrainingTokenizationService:

    async def prepare_configuration(
        self,
        db: AsyncSession,
        tokenizer_version_id: int,
        tokenizer_configuration: dict,
        organization_id: int | None = None,
        workspace_id: int | None = None,
    ) -> dict:

        if not isinstance(tokenizer_configuration, dict):
            raise ValueError(
                "Training tokenizer configuration "
                "must be an object."
            )

        version = await (
            tokenizer_training_lifecycle_repository
            .get_version_by_id(
                db=db,
                tokenizer_version_id=tokenizer_version_id,
            )
        )

        if version is None:
            raise ValueError(
                "Tokenizer version not found."
            )

        if not version.is_active:
            raise ValueError(
                "Tokenizer version is inactive."
            )

        if not version.is_immutable:
            raise ValueError(
                "Tokenizer version must be immutable."
            )

        artifacts = await (
            tokenizer_training_lifecycle_repository
            .list_version_artifacts(
                db=db,
                tokenizer_version_id=tokenizer_version_id,
            )
        )

        if not artifacts:
            raise ValueError(
                "Tokenizer version has no artifacts."
            )

        prepared = deepcopy(
            tokenizer_configuration
        )

        configuration = prepared.get(
            "configuration",
            {},
        )

        if not isinstance(configuration, dict):
            raise ValueError(
                "Training tokenizer 'configuration' "
                "must be an object."
            )

        resolved_configuration = deepcopy(
            configuration
        )

        algorithm_configuration = (
            resolved_configuration.get(
                "algorithm_configuration"
            )
        )

        if algorithm_configuration is None:
            artifact_runtime_configuration = (
                resolved_configuration
            )

        else:
            if not isinstance(
                algorithm_configuration,
                dict,
            ):
                raise ValueError(
                    "'algorithm_configuration' "
                    "must be an object."
                )

            artifact_runtime_configuration = (
                algorithm_configuration
            )

        resolved_artifacts = {}

        for artifact in artifacts:

            resolved_storage = await (
                storage_resolution_service
                .resolve(
                    db=db,
                    storage_instance_id=(
                        artifact.storage_instance_id
                    ),
                    organization_id=organization_id,
                    workspace_id=workspace_id,
                )
            )

            stream = await (
                resolved_storage.runtime.open_read(
                    storage_reference=(
                        artifact.storage_reference
                    )
                )
            )

            try:
                payload = stream.read()
            finally:
                stream.close()

            if not isinstance(payload, bytes):
                raise ValueError(
                    "Tokenizer artifact read must "
                    "return bytes."
                )

            actual_checksum = hashlib.sha256(
                payload
            ).hexdigest()

            expected_checksum = (
                self._normalize_checksum(
                    artifact.checksum
                )
            )

            if actual_checksum != expected_checksum:
                raise ValueError(
                    "Tokenizer artifact checksum mismatch "
                    f"for artifact ID {artifact.id}."
                )

            resolved_artifacts[
                artifact.artifact_code
            ] = {
                "artifact_id": artifact.id,
                "artifact_code": artifact.artifact_code,
                "artifact_type": artifact.artifact_type,
                "storage_instance_id": (
                    artifact.storage_instance_id
                ),
                "storage_reference": (
                    artifact.storage_reference
                ),
                "checksum": artifact.checksum,
                "checksum_valid": True,
                "mime_type": artifact.mime_type,
                "size_bytes": artifact.size_bytes,
                "metadata": deepcopy(
                    artifact.metadata_json or {}
                ),
            }

            if (
                artifact.mime_type
                == "application/json"
            ):
                try:
                    decoded_text = (
                        payload.decode(
                            "utf-8"
                        )
                    )

                except UnicodeDecodeError as exc:
                    raise ValueError(
                        "Tokenizer JSON artifact "
                        "must be valid UTF-8."
                    ) from exc

                try:
                    decoded = json.loads(
                        decoded_text
                    )

                except json.JSONDecodeError as exc:
                    raise ValueError(
                        "Tokenizer JSON artifact "
                        "must contain valid JSON."
                    ) from exc

                if not isinstance(
                    decoded,
                    dict,
                ):
                    raise ValueError(
                        "Tokenizer JSON artifact "
                        "must contain an object."
                    )

                decoded_runtime_configuration = (
                    decoded.get(
                        "runtime_configuration"
                    )
                )

                if isinstance(
                    decoded_runtime_configuration,
                    dict,
                ):
                    artifact_runtime_configuration.update(
                        deepcopy(
                            decoded_runtime_configuration
                        )
                    )

                for key in (
                    "vocabulary",
                    "special_tokens",
                    "token_pattern",
                    "normalization",
                ):
                    if key in decoded:
                        artifact_runtime_configuration[
                            key
                        ] = deepcopy(
                            decoded[key]
                        )

                tokenizer_format = (
                    artifact_runtime_configuration.get(
                        "tokenizer_format"
                    )
                )

                configured_artifact_code = (
                    artifact_runtime_configuration.get(
                        "artifact_code"
                    )
                )

                if (
                    tokenizer_format
                    == "TOKENIZERS_JSON"
                    and
                    configured_artifact_code
                    == artifact.artifact_code
                ):
                    artifact_runtime_configuration[
                        "tokenizer_json"
                    ] = decoded_text

                    artifact_runtime_configuration[
                        "tokenizer_checksum"
                    ] = actual_checksum

        resolved_configuration[
            "version_lineage"
        ] = {
            "tokenizer_id": version.tokenizer_id,
            "tokenizer_version_id": version.id,
            "tokenizer_version": version.version,
            "content_hash": version.content_hash,
        }

        resolved_configuration[
            "artifacts"
        ] = resolved_artifacts

        prepared[
            "configuration"
        ] = resolved_configuration

        return prepared


    def tokenize_batch(
        self,
        samples: list[FormattedTrainingSample],
        tokenizer_configuration: dict,
    ) -> list[TokenizedTrainingSample]:

        tokenizer_class = (
            tokenizer_configuration.get(
                "tokenizer_class"
            )
        )

        if (
            not isinstance(tokenizer_class, str)
            or
            not tokenizer_class.strip()
        ):
            raise ValueError(
                "Training tokenizer configuration must "
                "define 'tokenizer_class'."
            )

        configuration = (
            tokenizer_configuration.get(
                "configuration",
                {},
            )
        )

        if not isinstance(configuration, dict):
            raise ValueError(
                "Training tokenizer 'configuration' "
                "must be an object."
            )

        tokenizer_class_type = (
            dynamic_class_resolver.resolve_class(
                class_path=tokenizer_class,
                expected_base_class=TrainingTokenizer,
            )
        )

        tokenizer = tokenizer_class_type()

        tokenized_samples = (
            tokenizer.tokenize_batch(
                samples=samples,
                configuration=configuration,
            )
        )

        if not isinstance(tokenized_samples, list):
            raise ValueError(
                "Training tokenizer must return a list."
            )

        for sample in tokenized_samples:
            if not isinstance(
                sample,
                TokenizedTrainingSample,
            ):
                raise ValueError(
                    "Training tokenizer returned an "
                    "invalid tokenized sample."
                )

        return tokenized_samples


    @staticmethod
    def _normalize_checksum(
        checksum: str,
    ) -> str:

        if not isinstance(checksum, str):
            raise ValueError(
                "Tokenizer artifact checksum "
                "must be a string."
            )

        normalized = checksum.strip().lower()

        if ":" in normalized:
            algorithm, value = normalized.split(
                ":",
                1,
            )

            if algorithm != "sha256":
                raise ValueError(
                    "Unsupported tokenizer artifact "
                    "checksum algorithm."
                )

            normalized = value

        if (
            len(normalized) != 64
            or any(
                character
                not in "0123456789abcdef"
                for character in normalized
            )
        ):
            raise ValueError(
                "Tokenizer artifact checksum "
                "must be SHA-256."
            )

        return normalized


training_tokenization_service = (
    TrainingTokenizationService()
)