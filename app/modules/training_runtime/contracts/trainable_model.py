from abc import (
    ABC,
)

from torch import (
    nn,
)


class TrainableModel(
    nn.Module,
    ABC,
):

    def __init__(self):

        super().__init__()

    async def initialize_from_source(
        self,
        loaded_source,
    ) -> None:
        """
        Default implementation.

        Models may override if they need custom loading.
        """

        if loaded_source is None:
            return

        if isinstance(
            loaded_source,
            dict,
        ):
            self.load_state_dict(
                loaded_source,
                strict=False,
            )