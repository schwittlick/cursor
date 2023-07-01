from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.parser import HPGLParser
from cursor.path import Path


def test_hpgl_parser_LB():
    file = DataDirHandler().test_data_file("file_to_parse.hpgl")
    parser = HPGLParser(file)
    paths = parser.parse()

    collection = Collection()
    collection.add(Path.from_tuple_list([(100.25, 2.0), (100.875, 2.0)]))
    collection.add(Path.from_tuple_list([(100.25, 1.375), (100.625, 1.0), (100.625, 2.0)]))

    assert paths == collection


def test_hpgl_parser_PA():
    file = DataDirHandler().test_data_file("hpgl_pa_pd_pu.hpgl")
    parser = HPGLParser(file)
    paths = parser.parse()

    collection = Collection()
    collection.add(Path.from_tuple_list([(100, 0), (100, 100)]))

    assert paths == collection
