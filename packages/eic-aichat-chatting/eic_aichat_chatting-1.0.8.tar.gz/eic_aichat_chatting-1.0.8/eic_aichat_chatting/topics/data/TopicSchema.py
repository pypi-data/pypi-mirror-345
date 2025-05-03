from pip_services4_commons.convert import TypeCode
from pip_services4_data.validate import ObjectSchema


class TopicSchema(ObjectSchema):
    def __init__(self):
        super().__init__()

        self.with_optional_property('id', TypeCode.String)
        self.with_required_property('site_id', TypeCode.String)
        self.with_optional_property('type', TypeCode.String)
        self.with_optional_property('name', TypeCode.String)
        self.with_optional_property('content', TypeCode.String)