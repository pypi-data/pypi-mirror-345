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


''' Standard classes and class factories. '''
# TODO? ClassMutable and ProtocolClassMutable
#       Need inheritance of omnimutability and omnivisibility.


from __future__ import annotations

from . import __
from . import decorators as _decorators


@_decorators.decoration_by( *_decorators.class_factory_decorators )
class Class( type ): pass


@_decorators.decoration_by( *_decorators.class_factory_decorators )
@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class Dataclass( type ): pass


@_decorators.decoration_by( *_decorators.class_factory_decorators )
@__.typx.dataclass_transform( kw_only_default = True )
class DataclassMutable( type ): pass


@_decorators.decoration_by( *_decorators.class_factory_decorators )
class ProtocolClass( type( __.typx.Protocol ) ): pass


@_decorators.decoration_by( *_decorators.class_factory_decorators )
@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class ProtocolDataclass( type( __.typx.Protocol ) ): pass


@_decorators.decoration_by( *_decorators.class_factory_decorators )
@__.typx.dataclass_transform( kw_only_default = True )
class ProtocolDataclassMutable( type( __.typx.Protocol ) ): pass


class Object( metaclass = Class ): pass


class ObjectMutable( # pyright: ignore[reportGeneralTypeIssues]
    metaclass = Class,
    instances_mutables = '*', # pyright: ignore[reportCallIssue]
): pass


class DataclassObject( metaclass = Dataclass ): pass


class DataclassObjectMutable( metaclass = DataclassMutable ): pass


class Protocol( __.typx.Protocol, metaclass = ProtocolClass ): pass


class ProtocolMutable( # pyright: ignore[reportGeneralTypeIssues]
    __.typx.Protocol,
    metaclass = ProtocolClass,
    instances_mutables = '*', # pyright: ignore[reportCallIssue]
): pass


class DataclassProtocol(
    __.typx.Protocol, metaclass = ProtocolDataclass,
): pass


class DataclassProtocolMutable(
    __.typx.Protocol, metaclass = ProtocolDataclassMutable,
): pass
