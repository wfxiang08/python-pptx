# encoding: utf-8

"""
Test suite for pptx.text.fonts module
"""

from __future__ import absolute_import, print_function

import pytest

from pptx.text.fonts import _Font, FontFiles, _HeadTable, _NameTable, _Stream

from ..unitutil.file import test_file_dir, testfile
from ..unitutil.mock import (
    call, class_mock, function_mock, initializer_mock, instance_mock,
    method_mock, open_mock, property_mock, var_mock
)


class DescribeFontFiles(object):

    def it_can_find_a_system_font_file(self, find_fixture):
        family_name, is_bold, is_italic, expected_path = find_fixture
        path = FontFiles.find(family_name, is_bold, is_italic)
        assert path == expected_path

    def it_catalogs_the_system_fonts_to_help_find(self, installed_fixture):
        expected_call_args, expected_values = installed_fixture
        installed_fonts = FontFiles._installed_fonts()
        assert FontFiles._iter_font_files_in.call_args_list == (
            expected_call_args
        )
        assert installed_fonts == expected_values

    def it_generates_font_dirs_to_help_find(self, font_dirs_fixture):
        expected_values = font_dirs_fixture
        font_dirs = FontFiles._font_directories()
        assert font_dirs == expected_values

    def it_knows_os_x_font_dirs_to_help_find(self, osx_dirs_fixture):
        expected_dirs = osx_dirs_fixture
        font_dirs = FontFiles._os_x_font_directories()
        print(font_dirs)
        print(expected_dirs)
        assert font_dirs == expected_dirs

    def it_iterates_over_fonts_in_dir_to_help_find(self, iter_fixture):
        directory, _Font_, expected_calls, expected_paths = iter_fixture
        paths = list(FontFiles._iter_font_files_in(directory))

        print(directory)

        assert _Font_.open.call_args_list == expected_calls
        assert paths == expected_paths

    # fixtures ---------------------------------------------

    @pytest.fixture(params=[
        ('Foobar',  False, False, 'foobar.ttf'),
        ('Foobar',  True,  False, 'foobarb.ttf'),
        ('Barfoo',  False, True,  'barfooi.ttf'),
    ])
    def find_fixture(self, request, _installed_fonts_):
        family_name, is_bold, is_italic, expected_path = request.param
        return family_name, is_bold, is_italic, expected_path

    @pytest.fixture(params=[
        ('darwin', ['a', 'b']),
        ('win32',  ['c', 'd']),
    ])
    def font_dirs_fixture(
            self, request, _os_x_font_directories_,
            _windows_font_directories_):
        platform, expected_dirs = request.param
        dirs_meth_mock = {
            'darwin': _os_x_font_directories_,
            'win32':  _windows_font_directories_,
        }[platform]
        sys_ = var_mock(request, 'pptx.text.fonts.sys')
        sys_.platform = platform
        dirs_meth_mock.return_value = expected_dirs
        return expected_dirs

    @pytest.fixture
    def installed_fixture(self, _iter_font_files_in_, _font_directories_):
        _font_directories_.return_value = ['d', 'd_2']
        _iter_font_files_in_.side_effect = [
            [(('A', True,  False), 'a.ttf')],
            [(('B', False, True),  'b.ttf')],
        ]
        expected_call_args = [call('d'), call('d_2')]
        expected_values = {
            ('A', True,  False): 'a.ttf',
            ('B', False, True):  'b.ttf',
        }
        return expected_call_args, expected_values

    @pytest.fixture
    def iter_fixture(self, _Font_):
        directory = test_file_dir
        font_file_path = testfile('calibriz.ttf')
        font = _Font_.open.return_value.__enter__.return_value
        font.family_name, font.is_bold, font.is_italic = 'Arial', True, True
        expected_calls = [call(font_file_path)]
        expected_paths = [(('Arial', True, True), font_file_path)]
        return directory, _Font_, expected_calls, expected_paths

    @pytest.fixture
    def osx_dirs_fixture(self, request):
        import os
        os_ = var_mock(request, 'pptx.text.fonts.os')
        os_.path = os.path
        os_.environ = {'HOME': '/Users/fbar'}
        return [
            '/Library/Fonts',
            '/Network/Library/Fonts',
            '/System/Library/Fonts',
            '/Users/fbar/Library/Fonts',
            '/Users/fbar/.fonts',
        ]

    # fixture components -----------------------------------

    @pytest.fixture
    def _Font_(self, request):
        return class_mock(request, 'pptx.text.fonts._Font')

    @pytest.fixture
    def _font_directories_(self, request):
        return method_mock(request, FontFiles, '_font_directories')

    @pytest.fixture
    def _installed_fonts_(self, request):
        _installed_fonts_ = method_mock(
            request, FontFiles, '_installed_fonts'
        )
        _installed_fonts_.return_value = {
            ('Foobar',  False, False): 'foobar.ttf',
            ('Foobar',  True,  False): 'foobarb.ttf',
            ('Barfoo',  False, True):  'barfooi.ttf',
        }
        return _installed_fonts_

    @pytest.fixture
    def _iter_font_files_in_(self, request):
        return method_mock(request, FontFiles, '_iter_font_files_in')

    @pytest.fixture
    def _os_x_font_directories_(self, request):
        return method_mock(request, FontFiles, '_os_x_font_directories')

    @pytest.fixture
    def _windows_font_directories_(self, request):
        return method_mock(request, FontFiles, '_windows_font_directories')


class Describe_Font(object):

    def it_can_construct_from_a_font_file_path(self, open_fixture):
        path, _Stream_, stream_ = open_fixture
        with _Font.open(path) as f:
            _Stream_.open.assert_called_once_with(path)
            assert isinstance(f, _Font)
        stream_.close.assert_called_once_with()

    def it_knows_its_family_name(self, family_fixture):
        font, expected_name = family_fixture
        family_name = font.family_name
        assert family_name == expected_name

    def it_provides_access_to_its_tables(self, tables_fixture):
        font, _TableFactory_, expected_calls, expected_tables = tables_fixture
        tables = font._tables
        assert _TableFactory_.call_args_list == expected_calls
        assert tables == expected_tables

    def it_generates_table_records_to_help_read_tables(self, iter_fixture):
        font, expected_values = iter_fixture
        values = list(font._iter_table_records())
        assert values == expected_values

    def it_knows_the_table_count_to_help_read(self, table_count_fixture):
        font, expected_value = table_count_fixture
        assert font._table_count == expected_value

    def it_reads_the_header_to_help_read_font(self, fields_fixture):
        font, expected_values = fields_fixture
        fields = font._fields
        font._stream.read_fields.assert_called_once_with('>4sHHHH', 0)
        assert fields == expected_values

    # fixtures ---------------------------------------------

    @pytest.fixture
    def family_fixture(self, _tables_, name_table_):
        font = _Font(None)
        expected_name = 'Foobar'
        _tables_.return_value = {'name': name_table_}
        name_table_.family_name = expected_name
        return font, expected_name

    @pytest.fixture
    def fields_fixture(self, read_fields_):
        stream = _Stream(None)
        font = _Font(stream)
        read_fields_.return_value = expected_values = ('foob', 42, 64, 7, 16)
        return font, expected_values

    @pytest.fixture
    def iter_fixture(self, _table_count_, stream_read_):
        stream = _Stream(None)
        font = _Font(stream)
        _table_count_.return_value = 2
        stream_read_.return_value = (
            'name' 'xxxx' '\x00\x00\x00\x2A' '\x00\x00\x00\x15'
            'head' 'xxxx' '\x00\x00\x00\x15' '\x00\x00\x00\x2A'
        )
        expected_values = [('name', 42, 21), ('head', 21, 42)]
        return font, expected_values

    @pytest.fixture
    def open_fixture(self, _Stream_):
        path = 'foobar.ttf'
        stream_ = _Stream_.open.return_value
        return path, _Stream_, stream_

    @pytest.fixture
    def tables_fixture(
            self, stream_, name_table_, head_table_, _iter_table_records_,
            _TableFactory_):
        font = _Font(stream_)
        _iter_table_records_.return_value = iter([
            ('name', 11, 22),
            ('head', 33, 44),
        ])
        _TableFactory_.side_effect = [name_table_, head_table_]

        expected_calls = [
            call('name', stream_, 11, 22),
            call('head', stream_, 33, 44),
        ]
        expected_tables = {
            'name': name_table_,
            'head': head_table_
        }
        return font, _TableFactory_, expected_calls, expected_tables

    @pytest.fixture
    def table_count_fixture(self, _fields_):
        font = _Font(None)
        _fields_.return_value = (-666, 42)
        expected_value = 42
        return font, expected_value

    # fixture components -----------------------------------

    @pytest.fixture
    def _fields_(self, request):
        return property_mock(request, _Font, '_fields')

    @pytest.fixture
    def head_table_(self, request):
        return instance_mock(request, _HeadTable)

    @pytest.fixture
    def _iter_table_records_(self, request):
        return method_mock(request, _Font, '_iter_table_records')

    @pytest.fixture
    def name_table_(self, request):
        return instance_mock(request, _NameTable)

    @pytest.fixture
    def read_fields_(self, request):
        return method_mock(request, _Stream, 'read_fields')

    @pytest.fixture
    def _Stream_(self, request):
        return class_mock(request, 'pptx.text.fonts._Stream')

    @pytest.fixture
    def stream_(self, request):
        return instance_mock(request, _Stream)

    @pytest.fixture
    def stream_read_(self, request):
        return method_mock(request, _Stream, 'read')

    @pytest.fixture
    def _TableFactory_(self, request):
        return function_mock(request, 'pptx.text.fonts._TableFactory')

    @pytest.fixture
    def _table_count_(self, request):
        return property_mock(request, _Font, '_table_count')

    @pytest.fixture
    def _tables_(self, request):
        return property_mock(request, _Font, '_tables')


class Describe_Stream(object):

    def it_can_construct_from_a_path(self, open_fixture):
        path, open_, _init_, file_ = open_fixture
        stream = _Stream.open(path)
        open_.assert_called_once_with(path, 'rb')
        _init_.assert_called_once_with(file_)
        assert isinstance(stream, _Stream)

    def it_can_be_closed(self, close_fixture):
        stream, file_ = close_fixture
        stream.close()
        file_.close.assert_called_once_with()

    # fixtures ---------------------------------------------

    @pytest.fixture
    def close_fixture(self, file_):
        stream = _Stream(file_)
        return stream, file_

    @pytest.fixture
    def open_fixture(self, open_, _init_):
        path = 'foobar.ttf'
        file_ = open_.return_value
        return path, open_, _init_, file_

    # fixture components -----------------------------------

    @pytest.fixture
    def file_(self, request):
        return instance_mock(request, file)

    @pytest.fixture
    def _init_(self, request):
        return initializer_mock(request, _Stream)

    @pytest.fixture
    def open_(self, request):
        return open_mock(request, 'pptx.text.fonts')
