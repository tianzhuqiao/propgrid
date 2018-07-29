# https://github.com/ActiveState/code/blob/master/recipes/Python/305271_Enumerated_values_name_or/LICENSE.md
# Originally published: 2004-09-13 16:10:21
# Last updated: 2004-09-13 16:10:21
# Author: Samuel Reynolds
#
# This enumerated-values class is intended for use in module-level constants,
# such as an employee type or a status value. It allows simple attribute
# notation (e.g., employee.Type.Serf or employee.Type.CEO), but also supports
# simple bidirectional mapping using dictionary notation (e.g.,
# employee.Type['CEO']-->1 or employee.Type[1]-->'CEO').

# Copyright 2004 Samuel Reynolds
#
# The software is licensed according to the terms of the PSF (Python Software
# Foundation) license found here: http://www.python.org/psf/license/

class EnumType( object ):
    """
    Enumerated-values class.

    Allows reference to enumerated values by name
    or by index (i.e., bidirectional mapping).
    """
    def __init__( self, *names ):
        # Remember names list for reference by index
        self._names = list(names)
        # Attributes for direct reference
        for _i, _s in enumerate( self._names ):
            setattr( self, _s, _i )

    def __contains__( self, item ):
        try:
            trans = self[item]
            return True
        except:
            return False

    def __iter__( self ):
        return enumerate( self._names )

    def __getitem__( self, key ):
        if type(key) == type(0):
            return self._names[key]
        else:
            return self._nameToEnum( key )

    def __len__( self ):
        return len(self._names)

    def items( self ):
        return [ (idx, self._names[idx])
                for idx in range(0, len(self._names) ) ]


    def names( self ):
        return self._names[:]


    def _nameToEnum( self, name ):
        try:
            return getattr( self, name )
        except ValueError as exc:
            args = list(exc.args)
            args.append( "Unknown enum value name '%s'" % name )
            args = tuple(args)
            exc.args = args
            raise

