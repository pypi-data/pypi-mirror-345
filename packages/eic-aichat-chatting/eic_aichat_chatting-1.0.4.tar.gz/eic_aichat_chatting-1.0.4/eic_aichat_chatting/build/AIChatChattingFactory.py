# -*- coding: utf-8 -*-
from pip_services4_components.refer import Descriptor
from pip_services4_components.build import Factory

from eic_aichat_chatting.topics.logic.TopicsService import TopicsService
from eic_aichat_chatting.topics.persistence.TopicsMemoryPersistence import TopicsMemoryPersistence
from eic_aichat_chatting.topics.persistence.TopicsMongoDbPersistence import TopicsMongoDbPersistence
from eic_aichat_chatting.chatprocessor.logic.BasicService import BasicService


class AIChatChattingFactory(Factory):
    __MemoryPersistenceDescriptor = Descriptor('aichatchatting-topics', 'persistence', 'memory', '*', '1.0')
    __MongoDbPersistenceDescriptor = Descriptor('aichatchatting-topics', 'persistence', 'mongodb', '*', '1.0')
    __ServiceDescriptor = Descriptor('aichatchatting-topics', 'service', 'default', '*', '1.0')

    __ChatprocessorServiceDescriptor = Descriptor("aichatchatting-chatprocessor", "service", "*", "*", "1.0")


    def __init__(self):
        super().__init__()

        self.register_as_type(self.__MemoryPersistenceDescriptor, TopicsMemoryPersistence)
        self.register_as_type(self.__MongoDbPersistenceDescriptor, TopicsMongoDbPersistence)
        self.register_as_type(self.__ServiceDescriptor, TopicsService)

        self.register_as_type(self.__ChatprocessorServiceDescriptor, BasicService)
