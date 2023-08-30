from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CompileDocument(_message.Message):
    __slots__ = ["content", "url"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    content: str
    url: str
    def __init__(self, url: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class CompileRequest(_message.Message):
    __slots__ = ["document", "mode", "named_query", "query", "query_result", "references", "schema", "sql_block_schemas", "type"]
    class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    COMPILE: CompileRequest.Type
    COMPILE_AND_RENDER: CompileRequest.Mode
    COMPILE_ONLY: CompileRequest.Mode
    DOCUMENT_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    NAMED_QUERY_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    QUERY_RESULT_FIELD_NUMBER: _ClassVar[int]
    REFERENCES: CompileRequest.Type
    REFERENCES_FIELD_NUMBER: _ClassVar[int]
    RESULTS: CompileRequest.Type
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SQL_BLOCK_SCHEMAS: CompileRequest.Type
    SQL_BLOCK_SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    TABLE_SCHEMAS: CompileRequest.Type
    TYPE_FIELD_NUMBER: _ClassVar[int]
    document: CompileDocument
    mode: CompileRequest.Mode
    named_query: str
    query: str
    query_result: QueryResult
    references: _containers.RepeatedCompositeFieldContainer[CompileDocument]
    schema: str
    sql_block_schemas: _containers.RepeatedCompositeFieldContainer[SqlBlockSchema]
    type: CompileRequest.Type
    def __init__(self, type: _Optional[_Union[CompileRequest.Type, str]] = ..., mode: _Optional[_Union[CompileRequest.Mode, str]] = ..., document: _Optional[_Union[CompileDocument, _Mapping]] = ..., references: _Optional[_Iterable[_Union[CompileDocument, _Mapping]]] = ..., schema: _Optional[str] = ..., sql_block_schemas: _Optional[_Iterable[_Union[SqlBlockSchema, _Mapping]]] = ..., query: _Optional[str] = ..., named_query: _Optional[str] = ..., query_result: _Optional[_Union[QueryResult, _Mapping]] = ...) -> None: ...

class CompileResponse(_message.Message):
    __slots__ = ["model", "sql"]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    SQL_FIELD_NUMBER: _ClassVar[int]
    model: str
    sql: str
    def __init__(self, model: _Optional[str] = ..., sql: _Optional[str] = ...) -> None: ...

class CompilerRequest(_message.Message):
    __slots__ = ["connection", "content", "import_urls", "render_content", "sql_block", "table_schemas", "type"]
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    COMPLETE: CompilerRequest.Type
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ERROR: CompilerRequest.Type
    IMPORT: CompilerRequest.Type
    IMPORT_URLS_FIELD_NUMBER: _ClassVar[int]
    RENDER_CONTENT_FIELD_NUMBER: _ClassVar[int]
    RUN: CompilerRequest.Type
    SQL_BLOCK_FIELD_NUMBER: _ClassVar[int]
    SQL_BLOCK_SCHEMAS: CompilerRequest.Type
    TABLE_SCHEMAS: CompilerRequest.Type
    TABLE_SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN: CompilerRequest.Type
    connection: str
    content: str
    import_urls: _containers.RepeatedScalarFieldContainer[str]
    render_content: str
    sql_block: SqlBlock
    table_schemas: _containers.RepeatedCompositeFieldContainer[TableSchema]
    type: CompilerRequest.Type
    def __init__(self, type: _Optional[_Union[CompilerRequest.Type, str]] = ..., import_urls: _Optional[_Iterable[str]] = ..., table_schemas: _Optional[_Iterable[_Union[TableSchema, _Mapping]]] = ..., sql_block: _Optional[_Union[SqlBlock, _Mapping]] = ..., connection: _Optional[str] = ..., render_content: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class QueryResult(_message.Message):
    __slots__ = ["data", "total_rows"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROWS_FIELD_NUMBER: _ClassVar[int]
    data: str
    total_rows: int
    def __init__(self, data: _Optional[str] = ..., total_rows: _Optional[int] = ...) -> None: ...

class SqlBlock(_message.Message):
    __slots__ = ["connection", "name", "sql"]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SQL_FIELD_NUMBER: _ClassVar[int]
    connection: str
    name: str
    sql: str
    def __init__(self, name: _Optional[str] = ..., sql: _Optional[str] = ..., connection: _Optional[str] = ...) -> None: ...

class SqlBlockSchema(_message.Message):
    __slots__ = ["name", "schema", "sql"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SQL_FIELD_NUMBER: _ClassVar[int]
    name: str
    schema: str
    sql: str
    def __init__(self, name: _Optional[str] = ..., sql: _Optional[str] = ..., schema: _Optional[str] = ...) -> None: ...

class TableSchema(_message.Message):
    __slots__ = ["connection", "key", "table"]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    connection: str
    key: str
    table: str
    def __init__(self, key: _Optional[str] = ..., connection: _Optional[str] = ..., table: _Optional[str] = ...) -> None: ...

class ThirdPartyRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ThirdPartyResponse(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...
