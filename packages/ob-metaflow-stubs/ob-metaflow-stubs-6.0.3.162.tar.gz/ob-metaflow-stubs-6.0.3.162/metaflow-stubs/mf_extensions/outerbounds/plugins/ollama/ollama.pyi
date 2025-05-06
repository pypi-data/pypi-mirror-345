######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.10.1+obcheckpoint(0.2.1);ob(v1)                                                   #
# Generated on 2025-05-05T21:26:32.662630                                                            #
######################################################################################################

from __future__ import annotations



class ProcessStatus(object, metaclass=type):
    ...

class OllamaManager(object, metaclass=type):
    """
    A process manager for Ollama runtimes.
    This is run locally, e.g., whether @ollama has a local, remote, or managed backend.
    """
    def __init__(self, models, backend = 'local', debug = False):
        ...
    def terminate_models(self):
        """
        Terminate all processes gracefully.
        First, stop model processes using 'ollama stop <model>'.
        Then, shut down the API server process.
        """
        ...
    ...

