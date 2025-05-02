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


''' Catalog of common type aliases. '''
# ruff: noqa: F403,F405


from __future__ import annotations

from . import __
from ..nomina import *


BehaviorExclusionNames: __.typx.TypeAlias = __.cabc.Set[ str ]
BehaviorExclusionNamesOmni: __.typx.TypeAlias = (
    BehaviorExclusionNames | __.typx.Literal[ '*' ] )
BehaviorExclusionPredicate: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str ], bool ] )
BehaviorExclusionPredicates: __.typx.TypeAlias = (
    __.cabc.Sequence[ BehaviorExclusionPredicate ] )
BehaviorExclusionRegex: __.typx.TypeAlias = __.re.Pattern[ str ]
BehaviorExclusionRegexes: __.typx.TypeAlias = (
    __.cabc.Sequence[ BehaviorExclusionRegex ] )
BehaviorExclusionVerifier: __.typx.TypeAlias = (
    str | BehaviorExclusionRegex | BehaviorExclusionPredicate )
BehaviorExclusionVerifiers: __.typx.TypeAlias = (
    __.cabc.Sequence[ BehaviorExclusionVerifier ] )
BehaviorExclusionVerifiersOmni: __.typx.TypeAlias = (
    BehaviorExclusionVerifiers | __.typx.Literal[ '*' ] )
ErrorClassProvider: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str ], type[ Exception ] ] )


class AssignerCore( __.typx.Protocol ):
    ''' Core implementation of attributes assigner. '''

    @staticmethod
    def __call__( # noqa: PLR0913 # pragma: no branch
        obj: object, /, *,
        ligation: AssignerLigation,
        attributes_namer: AttributesNamer,
        error_class_provider: ErrorClassProvider,
        level: str,
        name: str,
        value: __.typx.Any,
    ) -> None: raise NotImplementedError


class DeleterCore( __.typx.Protocol ):
    ''' Core implementation of attributes deleter. '''

    @staticmethod
    def __call__( # noqa: PLR0913 # pragma: no branch
        obj: object, /, *,
        ligation: DeleterLigation,
        attributes_namer: AttributesNamer,
        error_class_provider: ErrorClassProvider,
        level: str,
        name: str,
    ) -> None: raise NotImplementedError


class SurveyorCore( __.typx.Protocol ):
    ''' Core implementation of attributes surveyor. '''

    @staticmethod
    def __call__( # pragma: no branch
        obj: object, /, *,
        ligation: SurveyorLigation,
        attributes_namer: AttributesNamer,
        level: str,
    ) -> __.cabc.Iterable[ str ]: raise NotImplementedError


class ClassPreparer( __.typx.Protocol ):
    ''' Prepares class for decorator application. '''

    @staticmethod
    def __call__( # pragma: no branch
        class_: type,
        decorators: DecoratorsMutable, /, *,
        attributes_namer: AttributesNamer,
    ) -> None: raise NotImplementedError
