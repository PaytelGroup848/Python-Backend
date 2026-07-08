from importlib import (
    import_module,
)

from typing import (
    TypeVar,
)


T = TypeVar(
    "T"
)


class DynamicClassResolver:

    def resolve_class(
        self,
        class_path: str,
        expected_base_class: type[T],
    ) -> type[T]:

        normalized_class_path = (
            class_path.strip()
        )

        if not normalized_class_path:
            raise ValueError(
                "Class path is required."
            )

        module_path, separator, class_name = (
            normalized_class_path
            .rpartition(".")
        )

        if (
            not separator
            or
            not module_path
            or
            not class_name
        ):
            raise ValueError(
                "Class path must be a fully qualified "
                "Python class path."
            )

        module = import_module(
            module_path
        )

        resolved_class = getattr(
            module,
            class_name,
            None,
        )

        if resolved_class is None:
            raise ValueError(
                "Configured class was not found: "
                f"'{normalized_class_path}'."
            )

        if (
            not isinstance(
                resolved_class,
                type,
            )
            or
            not issubclass(
                resolved_class,
                expected_base_class,
            )
        ):
            raise ValueError(
                "Configured class does not extend "
                f"'{expected_base_class.__name__}'."
            )

        return resolved_class


dynamic_class_resolver = (
    DynamicClassResolver()
)