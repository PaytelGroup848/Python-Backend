from pathlib import Path


class ArtifactLoader:

    def resolve(

        self,

        artifact_path: str

    ) -> Path:

        path = Path(
            artifact_path
        )

        if not path.exists():

            raise FileNotFoundError(
                artifact_path
            )

        return path


artifact_loader = (
    ArtifactLoader()
)