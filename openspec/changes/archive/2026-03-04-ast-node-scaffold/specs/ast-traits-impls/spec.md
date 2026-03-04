## ADDED Requirements

### Requirement: TraitDecl node
`ast.py` SHALL define a `TraitDecl` dataclass extending `Node` with fields: `name: str`, `methods: List[FnItem]`, `doc: Optional[DocComment] = None`, `vis: bool = False`.

#### Scenario: TraitDecl carries method signatures
- **WHEN** a `TraitDecl` is constructed with a list of `FnItem` nodes
- **THEN** `node.methods` returns those nodes in order

#### Scenario: TraitDecl default is private
- **WHEN** a `TraitDecl` is constructed without `vis`
- **THEN** `node.vis` is `False`

### Requirement: ImplBlock node
`ast.py` SHALL define an `ImplBlock` dataclass extending `Node` with fields: `trait_: Optional[str]`, `type_: Type_`, `methods: List[FnItem]`, `doc: Optional[DocComment] = None`.

#### Scenario: Inherent impl has no trait
- **WHEN** an `ImplBlock` is constructed with `trait_=None`
- **THEN** `node.trait_` is `None`

#### Scenario: Trait impl carries trait name
- **WHEN** an `ImplBlock` is constructed with `trait_="Display"`
- **THEN** `node.trait_` is `"Display"`

#### Scenario: ImplBlock carries method implementations
- **WHEN** an `ImplBlock` is constructed with a list of `FnItem` nodes
- **THEN** `node.methods` returns those nodes

### Requirement: Item union alias includes TraitDecl and ImplBlock
`ast.py` SHALL include `TraitDecl` and `ImplBlock` in the `Item` union alias, alongside `StructDecl`, `EnumDecl`, `TypeAlias`, `ConstDecl`, `FnItem`, `UseDecl`, and `ModuleDecl`.

#### Scenario: Item alias is importable from ast module
- **WHEN** a caller does `from aiclang.ast import Item`
- **THEN** no `ImportError` is raised

#### Scenario: TraitDecl is a valid Item
- **WHEN** a `TraitDecl` instance is assigned to a variable typed as `Item`
- **THEN** static type checkers accept it without error

### Requirement: File.items replaces File.uses and File.docs
`ast.py` SHALL update `File` so that it has `items: List[Item]` in place of the former `uses: List[UseDecl]` and `docs: List[DocComment]` fields. `File.module: Optional[ModuleDecl]` SHALL remain.

#### Scenario: File stores items in source order
- **WHEN** a `File` is constructed with a mixed list of `UseDecl`, `FnItem`, and `StructDecl` nodes
- **THEN** `file.items` preserves that order

#### Scenario: File.module is separate from items
- **WHEN** a `File` is constructed with a `ModuleDecl` and a list of items
- **THEN** `file.module` holds the `ModuleDecl` and `file.items` holds the remaining declarations
