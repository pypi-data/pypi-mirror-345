# -*- coding: utf-8 -*-
import json

import bottle
from pip_services4_commons.convert import TypeCode
from pip_services4_components.refer import Descriptor, IReferences
from pip_services4_data.validate import ObjectSchema
from pip_services4_http.controller import RestOperations, RestController
from pip_services4_components.context import Context

from eic_aichat_chatting.chatprocessor.logic.IBasicService import IBasicService
from eic_aichat_chatting.chatprocessor.data import RequestV1, RequestV1Schema
from eic_aichat_chatting.topics.data import Topic, TopicSchema
from eic_aichat_chatting.topics.logic.ITopicsService import ITopicsService
from eic_aichat_users.partialfacade.operations.version1.Authorize import AuthorizerV1


class ChattingOperations(RestOperations):
    def __init__(self):
        super().__init__()
        self.chatprocessor: IBasicService = None
        self._topics_service: ITopicsService = None
        self._dependency_resolver.put("aichatchatting-chatprocessor", Descriptor('aichatchatting-chatprocessor', 'service', '*', '*', '1.0'))
        self._dependency_resolver.put("topics-service", Descriptor('aichatchatting-topics', 'service', '*', '*', '1.0'))

    def configure(self, config):
        super().configure(config)

    def set_references(self, references: IReferences):
        super().set_references(references)
        self.chatprocessor = self._dependency_resolver.get_one_required('aichatchatting-chatprocessor')
        self._topics_service = self._dependency_resolver.get_one_required('topics-service')

    def process_prompt(self):

        # TODO user verification and other work with sessions
        context = Context.from_trace_id(self._get_trace_id())
        data = bottle.request.json
        request = data if isinstance(data, dict) else json.dumps(data)
        request = None if not request else RequestV1(**request)

        try:
            result = self.chatprocessor.handle_model_request(context, request)
            return self._send_result(result)
        except Exception as err:
            return self._send_error(err)

    def register_routes(self, controller: RestController, auth: AuthorizerV1):
        controller.register_route_with_auth('post', '/prompt', 
                                  ObjectSchema(True)
                                  .with_required_property("body", RequestV1Schema()), 
                                  auth.signed,
                                  self.process_prompt)
