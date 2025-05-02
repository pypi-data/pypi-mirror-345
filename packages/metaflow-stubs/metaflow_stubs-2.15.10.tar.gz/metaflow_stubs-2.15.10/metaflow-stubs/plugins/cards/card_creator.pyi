######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.10                                                                                #
# Generated on 2025-05-01T20:06:36.031560                                                            #
######################################################################################################

from __future__ import annotations


from ...metaflow_current import current as current

ASYNC_TIMEOUT: int

class CardProcessManager(object, metaclass=type):
    """
    This class is responsible for managing the card creation processes.
    """
    ...

class CardCreator(object, metaclass=type):
    def __init__(self, top_level_options):
        ...
    def create(self, card_uuid = None, user_set_card_id = None, runtime_card = False, decorator_attributes = None, card_options = None, logger = None, mode = 'render', final = False, sync = False):
        ...
    ...

