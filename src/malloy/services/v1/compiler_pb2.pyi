from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ThirdPartyRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ThirdPartyResponse(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class CompileRequest(_message.Message):
    __slots__ = ["type", "mode", "document", "references", "schema", "sql_block_schemas", "query", "named_query", "query_result"]
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        COMPILE: _ClassVar[CompileRequest.Type]
        REFERENCES: _ClassVar[CompileRequest.Type]
        TABLE_SCHEMAS: _ClassVar[CompileRequest.Type]
        SQL_BLOCK_SCHEMAS: _ClassVar[CompileRequest.Type]
        RESULTS: _ClassVar[CompileRequest.Type]
    COMPILE: CompileRequest.Type
    REFERENCES: CompileRequest.Type
    TABLE_SCHEMAS: CompileRequest.Type
    SQL_BLOCK_SCHEMAS: CompileRequest.Type
    RESULTS: CompileRequest.Type
    class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        COMPILE_AND_RENDER: _ClassVar[CompileRequest.Mode]
        COMPILE_ONLY: _ClassVar[CompileRequest.Mode]
    COMPILE_AND_RENDER: CompileRequest.Mode
    COMPILE_ONLY: CompileRequest.Mode
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_FIELD_NUMBER: _ClassVar[int]
    REFERENCES_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SQL_BLOCK_SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    NAMED_QUERY_FIELD_NUMBER: _ClassVar[int]
    QUERY_RESULT_FIELD_NUMBER: _ClassVar[int]
    type: CompileRequest.Type
    mode: CompileRequest.Mode
    document: CompileDocument
    references: _containers.RepeatedCompositeFieldContainer[CompileDocument]
    schema: str
    sql_block_schemas: _containers.RepeatedCompositeFieldContainer[SqlBlockSchema]
    query: str
    named_query: str
    query_result: QueryResult
    def __init__(self, type: _Optional[_Union[CompileRequest.Type, str]] = ..., mode: _Optional[_Union[CompileRequest.Mode, str]] = ..., document: _Optional[_Union[CompileDocument, _Mapping]] = ..., references: _Optional[_Iterable[_Union[CompileDocument, _Mapping]]] = ..., schema: _Optional[str] = ..., sql_block_schemas: _Optional[_Iterable[_Union[SqlBlockSchema, _Mapping]]] = ..., query: _Optional[str] = ..., named_query: _Optional[str] = ..., query_result: _Optional[_Union[QueryResult, _Mapping]] = ...) -> None: ...

class QueryResult(_message.Message):
    __slots__ = ["data", "total_rows"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROWS_FIELD_NUMBER: _ClassVar[int]
    data: str
    total_rows: int
    def __init__(self, data: _Optional[str] = ..., total_rows: _Optional[int] = ...) -> None: ...

class CompileResponse(_message.Message):
    __slots__ = ["model", "sql"]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    SQL_FIELD_NUMBER: _ClassVar[int]
    model: str
    sql: str
    def __init__(self, model: _Optional[str] = ..., sql: _Optional[str] = ...) -> None: ...

class CompileDocument(_message.Message):
    __slots__ = ["url", "content"]
    URL_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    url: str
    content: str
    def __init__(self, url: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class TableSchema(_message.Message):
    __slots__ = ["key", "connection", "table"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    key: str
    connection: str
    table: str
    def __init__(self, key: _Optional[str] = ..., connection: _Optional[str] = ..., table: _Optional[str] = ...) -> None: ...

class CompilerRequest(_message.Message):
    __slots__ = ["type", "import_urls", "table_schemas", "sql_block", "connection", "render_content", "problems", "content"]
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        UNKNOWN: _ClassVar[CompilerRequest.Type]
        IMPORT: _ClassVar[CompilerRequest.Type]
        TABLE_SCHEMAS: _ClassVar[CompilerRequest.Type]
        SQL_BLOCK_SCHEMAS: _ClassVar[CompilerRequest.Type]
        COMPLETE: _ClassVar[CompilerRequest.Type]
        ERROR: _ClassVar[CompilerRequest.Type]
        RUN: _ClassVar[CompilerRequest.Type]
    UNKNOWN: CompilerRequest.Type
    IMPORT: CompilerRequest.Type
    TABLE_SCHEMAS: CompilerRequest.Type
    SQL_BLOCK_SCHEMAS: CompilerRequest.Type
    COMPLETE: CompilerRequest.Type
    ERROR: CompilerRequest.Type
    RUN: CompilerRequest.Type
    TYPE_FIELD_NUMBER: _ClassVar[int]
    IMPORT_URLS_FIELD_NUMBER: _ClassVar[int]
    TABLE_SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    SQL_BLOCK_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    RENDER_CONTENT_FIELD_NUMBER: _ClassVar[int]
    PROBLEMS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    type: CompilerRequest.Type
    import_urls: _containers.RepeatedScalarFieldContainer[str]
    table_schemas: _containers.RepeatedCompositeFieldContainer[TableSchema]
    sql_block: SqlBlock
    connection: str
    render_content: str
    problems: _containers.RepeatedScalarFieldContainer[str]
    content: str
    def __init__(self, type: _Optional[_Union[CompilerRequest.Type, str]] = ..., import_urls: _Optional[_Iterable[str]] = ..., table_schemas: _Optional[_Iterable[_Union[TableSchema, _Mapping]]] = ..., sql_block: _Optional[_Union[SqlBlock, _Mapping]] = ..., connection: _Optional[str] = ..., render_content: _Optional[str] = ..., problems: _Optional[_Iterable[str]] = ..., content: _Optional[str] = ...) -> None: ...

class SqlBlock(_message.Message):
    __slots__ = ["name", "sql", "connection"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SQL_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    sql: str
    connection: str
    def __init__(self, name: _Optional[str] = ..., sql: _Optional[str] = ..., connection: _Optional[str] = ...) -> None: ...

class SqlBlockSchema(_message.Message):
    __slots__ = ["name", "sql", "schema"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SQL_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    name: str
    sql: str
    schema: str
    def __init__(self, name: _Optional[str] = ..., sql: _Optional[str] = ..., schema: _Optional[str] = ...) -> None: ...
