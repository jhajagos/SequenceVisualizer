import sqlalchemy as sa


class DBClass(object):
    """Base Class for DB access table in a schema"""
    def __init__(self, connection, meta_data):
        self.connection = connection
        self.meta_data = meta_data
        self.schema = meta_data.schema
        self.table_name = self._table_name()

        if self.schema is not None:
            self.table_name_with_schema = self.schema + "." + self.table_name
        else:
            self.table_name_with_schema = self.table_name

        self.table_obj = self.meta_data.tables[self.table_name_with_schema]

    def _table_name(self):
        return ""

    def insert_struct(self, data_struct):
        return self.connection.execute(self.table_obj.insert(data_struct).returning(self.table_obj.c.id)).fetchone()[0]

    def update_struct(self, row_id, update_dict):
        sql_expr = self.table_obj.update().where(self.table_obj.c.id == row_id).values(update_dict)
        self.connection.execute(sql_expr)

    def find_by_id(self, row_id):
        sql_expr = self.table_obj.select().where(self.table_obj.c.id == row_id)
        cursor = self.connection.execute(sql_expr)
        return list(cursor)[0]

    def find_one(self, value_string, field_name="name"):
        sql_expr = self.table_obj.select().where(self.table_obj.c[field_name] == value_string)
        cursor = self.connection.execute(sql_expr)

        result_list = list(cursor)
        if len(result_list):
            return result_list[0]
        else:
            return None

    def find_many(self, value_string, field_name="name"):
        sql_expr = self.table_obj.select().where(self.table_obj.c[field_name] == value_string)
        cursor = self.connection.execute(sql_expr)

        return list(cursor)

    def find_all(self):
        sql_expr = self.table_obj.select()
        cursor = self.connection.execute(sql_expr)

        return list(cursor)

    def find_by_sql(self, sql_query):
        return list(self.connection.execute(sql_query))

    def _find_by_name(self, name):
        find_expr = self.table_obj.select().where(self.table_obj.columns["name"] == name)
        cursor = self.connection.execute(find_expr)
        cursor_result = list(cursor)
        if len(cursor_result):
            return cursor_result[0]
        else:
            return None

    def get_columns_obj(self):
        table_obj = self.meta_data.tables[self.table_name_with_schema]
        return table_obj.columns

    def count(self):
        sql_obj = sa.select([sa.func.count()]).select_from(self.table_obj)
        return list(self.connection.execute(sql_obj))[0][0]

    def get_column_names(self):
        return [c.name for c in self.get_columns_obj()]


class DBClassName(DBClass):
    """Base class for working with table name"""

    def __init__(self, name, connection, meta_data, create_if_does_not_exists=True):

        self.connection = connection
        self.meta_data = meta_data
        self.schema = meta_data.schema
        self.table_name = self._table_name()
        self.name = name

        if self.schema is not None:
            self.table_name_with_schema = self.schema + "." + self.table_name
        else:
            self.table_name_with_schema = self.table_name

        self.table_obj = self.meta_data.tables[self.table_name_with_schema]

        self.name_obj = self._find_by_name(self.name)
        if self.name_obj is None and create_if_does_not_exists:
            self._insert_name(self.name)
            self.name_obj = self._find_by_name(self.name)

    def get_id(self):
        return self.name_obj.id

    def _insert_name(self, name):
        self.connection.execute(self.table_obj.insert({"name": name}))


class DBClassFactory(object):

    def __init__(self, connection, meta_data):

        self.connection = connection
        self.meta_data = meta_data
        self.name_class_dict = {}
        self.register_classes()

    def _name_class_pairs(self):
        return []

    def register_classes(self):

        for pair in self._name_class_pairs():
            class_name, class_ref = pair
            self.name_class_dict[class_name] = class_ref

    def create(self, class_name):
        return self.name_class_dict[class_name](self.connection, self.meta_data)