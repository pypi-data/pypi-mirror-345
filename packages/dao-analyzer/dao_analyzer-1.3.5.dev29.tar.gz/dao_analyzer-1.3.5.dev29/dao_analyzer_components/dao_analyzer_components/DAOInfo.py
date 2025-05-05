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


class DAOInfo(Component):
    """A DAOInfo component.
DAOInfo is the component on the top left of the second header
It receives the DAO name, the network(s), the address, the creation date,
and the participation statistics and shows them in a grid view.

Keyword arguments:

- id (string; default 'dao-info'):
    The ID used to identify the component in Dash callbacks.

- address (string; optional):
    The address of the organization.

- creation_date (string; optional):
    The creation date of the organization.

- first_activity (string; optional):
    The date where the first activity was recorded.

- name (string; default 'no name given'):
    The organization (DAO) name.

- network (string; optional):
    The network the DAO is deployed on.

- participation_stats (list of dicts; optional):
    The array of participation_stats objects."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dao_analyzer_components'
    _type = 'DAOInfo'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        name: typing.Optional[str] = None,
        network: typing.Optional[str] = None,
        address: typing.Optional[str] = None,
        creation_date: typing.Optional[str] = None,
        first_activity: typing.Optional[str] = None,
        participation_stats: typing.Optional[typing.Sequence[dict]] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'address', 'creation_date', 'first_activity', 'name', 'network', 'participation_stats']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'address', 'creation_date', 'first_activity', 'name', 'network', 'participation_stats']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DAOInfo, self).__init__(**args)

setattr(DAOInfo, "__init__", _explicitize_args(DAOInfo.__init__))
