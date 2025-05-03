# -*- coding: utf-8 -*-
import json

import bottle
from pip_services4_commons.convert import TypeCode
from pip_services4_components.refer import Descriptor, IReferences
from pip_services4_data.validate import ObjectSchema
from pip_services4_http.controller import RestOperations, RestController
from pip_services4_components.context import Context

from aichatchatting.topics.data import Topic, TopicSchema
from aichatchatting.topics.logic.ITopicsService import ITopicsService


class TopicsOperations(RestOperations):
    def __init__(self):
        super().__init__()
        self._topics_service: ITopicsService = None
        self._dependency_resolver.put("topics-service", Descriptor('aichatchatting-topics', 'service', '*', '*', '1.0'))

    def configure(self, config):
        super().configure(config)

    def set_references(self, references: IReferences):
        super().set_references(references)
        self._topics_service = self._dependency_resolver.get_one_required('topics-service')

    def get_topics(self):
        context = Context.from_trace_id(self._get_trace_id())
        filter_params = self._get_filter_params()
        paging_params = self._get_paging_params()
        try:
            res = self._topics_service.get_topics(context, filter_params, paging_params)
            return self._send_result(res)
        except Exception as err:
            return self._send_error(err)

    def get_topic_by_id(self, id):
        context = Context.from_trace_id(self._get_trace_id())
        try:
            res = self._topics_service.get_topic_by_id(context, id)
            return self._send_result(res)
        except Exception as err:
            return self._send_error(err)

    def create_topic(self):
        context = Context.from_trace_id(self._get_trace_id())
        data = bottle.request.json
        topic = data if isinstance(data, dict) else json.loads(data)
        topic = None if not topic else Topic(**topic)
        try:
            res = self._topics_service.create_topic(context, topic)
            return self._send_result(res)
        except Exception as err:
            return self._send_error(err)

    def update_topic(self):
        context = Context.from_trace_id(self._get_trace_id())
        data = bottle.request.json
        topic = data if isinstance(data, dict) else json.loads(data)
        topic = None if not topic else Topic(**topic)
        try:
            res = self._topics_service.update_topic(context, topic)
            return self._send_result(res)
        except Exception as err:
            return self._send_error(err)

    def delete_topic_by_id(self, id):
        context = Context.from_trace_id(self._get_trace_id())
        try:
            res = self._topics_service.delete_topic_by_id(context, id)
            return self._send_result(res)
        except Exception as err:
            return self._send_error(err)

    def register_routes(self, controller: RestController):
        controller.register_route('get', '/topics', None,
                                  self.get_topics)

        controller.register_route('get', '/topics/<id>', ObjectSchema(True)
                                  .with_optional_property("topic_id", TypeCode.String),
                                  self.get_topic_by_id)

        controller.register_route('post', '/topics', ObjectSchema(True)
                                  .with_required_property("body", TopicSchema()),
                                  self.create_topic)

        controller.register_route('put', '/topics', ObjectSchema(True)
                                  .with_required_property("body", TopicSchema()),
                                  self.update_topic)

        controller.register_route('delete', '/topics/<id>', ObjectSchema(True)
                                  .with_required_property("topic_id", TypeCode.String),
                                  self.delete_topic_by_id)
