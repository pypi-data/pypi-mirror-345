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


''' Standard decorators. '''
# TODO? Add attribute value transformer as standard decorator argument.

# ruff: noqa: F401


from __future__ import annotations

from .. import factories as _factories
from .. import utilities as _utilities
from ..decorators import (
    decoration_by,
    produce_class_construction_decorator,
    produce_class_initialization_decorator,
)
from . import __
from . import behaviors as _behaviors
from . import nomina as _nomina


_U = __.typx.TypeVar( '_U' )


_dataclass_core = __.dcls.dataclass( kw_only = True, slots = True )


def _produce_class_factory_core(
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
) -> tuple[ _nomina.ClassConstructor, _nomina.ClassInitializer ]:
    preprocessors = (
        _behaviors.produce_class_construction_preprocessor(
            attributes_namer = attributes_namer ), )
    postprocessors = (
        _behaviors.produce_class_construction_postprocessor(
            attributes_namer = attributes_namer ), )
    completers = (
        _behaviors.produce_class_initialization_completer(
            attributes_namer = attributes_namer ), )
    constructor = (
        _factories.produce_class_constructor(
            attributes_namer = attributes_namer,
            preprocessors = preprocessors,
            postprocessors = postprocessors ) )
    initializer = (
        _factories.produce_class_initializer(
            attributes_namer = attributes_namer,
            completers = completers ) )
    return constructor, initializer


def prepare_dataclass_for_instances(
    cls: type,
    decorators: _nomina.DecoratorsMutable, /, *,
    attributes_namer: _nomina.AttributesNamer,
) -> None:
    ''' Annotates dataclass in support of instantiation machinery. '''
    annotations = __.inspect.get_annotations( cls )
    behaviors_name = attributes_namer( 'instance', 'behaviors' )
    behaviors_name_m = _utilities.mangle_name( cls, behaviors_name )
    annotations[ behaviors_name_m ] = set[ str ]
    setattr( cls, '__annotations__', annotations ) # in case of absence
    setattr( cls, behaviors_name_m, __.dcls.field( init = False ) )


def produce_class_factory_decorators(
    attributes_namer: _nomina.AttributesNamer = __.calculate_attrname,
    error_class_provider: _nomina.ErrorClassProvider = __.provide_error_class,
    assigner_core: _nomina.AssignerCore = (
        _behaviors.assign_attribute_if_mutable ),
    deleter_core: _nomina.DeleterCore = (
        _behaviors.delete_attribute_if_mutable ),
    surveyor_core: _nomina.SurveyorCore = (
        _behaviors.survey_visible_attributes ),
) -> _nomina.Decorators:
    decorators: list[ _nomina.Decorator ] = [ ]
    constructor, initializer = (
        _produce_class_factory_core(
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider ) )
    decorators.append(
        produce_class_construction_decorator(
            attributes_namer = attributes_namer,
            constructor = constructor ) )
    decorators.append(
        produce_class_initialization_decorator(
            attributes_namer = attributes_namer,
            initializer = initializer ) )
    decorators.append(
        produce_attributes_assignment_decorator(
            level = 'class',
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            implementation_core = assigner_core ) )
    decorators.append(
        produce_attributes_deletion_decorator(
            level = 'class',
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            implementation_core = deleter_core ) )
    decorators.append(
        produce_attributes_surveillance_decorator(
            level = 'class',
            attributes_namer = attributes_namer,
            implementation_core = surveyor_core ) )
    return decorators


def produce_instances_initialization_decorator(
    attributes_namer: _nomina.AttributesNamer,
    mutables: _nomina.BehaviorExclusionVerifiersOmni,
    visibles: _nomina.BehaviorExclusionVerifiersOmni,
) -> _nomina.Decorator:
    def decorate( cls: type[ _U ] ) -> type[ _U ]:
        initializer_name = attributes_namer( 'instances', 'initializer' )
        extant = getattr( cls, initializer_name, None )
        original = getattr( cls, '__init__' )
        if extant is original: return cls
        behaviors: set[ str ] = set( )
        behaviors_name = attributes_namer( 'instance', 'behaviors' )
        behaviors_name_m = _utilities.mangle_name( cls, behaviors_name )
        _behaviors.record_behavior(
            cls, attributes_namer = attributes_namer,
            level = 'instances', basename = 'mutables',
            label = _behaviors.immutability_label, behaviors = behaviors,
            verifiers = mutables )
        _behaviors.record_behavior(
            cls, attributes_namer = attributes_namer,
            level = 'instances', basename = 'visibles',
            label = _behaviors.concealment_label, behaviors = behaviors,
            verifiers = visibles )

        @__.funct.wraps( original )
        def initialize(
            self: object, *posargs: __.typx.Any, **nomargs: __.typx.Any
        ) -> None:
            original( self, *posargs, **nomargs )
            behaviors_: set[ str ] = getattr( self, behaviors_name_m, set( ) )
            behaviors_.update( behaviors )
            setattr( self, behaviors_name_m, frozenset( behaviors_ ) )

        setattr( cls, initializer_name, initialize )
        cls.__init__ = initialize
        return cls

    return decorate


def produce_attributes_assignment_decorator(
    level: str,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    implementation_core: _nomina.AssignerCore,
) -> _nomina.Decorator:
    def decorate( cls: type[ _U ] ) -> type[ _U ]:
        assigner_name = attributes_namer( level, 'assigner' )
        extant = getattr( cls, assigner_name, None )
        original = getattr( cls, '__setattr__' )
        if extant is original: return cls

        @__.funct.wraps( original )
        def assign( self: object, name: str, value: __.typx.Any ) -> None:
            implementation_core(
                self,
                ligation = __.funct.partial( original, self ),
                attributes_namer = attributes_namer,
                error_class_provider = error_class_provider,
                level = level,
                name = name, value = value )

        setattr( cls, assigner_name, assign )
        cls.__setattr__ = assign
        return cls

    return decorate


def produce_attributes_deletion_decorator(
    level: str,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    implementation_core: _nomina.DeleterCore,
) -> _nomina.Decorator:
    def decorate( cls: type[ _U ] ) -> type[ _U ]:
        deleter_name = attributes_namer( level, 'deleter' )
        extant = getattr( cls, deleter_name, None )
        original = getattr( cls, '__delattr__' )
        if extant is original: return cls

        @__.funct.wraps( original )
        def delete( self: object, name: str ) -> None:
            implementation_core(
                self,
                ligation = __.funct.partial( original, self ),
                attributes_namer = attributes_namer,
                error_class_provider = error_class_provider,
                level = level,
                name = name )

        setattr( cls, deleter_name, delete )
        cls.__delattr__ = delete
        return cls

    return decorate


def produce_attributes_surveillance_decorator(
    level: str,
    attributes_namer: _nomina.AttributesNamer,
    implementation_core: _nomina.SurveyorCore,
) -> _nomina.Decorator:
    def decorate( cls: type[ _U ] ) -> type[ _U ]:
        surveyor_name = attributes_namer( level, 'surveyor' )
        extant = getattr( cls, surveyor_name, None )
        original = getattr( cls, '__dir__' )
        if extant is original: return cls

        @__.funct.wraps( original )
        def survey( self: object ) -> __.cabc.Iterable[ str ]:
            return implementation_core(
                self,
                ligation = __.funct.partial( original, self ),
                attributes_namer = attributes_namer,
                level = level )

        setattr( cls, surveyor_name, survey )
        cls.__dir__ = survey
        return cls

    return decorate


def produce_decorators_factory( # noqa: PLR0913
    level: str,
    attributes_namer: _nomina.AttributesNamer = __.calculate_attrname,
    error_class_provider: _nomina.ErrorClassProvider = __.provide_error_class,
    assigner_core: _nomina.AssignerCore = (
        _behaviors.assign_attribute_if_mutable ),
    deleter_core: _nomina.DeleterCore = (
        _behaviors.delete_attribute_if_mutable ),
    surveyor_core: _nomina.SurveyorCore = (
        _behaviors.survey_visible_attributes ),
) -> __.cabc.Callable[
    [
        _nomina.BehaviorExclusionVerifiersOmni,
        _nomina.BehaviorExclusionVerifiersOmni
    ],
    _nomina.Decorators
]:
    def produce(
        mutables: _nomina.BehaviorExclusionVerifiersOmni,
        visibles: _nomina.BehaviorExclusionVerifiersOmni,
    ) -> _nomina.Decorators:
        ''' Produces standard decorators. '''
        decorators: list[ _nomina.Decorator ] = [ ]
        decorators.append(
            produce_instances_initialization_decorator(
                attributes_namer = attributes_namer,
                mutables = mutables, visibles = visibles ) )
        if mutables != '*':
            decorators.append(
                produce_attributes_assignment_decorator(
                    level = level,
                    attributes_namer = attributes_namer,
                    error_class_provider = error_class_provider,
                    implementation_core = assigner_core ) )
            decorators.append(
                produce_attributes_deletion_decorator(
                    level = level,
                    attributes_namer = attributes_namer,
                    error_class_provider = error_class_provider,
                    implementation_core = deleter_core ) )
        if visibles != '*':
            decorators.append(
                produce_attributes_surveillance_decorator(
                    level = level,
                    attributes_namer = attributes_namer,
                    implementation_core = surveyor_core ) )
        return decorators

    return produce


def produce_decoration_preparers_factory(
    attributes_namer: _nomina.AttributesNamer = __.calculate_attrname,
    error_class_provider: _nomina.ErrorClassProvider = __.provide_error_class,
    class_preparer: __.typx.Optional[ _nomina.ClassPreparer ] = None,
) -> __.cabc.Callable[ [ ], _nomina.DecorationPreparers ]:
    def produce( ) -> _nomina.DecorationPreparers:
        ''' Produces processors for standard decorators. '''
        preprocessors: list[ _nomina.DecorationPreparer ] = [ ]
        if class_preparer is not None:
            preprocessors.append(
                __.funct.partial(
                    class_preparer,
                    attributes_namer = attributes_namer  ) )
        return tuple( preprocessors )

    return produce


class_factory_decorators = produce_class_factory_decorators( )


@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
def dataclass_with_standard_behaviors(
    decorators: _nomina.Decorators = ( ),
    mutables: _nomina.BehaviorExclusionVerifiersOmni = __.mutables_default,
    visibles: _nomina.BehaviorExclusionVerifiersOmni = __.visibles_default,
) -> _nomina.Decorator:
    # https://github.com/microsoft/pyright/discussions/10344
    ''' Dataclass decorator factory. '''
    decorators_factory = produce_decorators_factory( level = 'instances' )
    decorators_ = decorators_factory( mutables, visibles )
    preparers_factory = produce_decoration_preparers_factory(
        class_preparer = prepare_dataclass_for_instances )
    preparers = preparers_factory( )
    return decoration_by(
        *decorators, _dataclass_core, *decorators_, preparers = preparers )


def with_standard_behaviors(
    decorators: _nomina.Decorators = ( ),
    mutables: _nomina.BehaviorExclusionVerifiersOmni = __.mutables_default,
    visibles: _nomina.BehaviorExclusionVerifiersOmni = __.visibles_default,
) -> _nomina.Decorator:
    ''' Class decorator factory. '''
    decorators_factory = produce_decorators_factory( level = 'instances' )
    decorators_ = decorators_factory( mutables, visibles )
    preparers_factory = produce_decoration_preparers_factory( )
    preparers = preparers_factory( )
    return decoration_by( *decorators, *decorators_, preparers = preparers )
