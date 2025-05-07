from typing import Any, List, Tuple


def _flatten_args(
    args: List[Any | List[Any]] | Tuple[Any | List[Any], ...],
) -> List[Any]:
    return [
        item
        for sublist in args
        for item in (sublist if isinstance(sublist, list) else [sublist])
    ]
