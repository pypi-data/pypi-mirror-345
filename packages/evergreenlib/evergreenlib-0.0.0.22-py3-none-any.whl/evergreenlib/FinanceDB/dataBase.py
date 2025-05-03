import pandas as pd
import psycopg2
from psycopg2 import sql
import yaml
import os


class DatabaseClient:
    def __init__(self, config_path=None):
        if config_path is None:
            user_home = os.path.expanduser("~")
            config_path = os.path.join(user_home, "db_config.yaml")

        with open(config_path, 'r', encoding='utf-8') as f:
            self.db_config = yaml.safe_load(f)

    def _map_dtype(self, dtype):
        """Маппинг типов pandas на типы PostgreSQL."""
        if pd.api.types.is_float_dtype(dtype):
            return 'NUMERIC'
        elif pd.api.types.is_integer_dtype(dtype):
            return 'INTEGER'
        elif pd.api.types.is_bool_dtype(dtype):
            return 'BOOLEAN'
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return 'TIMESTAMP'
        elif dtype == 'object':
            return 'VARCHAR'
        else:
            return 'BYTEA'

    def save_df_to_db(self, df, table_name, binary_columns=None):
        """
        Сохраняет DataFrame в PostgreSQL с автоматическим созданием таблицы.

        :param df: DataFrame для сохранения.
        :param table_name: Название таблицы в БД.
        :param binary_columns: Список колонок, содержащих бинарные данные.
        """
        if binary_columns is None:
            binary_columns = []

        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        # Формируем запрос на создание таблицы с корректными типами
        columns_with_types = ', '.join(
            f'{sql.Identifier(col).as_string(conn)} BYTEA' if col in binary_columns
            else f'{sql.Identifier(col).as_string(conn)} {self._map_dtype(dtype)}'
            for col, dtype in zip(df.columns, df.dtypes)
        )

        create_table_query = sql.SQL("CREATE TABLE IF NOT EXISTS {table} ({fields})").format(
            table=sql.Identifier(table_name),
            fields=sql.SQL(columns_with_types)
        )

        cursor.execute(create_table_query)
        conn.commit()

        insert_query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
            table=sql.Identifier(table_name),
            fields=sql.SQL(', ').join(map(sql.Identifier, df.columns)),
            values=sql.SQL(', ').join(sql.Placeholder() * len(df.columns))
        )

        for _, row in df.iterrows():
            data = [psycopg2.Binary(row[col]) if col in binary_columns else row[col] for col in df.columns]
            cursor.execute(insert_query, data)

        conn.commit()

        cursor.close()
        conn.close()

        print(f"Данные успешно загружены в таблицу '{table_name}'")
