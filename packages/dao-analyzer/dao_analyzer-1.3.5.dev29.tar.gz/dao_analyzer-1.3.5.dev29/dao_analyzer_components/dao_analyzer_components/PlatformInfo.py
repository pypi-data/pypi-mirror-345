# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class PlatformInfo(Component):
    """A PlatformInfo component.
PlatformInfo is the component on the top left of the second header
It receives the DAO name, the network(s) and other data and displays it in a grid view.

Keyword arguments:

- creation_date (string; optional):
    The creation date of the organization.

- name (string; optional):
    The name of the platform.

- networks (list of strings; optional):
    The networks the platform is deployed in.

- participation_stats (list of dicts; optional):
    The array of participation_stats objects."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dao_analyzer_components'
    _type = 'PlatformInfo'


    def __init__(
        self,
        name: typing.Optional[str] = None,
        networks: typing.Optional[typing.Sequence[str]] = None,
        creation_date: typing.Optional[str] = None,
        participation_stats: typing.Optional[typing.Sequence[dict]] = None,
        **kwargs
    ):
        self._prop_names = ['creation_date', 'name', 'networks', 'participation_stats']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['creation_date', 'name', 'networks', 'participation_stats']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(PlatformInfo, self).__init__(**args)

setattr(PlatformInfo, "__init__", _explicitize_args(PlatformInfo.__init__))
