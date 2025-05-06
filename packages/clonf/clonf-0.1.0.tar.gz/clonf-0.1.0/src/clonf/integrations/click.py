from __future__ import annotations
import typing as t
from pydantic import BaseModel
import functools

import typing_extensions as te
from ..annotations import ClonfAnnotation, CliArgument, CliOption
from ..extractor import extract_cli_info
import typing as t
import datetime
import pathlib
import uuid

try:
    import click
except ImportError:  # pragma: no cover
    raise ImportError("clonf integration with click requires click to be installed")

_TReturn = t.TypeVar("_TReturn", covariant=True)


_CliFunc: te.TypeAlias = t.Callable[..., _TReturn]


class _WrappedFunc(t.Protocol, t.Generic[_TReturn]):
    def __call__(self, **kwargs: t.Any) -> _TReturn: ...


def _extract_cli_info_click(model: type[BaseModel]) -> list[ClonfAnnotation]:
    cli_infos = extract_cli_info(model)

    for cli_info in cli_infos:
        if cli_info._type is None or cli_info._field_info is None:  # pragma: no cover
            continue

        for meta in cli_info._field_info.metadata:
            if isinstance(meta, click.ParamType):
                cli_info._type = meta
                break

        if isinstance(cli_info._type, click.ParamType):
            continue

        type_origin = t.get_origin(cli_info._type)
        if type_origin is t.Literal:
            literal_values = t.get_args(cli_info._type)
            cli_info._type = click.Choice(*literal_values)
        elif type_origin is not None:
            raise TypeError(f"Don't know how to handle type {type_origin}")
        elif issubclass(cli_info._type, (datetime.datetime, datetime.date)):
            cli_info._type = click.DateTime()
        elif issubclass(cli_info._type, pathlib.Path):
            cli_info._type = click.Path(path_type=pathlib.Path)
        elif issubclass(cli_info._type, uuid.UUID):
            cli_info._type = click.UUID
        elif issubclass(cli_info._type, int) or issubclass(cli_info._type, float):
            range_kwargs = {
                "min": cli_info._field_info._attributes_set.get("gt", None)
                or cli_info._field_info._attributes_set.get("ge", None),
                "max": cli_info._field_info._attributes_set.get("lt", None)
                or cli_info._field_info._attributes_set.get("le", None),
                "min_open": cli_info._field_info._attributes_set.get("ge", None)
                is not None,
                "max_open": cli_info._field_info._attributes_set.get("le", None)
                is not None,
            }

            if issubclass(cli_info._type, int):
                cli_info._type = click.IntRange(**range_kwargs)  # type: ignore[arg-type]
            elif issubclass(cli_info._type, float):
                cli_info._type = click.FloatRange(**range_kwargs)  # type: ignore[arg-type]

    return cli_infos


def clonf_click(
    func: _CliFunc[_TReturn],
) -> _WrappedFunc[_TReturn]:
    # TODO: replace with inspect.get_annotations when deprecating PY39
    func_annotations: dict[str, t.Any] | None = getattr(func, "__annotations__", None)
    if func_annotations is None:  # pragma: no cover
        raise ValueError("Could not extract annotations from input func")

    cli_infos: dict[str, list[ClonfAnnotation]] = {}
    for arg, ann in func_annotations.items():
        if arg == "return":
            continue
        assert issubclass(ann, BaseModel), (
            f"Input type {ann} is not a subclass of BaseModel"
        )

        cli_infos[arg] = _extract_cli_info_click(ann)

    @functools.wraps(func)
    @click.pass_context
    def wrapper(ctx: click.Context, /, **kwargs: t.Any) -> _TReturn:
        new_kwargs: dict[str, BaseModel] = {}

        for arg, ann in func_annotations.items():
            if arg == "return":
                continue
            cli_info_names: set[str] = {
                cli_info.name
                for cli_info in cli_infos[arg]
                if cli_info.name is not Ellipsis
            }
            selected_kwargs = {k: v for k, v in kwargs.items() if k in cli_info_names}
            to_remove: list[str] = []
            for kwarg, v in selected_kwargs.items():
                param: click.Parameter | None = None
                for s_param in ctx.command.params:
                    if s_param.name == kwarg:
                        param = s_param
                        break
                if param is None:  # pragma: no cover
                    raise ValueError(f"Could not find parameter for input: {kwarg}")
                default = param.get_default(ctx)
                if default == v:
                    to_remove.append(kwarg)

            for kwarg in to_remove:
                del selected_kwargs[kwarg]

            new_kwargs[arg] = ann(**selected_kwargs)

        result = func(**new_kwargs)

        return result

    for sub_cli_infos in cli_infos.values():
        for cli_info in sub_cli_infos:
            if isinstance(cli_info, CliArgument):
                assert isinstance(cli_info.name, str), (
                    "CliArgument has no resolved name"
                )
                click.argument(
                    cli_info.name,
                    default=None if cli_info.default is Ellipsis else cli_info.default,
                    type=cli_info._type,
                )(wrapper)
            elif isinstance(cli_info, CliOption):
                assert isinstance(cli_info.name, str), "CliOption has no resolved name"
                click.option(
                    f"{cli_info.prefix}{cli_info.name}",
                    default=None if cli_info.default is Ellipsis else cli_info.default,
                    type=cli_info._type,
                    help=cli_info.description,
                )(wrapper)

    return wrapper
