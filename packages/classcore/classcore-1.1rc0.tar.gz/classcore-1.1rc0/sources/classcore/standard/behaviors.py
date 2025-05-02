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


''' Implementations for standard behaviors. '''
# TODO? Support introspection of PEP 593 annotations for behavior exclusions.
#       Maybe enum for mutability and visibility.


from __future__ import annotations

from .. import utilities as _utilities
from . import __
from . import nomina as _nomina


concealment_label = 'concealment'
immutability_label = 'immutability'


def assign_attribute_if_mutable( # noqa: PLR0913
    obj: object, /, *,
    ligation: _nomina.AssignerLigation,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    level: str,
    name: str,
    value: __.typx.Any,
) -> None:
    leveli = 'instance' if level == 'instances' else level
    behaviors_name = attributes_namer( leveli, 'behaviors' )
    behaviors = _utilities.getattr0( obj, behaviors_name, frozenset( ) )
    if immutability_label not in behaviors:
        ligation( name, value )
        return
    names_name = attributes_namer( level, 'mutables_names' )
    names: _nomina.BehaviorExclusionNamesOmni = (
        getattr( obj, names_name, frozenset( ) ) )
    if names == '*' or name in names:
        ligation( name, value )
        return
    predicates_name = attributes_namer( level, 'mutables_predicates' )
    predicates: _nomina.BehaviorExclusionPredicates = (
        getattr( obj, predicates_name, ( ) ) )
    for predicate in predicates:
        if predicate( name ):
            # TODO? Cache predicate hit.
            ligation( name, value )
            return
    regexes_name = attributes_namer( level, 'mutables_regexes' )
    regexes: _nomina.BehaviorExclusionRegexes = (
        getattr( obj, regexes_name, ( ) ) )
    for regex in regexes:
        if regex.fullmatch( name ):
            # TODO? Cache regex hit.
            ligation( name, value )
            return
    target = _utilities.describe_object( obj )
    raise error_class_provider( 'AttributeImmutability' )( name, target )


def delete_attribute_if_mutable( # noqa: PLR0913
    obj: object, /, *,
    ligation: _nomina.DeleterLigation,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    level: str,
    name: str,
) -> None:
    leveli = 'instance' if level == 'instances' else level
    behaviors_name = attributes_namer( leveli, 'behaviors' )
    behaviors = _utilities.getattr0( obj, behaviors_name, frozenset( ) )
    if immutability_label not in behaviors:
        ligation( name )
        return
    names_name = attributes_namer( level, 'mutables_names' )
    names: _nomina.BehaviorExclusionNamesOmni = (
        getattr( obj, names_name, frozenset( ) ) )
    if names == '*' or name in names:
        ligation( name )
        return
    predicates_name = attributes_namer( level, 'mutables_predicates' )
    predicates: _nomina.BehaviorExclusionPredicates = (
        getattr( obj, predicates_name, ( ) ) )
    for predicate in predicates:
        if predicate( name ):
            # TODO? Cache predicate hit.
            ligation( name )
            return
    regexes_name = attributes_namer( level, 'mutables_regexes' )
    regexes: _nomina.BehaviorExclusionRegexes = (
        getattr( obj, regexes_name, ( ) ) )
    for regex in regexes:
        if regex.fullmatch( name ):
            # TODO? Cache regex hit.
            ligation( name )
            return
    target = _utilities.describe_object( obj )
    raise error_class_provider( 'AttributeImmutability' )( name, target )


def survey_visible_attributes(
    obj: object, /, *,
    ligation: _nomina.SurveyorLigation,
    attributes_namer: _nomina.AttributesNamer,
    level: str,
) -> __.cabc.Iterable[ str ]:
    names_base = ligation( )
    leveli = 'instance' if level == 'instances' else level
    behaviors_name = attributes_namer( leveli, 'behaviors' )
    behaviors = _utilities.getattr0( obj, behaviors_name, frozenset( ) )
    if concealment_label not in behaviors: return names_base
    names_name = attributes_namer( level, 'visibles_names' )
    names: _nomina.BehaviorExclusionNamesOmni = (
        getattr( obj, names_name, frozenset( ) ) )
    if names == '*': return names_base # pragma: no branch
    regexes_name = attributes_namer( level, 'visibles_regexes' )
    regexes: _nomina.BehaviorExclusionRegexes = (
        getattr( obj, regexes_name, ( ) ) )
    predicates_name = attributes_namer( level, 'visibles_predicates' )
    predicates: _nomina.BehaviorExclusionPredicates = (
        getattr( obj, predicates_name, ( ) ) )
    names_: list[ str ] = [ ]
    for name in names_base:
        if name in names:
            names_.append( name )
            continue
        for predicate in predicates:
            if predicate( name ):
                # TODO? Cache predicate hit.
                names_.append( name )
                continue
        for regex in regexes:
            if regex.fullmatch( name ):
                # TODO? Cache regex hit.
                names_.append( name )
                continue
    return names_


def classify_behavior_exclusion_verifiers(
    verifiers: _nomina.BehaviorExclusionVerifiers
) -> tuple[
    _nomina.BehaviorExclusionNames,
    _nomina.BehaviorExclusionRegexes,
    _nomina.BehaviorExclusionPredicates,
]:
    names: set[ str ] = set( )
    regexes: list[ __.re.Pattern[ str ] ] = [ ]
    predicates: list[ __.cabc.Callable[ ..., bool ] ] = [ ]
    for verifier in verifiers:
        if isinstance( verifier, str ):
            names.add( verifier )
        elif isinstance( verifier, __.re.Pattern ):
            regexes.append( verifier )
        elif callable( verifier ):
            predicates.append( verifier )
        else:
            from ..exceptions import BehaviorExclusionInvalidity
            raise BehaviorExclusionInvalidity( verifier )
    return frozenset( names ), tuple( regexes ), tuple( predicates )


def produce_class_construction_preprocessor(
    attributes_namer: _nomina.AttributesNamer
) -> _nomina.ClassConstructionPreprocessor:

    def preprocess( # noqa: PLR0913
        clscls: type,
        name: str,
        bases: list[ type ],
        namespace: dict[ str, __.typx.Any ],
        arguments: dict[ str, __.typx.Any ],
        decorators: _nomina.DecoratorsMutable,
    ) -> None:
        record_class_construction_arguments(
            attributes_namer, namespace, arguments )

    return preprocess


def produce_class_construction_postprocessor(
    attributes_namer: _nomina.AttributesNamer
) -> _nomina.ClassConstructionPostprocessor:
    arguments_name = attributes_namer( 'class', 'construction_arguments' )

    def postprocess(
        cls: type, decorators: _nomina.DecoratorsMutable
    ) -> None:
        arguments = getattr( cls, arguments_name, { } )
        dcls_spec = getattr( cls, '__dataclass_transform__', None )
        if not dcls_spec: # either base class or metaclass may be marked
            clscls = type( cls )
            dcls_spec = getattr( clscls, '__dataclass_transform__', None )
        instances_mutables = arguments.get(
            'instances_mutables', __.mutables_default )
        instances_visibles = arguments.get(
            'instances_visibles', __.visibles_default )
        if dcls_spec and dcls_spec.get( 'kw_only_default', False ):
            from .decorators import dataclass_with_standard_behaviors
            decorator_factory = dataclass_with_standard_behaviors
            if not dcls_spec.get( 'frozen_default', True ):
                instances_mutables = instances_mutables or '*'
        else:
            from .decorators import with_standard_behaviors
            decorator_factory = with_standard_behaviors
        decorator = decorator_factory(
            mutables = instances_mutables, visibles = instances_visibles )
        decorators.append( decorator )

    return postprocess


def produce_class_initialization_completer(
    attributes_namer: _nomina.AttributesNamer
) -> _nomina.ClassInitializationCompleter:
    arguments_name = attributes_namer( 'class', 'construction_arguments' )

    def complete( cls: type ) -> None:
        arguments: __.typx.Optional[ dict[ str, __.typx.Any ] ] = (
            getattr( cls, arguments_name, None ) )
        if arguments is not None: delattr( cls, arguments_name )
        arguments = arguments or { }
        mutables = arguments.get( 'class_mutables', __.mutables_default )
        visibles = arguments.get( 'class_visibles', __.visibles_default )
        behaviors: set[ str ] = set( )
        record_behavior(
            cls, attributes_namer = attributes_namer,
            level = 'class', basename = 'mutables',
            label = immutability_label, behaviors = behaviors,
            verifiers = mutables )
        record_behavior(
            cls, attributes_namer = attributes_namer,
            level = 'class', basename = 'visibles',
            label = concealment_label, behaviors = behaviors,
            verifiers = visibles )
        # Set behaviors attribute last since it enables enforcement.
        behaviors_name = attributes_namer( 'class', 'behaviors' )
        _utilities.setattr0( cls, behaviors_name, frozenset( behaviors ) )

    return complete


def record_behavior( # noqa: PLR0913
    cls: type, /, *,
    attributes_namer: _nomina.AttributesNamer,
    level: str,
    basename: str,
    label: str,
    behaviors: set[ str ],
    verifiers: _nomina.BehaviorExclusionVerifiersOmni,
) -> None:
    names_name = attributes_namer( level, f"{basename}_names" )
    if verifiers == '*':
        setattr( cls, names_name, '*' )
        return
    names_omni: _nomina.BehaviorExclusionNamesOmni = (
        getattr( cls, names_name, frozenset( ) ) )
    if names_omni == '*': return
    names, regexes, predicates = (
        classify_behavior_exclusion_verifiers( verifiers ) )
    regexes_name = attributes_namer( level, f"{basename}_regexes" )
    predicates_name = attributes_namer( level, f"{basename}_predicates" )
    names_: _nomina.BehaviorExclusionNames = (
        frozenset( { *names, *names_omni } ) )
    regexes_: _nomina.BehaviorExclusionRegexes = (
        _deduplicate_merge_sequences(
            regexes, getattr( cls, regexes_name, ( ) ) ) )
    predicates_: _nomina.BehaviorExclusionPredicates = (
        _deduplicate_merge_sequences(
            predicates, getattr( cls, predicates_name, ( ) ) ) )
    setattr( cls, names_name, names_ )
    setattr( cls, regexes_name, regexes_ )
    setattr( cls, predicates_name, predicates_ )
    # TODO? Add regexes match cache.
    # TODO? Add predicates match cache.
    behaviors.add( label )


def record_class_construction_arguments(
    attributes_namer: _nomina.AttributesNamer,
    namespace: dict[ str, __.typx.Any ],
    arguments: dict[ str, __.typx.Any ],
) -> None:
    arguments_name = attributes_namer( 'class', 'construction_arguments' )
    arguments_ = namespace.get( arguments_name, { } )
    # Decorators, which replace classes, will cause construction of the
    # replacements without arguments. If we had previously recorded them in
    # the class namespace, then we do not want to clobber them.
    if arguments_: return
    arguments_ = { }
    for name in (
        'class_mutables', 'class_visibles',
        'instances_mutables', 'instances_visibles',
    ):
        if name not in arguments: continue
        arguments_[ name ] = arguments.pop( name )
    namespace[ arguments_name ] = arguments_


def _deduplicate_merge_sequences(
    addends: __.cabc.Sequence[ __.typx.Any ],
    augends: __.cabc.Sequence[ __.typx.Any ],
) -> __.cabc.Sequence[ __.typx.Any ]:
    result = list( augends )
    augends_ = set( augends )
    for addend in addends:
        if addend in augends_: continue
        result.append( addend )
    return tuple( result )
