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


''' Various utilities for class manipulation. '''


from __future__ import annotations

from . import __


def describe_object( obj: object ) -> str:
    if __.inspect.isclass( obj ):
        return "class '{}'".format( qualify_class_name( obj ) )
    # TODO? functions, methods, etc...
    return "instance of {}".format( describe_object( type( obj ) ) )


def getattr0( obj: object, name: str, default: __.typx.Any ) -> __.typx.Any:
    ''' Returns private attribute from object.

        Uses mangled attribute which is unique to the class.
    '''
    name_m = mangle_name( obj, name )
    return getattr( obj, name_m, default )


def delattr0( obj: object, name: str ) -> None:
    ''' Deletes private attribute on object.

        Uses mangled attribute which is unique to the class.
    '''
    name_m = mangle_name( obj, name )
    delattr( obj, name_m )


def setattr0( obj: object, name: str, value: __.typx.Any ) -> None:
    ''' Assigns private attribute to object.

        Uses mangled attribute which is unique to the class.
    '''
    name_m = mangle_name( obj, name )
    setattr( obj, name_m, value )


def mangle_name( obj: object, name: str ) -> str:
    ''' Mangles attribute name so that it is unique.

        Effectively provides name of private member attribute,
        which is unique across class inheritance.
    '''
    if not __.inspect.isclass( obj ):
        return mangle_name( type( obj ), name )
    namehash = __.hashlib.sha256( )
    namehash.update( qualify_class_name( obj ).encode( ) )
    namehash_hex = namehash.hexdigest( )
    return f"{name}_{namehash_hex}"


def qualify_class_name( cls: type ) -> str:
    return f"{cls.__module__}.{cls.__qualname__}"


def repair_class_reproduction( original: type, reproduction: type ) -> None:
    ''' Repairs a class reproduction, if necessary. '''
    match __.platform.python_implementation( ):
        case 'CPython':  # pragma: no branch
            _repair_cpython_class_closures( original, reproduction )
        case _: pass  # pragma: no cover


def _repair_cpython_class_closures(
    original: type, reproduction: type
) -> None:
    # Adapted from https://github.com/python/cpython/pull/124455/files
    def try_repair_closure(
        function: __.cabc.Callable[ ..., __.typx.Any ]
    ) -> bool:
        try: index = function.__code__.co_freevars.index( '__class__' )
        except ValueError: return False
        if not function.__closure__: return False # pragma: no branch
        closure = function.__closure__[ index ]
        if original is closure.cell_contents: # pragma: no branch
            closure.cell_contents = reproduction
            return True
        return False # pragma: no cover

    for attribute in reproduction.__dict__.values( ):
        attribute_ = __.inspect.unwrap( attribute )
        if (    __.inspect.isfunction( attribute_ )
            and try_repair_closure( attribute_ )
        ): return
        if isinstance( attribute_, property ):
            for aname in ( 'fget', 'fset', 'fdel' ):
                accessor = getattr( attribute_, aname )
                if None is accessor: continue
                if try_repair_closure( accessor ): return
