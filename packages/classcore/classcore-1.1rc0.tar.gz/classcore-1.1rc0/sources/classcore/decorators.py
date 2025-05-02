# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Utilities for the decoration of classes, including metaclasses. '''


from __future__ import annotations

from . import __
from . import nomina as _nomina
from . import utilities as _utilities


_T = __.typx.TypeVar( '_T', bound = type )


def apply_decorators( cls: type, decorators: _nomina.Decorators ) -> type:
    ''' Applies sequence of decorators to class.

        If decorators replace classes (e.g., ``dataclass( slots = True )``),
        then any necessary repairs are performed on the replacement class with
        respect to the original. E.g., on CPython, the class closure cell is
        repaired so that ``super`` operates correctly in methods of the
        replacement class.
    '''
    for decorator in decorators:
        cls_ = decorator( cls )
        if cls is cls_: continue # Simple mutation. No replacement.
        _utilities.repair_class_reproduction( cls, cls_ )
        cls = cls_ # Use the replacement class.
    return cls


def decoration_by(
    *decorators: _nomina.Decorator,
    preparers: _nomina.DecorationPreparers = ( ),
) -> _nomina.Decorator:
    ''' Class decorator which applies other class decorators.

        Useful to apply a stack of decorators as a sequence.

        Can optionally execute a sequence of decoration preparers before
        applying the decorators proper. These can be used to alter the
        decorators list itself, such as to inject decorators based on
        introspection of the class.
    '''
    def decorate( cls: type ) -> type:
        decorators_ = list( decorators )
        for preparer in preparers: preparer( cls, decorators_ )
        return apply_decorators( cls, decorators_ )

    return decorate


def produce_class_construction_decorator(
    attributes_namer: _nomina.AttributesNamer,
    constructor: _nomina.ClassConstructor,
) -> _nomina.Decorator:
    ''' Produces metaclass decorator to control class construction.

        Decorator overrides ``__new__`` on metaclass.
    '''
    def decorate( clscls: type[ _T ] ) -> type[ _T ]:
        constructor_name = attributes_namer( 'classes', 'constructor' )
        extant = getattr( clscls, constructor_name, None )
        original = getattr( clscls, '__new__' )
        if extant is original: return clscls

        def construct(
            clscls_: type[ _T ],
            name: str,
            bases: tuple[ type, ... ],
            namespace: dict[ str, __.typx.Any ], *,
            decorators: _nomina.Decorators = ( ),
            **arguments: __.typx.Any,
        ) -> type[ object ]:
            return constructor(
                clscls_, original,
                name, bases, namespace, arguments, decorators )

        setattr( clscls, constructor_name, construct )
        setattr( clscls, '__new__', construct )
        return clscls

    return decorate


def produce_class_initialization_decorator(
    attributes_namer: _nomina.AttributesNamer,
    initializer: _nomina.ClassInitializer,
) -> _nomina.Decorator:
    ''' Produces metaclass decorator to control class initialization.

        Decorator overrides ``__init__`` on metaclass.
    '''
    def decorate( clscls: type[ _T ] ) -> type[ _T ]:
        initializer_name = attributes_namer( 'classes', 'initializer' )
        extant = getattr( clscls, initializer_name, None )
        original = getattr( clscls, '__init__' )
        if extant is original: return clscls

        @__.funct.wraps( original )
        def initialize(
            cls: type, *posargs: __.typx.Any, **nomargs: __.typx.Any
        ) -> None:
            ligation = __.funct.partial( original, cls )
            initializer( cls, ligation, posargs, nomargs )

        setattr( clscls, initializer_name, initialize )
        clscls.__init__ = initialize
        return clscls

    return decorate
