import os
import pytest
from heavydb.connection import Connection
from heavydb._parsers import _extract_column_details

heavydb_host = os.environ.get('HEAVYDB_HOST', 'localhost')

@pytest.mark.usefixtures("heavydb_server")
class TestTableMetaData:
    def test_column_level_comments(self):
        c = Connection(
            user='admin',
            password='HyperInteractive',
            host=heavydb_host,
            dbname='heavyai')
        c.execute('drop table if exists meta_data_example')
        c.execute('create table meta_data_example (mint INTEGER)')
        c.execute('comment on column meta_data_example.mint is \'mint_comment\'')
        table_details = c._client.get_table_details(c._session, 'meta_data_example')
        column_details = _extract_column_details(table_details.row_desc)
        c.execute('drop table if exists meta_data_example')
        assert len(column_details) == 1
        assert column_details[0].comment == 'mint_comment' 


    def test_table_level_comments(self):
        c = Connection(
            user='admin',
            password='HyperInteractive',
            host=heavydb_host,
            dbname='heavyai')
        c.execute('drop table if exists meta_data_example')
        c.execute('create table meta_data_example (mint INTEGER)')
        c.execute('comment on table meta_data_example is \'table_comment\'')
        table_details = c._client.get_table_details(c._session, 'meta_data_example')
        c.execute('drop table if exists meta_data_example')
        assert table_details.comment == 'table_comment' 
