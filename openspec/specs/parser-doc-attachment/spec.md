## ADDED Requirements

### Requirement: Pending doc comment slot in dispatch loop
The dispatch loop SHALL maintain a `pending_doc` slot that is populated when a `DOC_COMMENT` token is encountered and cleared after each item is parsed.

#### Scenario: Doc comment before struct is stored in pending_doc
- **WHEN** the dispatch loop encounters a `DOC_COMMENT` token
- **THEN** it stores the `DocComment` node in `pending_doc` and does not immediately append it to `file.items`

#### Scenario: pending_doc cleared after each item
- **WHEN** an item parser completes and the node is appended to `file.items`
- **THEN** `pending_doc` is reset to `None` for the next iteration

### Requirement: Doc comment attached to following item
The `pending_doc` SHALL be passed into each item parser which SHALL assign it to the node's `doc` field so that the `DocComment` is accessible on the parsed declaration node.

#### Scenario: Doc comment attached to following struct
- **WHEN** a `DOC_COMMENT` token immediately precedes a `struct` declaration
- **THEN** the resulting `StructDecl` has `doc` set to the `DocComment` node

#### Scenario: Doc comment attached to following enum
- **WHEN** a `DOC_COMMENT` token immediately precedes an `enum` declaration
- **THEN** the resulting `EnumDecl` has `doc` set to the `DocComment` node

#### Scenario: Doc comment attached to following type alias
- **WHEN** a `DOC_COMMENT` token immediately precedes a `type` declaration
- **THEN** the resulting `TypeAlias` has `doc` set to the `DocComment` node

#### Scenario: Doc comment attached to following const
- **WHEN** a `DOC_COMMENT` token immediately precedes a `const` declaration
- **THEN** the resulting `ConstDecl` has `doc` set to the `DocComment` node

#### Scenario: Doc comment attached to following use declaration
- **WHEN** a `DOC_COMMENT` token immediately precedes a `use` declaration
- **THEN** the resulting `UseDecl` has `doc` set to the `DocComment` node

### Requirement: Declaration without preceding doc comment has doc=None
Each item parser SHALL set the node's `doc` field to `None` when no `pending_doc` is present.

#### Scenario: Struct without doc comment has doc=None
- **WHEN** a `struct` declaration is not preceded by a `DOC_COMMENT` token
- **THEN** the resulting `StructDecl` has `doc == None`

### Requirement: Consecutive doc comments retain only the last
If multiple consecutive `DOC_COMMENT` tokens appear before an item, the dispatch loop SHALL overwrite `pending_doc` with each new token, so only the last doc comment is attached.

#### Scenario: Last of multiple doc comments is attached
- **WHEN** two `DOC_COMMENT` tokens appear consecutively before a struct
- **THEN** the `StructDecl` has `doc` set to the second (last) `DocComment` node
