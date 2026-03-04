## ADDED Requirements

### Requirement: StructDecl node
`ast.py` SHALL define a `StructDecl` dataclass extending `Node` with fields: `name: str`, `fields: List[StructField]`, `doc: Optional[DocComment] = None`, `vis: bool = False`.

#### Scenario: StructDecl carries name and fields
- **WHEN** a `StructDecl` is constructed with a name and a list of `StructField` nodes
- **THEN** `node.name` returns the struct name and `node.fields` returns the field list

#### Scenario: StructDecl default visibility is private
- **WHEN** a `StructDecl` is constructed without specifying `vis`
- **THEN** `node.vis` is `False`

### Requirement: StructField node
`ast.py` SHALL define a `StructField` dataclass extending `Node` with fields: `name: str`, `type_: Type_`, `doc: Optional[DocComment] = None`.

#### Scenario: StructField carries name and type
- **WHEN** a `StructField` is constructed with a name and a type node
- **THEN** `field.name` and `field.type_` are accessible

### Requirement: EnumDecl node
`ast.py` SHALL define an `EnumDecl` dataclass extending `Node` with fields: `name: str`, `variants: List[EnumVariant]`, `doc: Optional[DocComment] = None`, `vis: bool = False`.

#### Scenario: EnumDecl carries variants
- **WHEN** an `EnumDecl` is constructed with a list of `EnumVariant` nodes
- **THEN** `node.variants` returns those variants in order

### Requirement: EnumVariant node
`ast.py` SHALL define an `EnumVariant` dataclass extending `Node` with fields: `name: str`, `fields: List[Type_]`, `doc: Optional[DocComment] = None`.

#### Scenario: Unit variant has empty fields list
- **WHEN** an `EnumVariant` is constructed with no `fields`
- **THEN** `variant.fields` is an empty list

#### Scenario: Tuple variant carries payload types
- **WHEN** an `EnumVariant` is constructed with one or more `Type_` nodes
- **THEN** `variant.fields` returns those types in order

### Requirement: TypeAlias node
`ast.py` SHALL define a `TypeAlias` dataclass extending `Node` with fields: `name: str`, `type_: Type_`, `doc: Optional[DocComment] = None`, `vis: bool = False`.

#### Scenario: TypeAlias stores name and aliased type
- **WHEN** a `TypeAlias` is constructed
- **THEN** `node.name` and `node.type_` are accessible

### Requirement: ConstDecl node
`ast.py` SHALL define a `ConstDecl` dataclass extending `Node` with fields: `name: str`, `type_: Type_`, `value: Expr`, `doc: Optional[DocComment] = None`, `vis: bool = False`.

#### Scenario: ConstDecl carries type annotation and initializer
- **WHEN** a `ConstDecl` is constructed
- **THEN** `node.type_` and `node.value` are accessible

### Requirement: LetStmt node
`ast.py` SHALL define a `LetStmt` dataclass extending `Node` with fields: `name: str`, `mut: bool`, `type_: Optional[Type_]`, `value: Optional[Expr]`.

#### Scenario: LetStmt default is immutable
- **WHEN** a `LetStmt` is constructed without specifying `mut`
- **THEN** `node.mut` is `False`

#### Scenario: LetStmt type annotation is optional
- **WHEN** a `LetStmt` is constructed without a `type_`
- **THEN** `node.type_` is `None`

### Requirement: Type_ union alias covers all type-position node kinds
`ast.py` SHALL define `Type_ = Union[IdentType, PathType, TupleType, ArrayType]` and expose it at module level.

#### Scenario: Type_ alias is importable from ast module
- **WHEN** a caller does `from aiclang.ast import Type_`
- **THEN** no `ImportError` is raised

### Requirement: IdentType and PathType nodes
`ast.py` SHALL define `IdentType(Node, name: str)` for single-segment type names and `PathType(Node, segments: List[str])` for qualified type paths.

#### Scenario: IdentType for simple type name
- **WHEN** an `IdentType` is constructed with `name="i32"`
- **THEN** `node.name` is `"i32"`

#### Scenario: PathType for multi-segment type
- **WHEN** a `PathType` is constructed with `segments=["std", "io", "Result"]`
- **THEN** `node.segments` has three elements

### Requirement: TupleType and ArrayType nodes
`ast.py` SHALL define `TupleType(Node, elements: List[Type_])` and `ArrayType(Node, element: Type_)`.

#### Scenario: TupleType stores element types
- **WHEN** a `TupleType` is constructed with two element types
- **THEN** `node.elements` has length 2

#### Scenario: ArrayType stores element type
- **WHEN** an `ArrayType` is constructed
- **THEN** `node.element` is accessible
