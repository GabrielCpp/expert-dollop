from sqlalchemy import and_


class ExactMatchFilter:
    def __init__(self, table):
        self.table = table

    def __call__(self, query, mapper):
        fields = mapper.map(query, dict)
        where_filter = ExactMatchFilter.build_and_column_filter(self.table, fields)
        return where_filter

    @staticmethod
    def build_and_column_filter(table, fields: dict):
        condition = None

        for column_name, value in fields.items():
            if condition is None:
                condition = getattr(table.c, column_name) == value
            else:
                condition = and_(condition, getattr(table.c, column_name) == value)

        return condition
