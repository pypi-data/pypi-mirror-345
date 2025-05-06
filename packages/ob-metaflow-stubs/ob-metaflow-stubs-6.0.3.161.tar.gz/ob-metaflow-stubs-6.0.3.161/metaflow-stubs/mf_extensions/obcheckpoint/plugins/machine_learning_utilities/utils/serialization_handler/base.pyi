######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.10.1+obcheckpoint(0.2.1);ob(v1)                                                   #
# Generated on 2025-05-05T20:26:16.796551                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import typing


class SerializationHandler(object, metaclass=type):
    def serialze(self, *args, **kwargs) -> typing.Union[str, bytes]:
        ...
    def deserialize(self, *args, **kwargs) -> typing.Any:
        ...
    ...

