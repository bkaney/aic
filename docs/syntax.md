# AIC Syntax and Semantics (Draft)

This document describes the surface syntax, core semantics, and formatting rules aimed at maximizing first‑try correctness from AI code generation.

## Lexical Structure
- Files are UTF‑8. Newline is `\n`.
- Whitespace is insignificant except inside string literals; indentation has no semantic meaning.
- Comments: `// line`, `/* block */`, `/// doc` (attached to the following item).
- Identifiers: `snake_case` for variables, fields; `CamelCase` for types/traits; `SCREAMING_SNAKE` for consts.
- Keywords (reserved): `module, use, pub, let, const, mut, fn, struct, enum, trait, impl, match, if, else, loop, for, in, break, continue, return, async, await, where, true, false, none, extern, effects`.
- Literals: integers (`0`, `42`, `0xFF`), floats (`1.0`, `2e5`), strings (`"..."`, `r"..."`), booleans (`true/false`), `none`.

## Formatting (Canonical)
- Enforced by `aic fmt` and `aic check`.
- Braces are mandatory for all blocks; K&R style: opening brace on same line.
- One statement per line; semicolons are required after statements.
  - MVP: required for unambiguous parsing and simpler fix‑its.
  - Post‑MVP: evaluate safe semicolon elision (newline termination) with benchmarks; keep grammar simple and avoid JS/Go‑style insertion pitfalls.
- 4 spaces per indentation level; no tabs.
- Trailing commas allowed in multi‑line lists.

## Terseness & Tokenization
- Short, common keywords to reduce token count and leverage model familiarity (`fn`, `let`, `pub`, `use`, `impl`, `trait`, `enum`, `match`, `async`, `await`).
- Compact formatting: no vertical alignment, minimal whitespace, no gratuitous parentheses.
- Prefer short stdlib module names and identifiers where clear (`io`, `net`, `fs`, `json`, `fmt`).
- Avoid duplicate calling styles (e.g., no named args) to reduce surface area.
- Open consideration (post‑MVP): potential aliases for particularly long keywords/types (e.g., `module`→`mod`, `string`→`str`) pending tokenizer/benchmark data; canonical spellings remain as specified for MVP.

## Modules and Imports
```aic
module http.client;
use std::net::http;
use std::json as json;

pub use http::Response; // re‑export
```
- One module per file; module path matches directory structure.
- `use` paths use `::` separators. Aliasing via `as`.
- Exports must be explicit with `pub` or `pub use`.
 - `module` and `use` lines are statements and require semicolons.

## Types
- Primitives: `bool, i32, i64, u32, u64, f32, f64, string, bytes`.
- Aggregates: `tuple` literals `(T1, T2)`, arrays `[T; N]`, slices `[]T`, maps `map[K, V]`.
- User types:
```aic
pub struct User {
    id: u64;
    name: string;
}

pub enum HttpErr {
    Status(u16);
    Decode(string);
    Net(string);
}

pub type UserId = u64;
```

## Generics and Where Clauses
```aic
pub fn max<T>(a: T, b: T) -> T where T: Ord {
    if a > b { return a; }
    return b;
}
```
- Monomorphized at compile time; no higher‑kinded types.
- `where` lists trait bounds on generic parameters.

## Traits and Implementations
```aic
pub trait ToJson { fn to_json(&self) -> string; }

impl ToJson for User {
    fn to_json(&self) -> string { json.encode(self) }
}
```
- No method or operator overloading beyond trait method sets.
- Methods take `self` explicitly; no implicit receivers.

## Variables and Bindings
```aic
let x: i32 = 5;
let y = 10; // local inference
let mut z: string = "hi";
z = z + "!";
```
- Shadowing is disallowed by default to reduce mistakes; use `shadow let x = ...` to shadow intentionally.

## Functions
```aic
pub fn add(a: i32, b: i32) -> i32 { return a + b; }

pub async fn fetch_user(id: u64) -> Result<User, HttpErr> effects(net) {
    let resp = await http.get("/users/{id}");
    if resp.status != 200 { return Err(HttpErr::Status(resp.status)); }
    let u: User = json.decode(resp.body).map_err(HttpErr::Decode)?;
    return Ok(u);
}
```
- Signature order: visibility, `async` flag, `fn`, name, generics, params, return type, `where` (optional), `effects(...)` (optional).
- Effects are a comma‑separated set of capabilities: `effects(io, net)`.

## Control Flow
```aic
if cond { ... } else { ... }

loop { if done { break; } }

for item in items { ... }
```
- `for` loops iterate over `IntoIter` trait; desugars to iterator protocol calls.

## Pattern Matching
```aic
match result {
    Ok(v) => print(v),
    Err(HttpErr::Status(s)) => log.warn("status", s),
    Err(e) => log.error("fetch_user", e),
};
```
- Matches on enums must be exhaustive. Use `_` to catch remaining cases.

## Error Handling
- `Result<T, E>` with `Ok(T)` and `Err(E)` variants.
- `?` operator propagates `Err(E)` early with the current return type.
- `map_err(F)` transforms errors; standard adapters available.

## Typed Holes and Incomplete Code
```aic
let name: string = _; // compiler: expected string; suggestions: from context

todo("parse headers") // warning: unreachable at runtime if executed
unimplemented()        // warning: not implemented
```
- Holes are allowed in expression and pattern positions; compiling yields diagnostics with expected types and suggestions.

## Operators and Precedence (low → high)
- Logical OR: `||`
- Logical AND: `&&`
- Comparisons: `== != < <= > >=`
- Add/Sub: `+ -`
- Mul/Div/Mod: `* / %`
- Unary: `! -`
- Member access and calls have highest precedence: `. () []`
- No user‑defined operators or overloading.

## Strings and Interpolation
- Basic strings: `"hello"`, raw strings: `r"{json}"` (no escapes processed).
- Interpolation uses format functions: `fmt::format("Hello {0}", name)` to avoid syntax surprises.

## Visibility and Access
- `pub` on types, functions, fields to export.
- Modules are closed by default; re‑exports via `pub use`.

## FFI and Extern
```aic
extern "C" {
    fn puts(msg: *const u8) -> i32;
}
```
- C ABI only in MVP; types are explicitly mapped.

## Collections and Iteration
```aic
let names: []string = vec!["a", "b"];
for n in names { print(n); }
```

## Example File
```aic
module app.main;
use std::io;
use std::json;

pub struct Config { path: string; }

pub fn read_config(path: string) -> Result<Config, IoErr> effects(io) {
    let data = io::read_to_string(path)?;
    let conf: Config = json::decode(data)?;
    return Ok(conf);
}
```

Notes:
- This document adopts `effects(...)` trailing clause (replacing the earlier inline `-> io Result<T>` strawman) for readability and grammar simplicity.
