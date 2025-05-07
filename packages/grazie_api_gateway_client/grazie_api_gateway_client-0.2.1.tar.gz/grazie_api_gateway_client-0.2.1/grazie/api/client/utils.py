from typing import Any, Dict, Union

import attrs


def filter_fields(obj: Dict[str, Any], t: Any):
    return {k: v for k, v in obj.items() if k in attrs.fields_dict(t)}


def typ(t: Any, **kwargs) -> Any:
    return attrs.field(converter=lambda obj: t(**filter_fields(obj, t)), **kwargs)


def typ_or_none(t: Any, **kwargs) -> Union[Any, None]:
    return attrs.field(
        converter=lambda obj: t(**filter_fields(obj, t)) if obj is not None else None,
        default=None,
        **kwargs,
    )
