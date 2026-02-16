# AIC vs Python

AIC is a compiled, mid-level language optimized for first-try correctness and predictable performance. Python is a dynamic, interpreted language optimized for expressiveness and ecosystem breadth.

## Summary
- Runtime: AIC compiles to native/WASM; Python runs on interpreters/VMs (CPython, PyPy, etc.).
- Types: AIC has nominal types, enums, traits, monomorphized generics; Python is dynamically typed with optional type hints (mypy, Pyright).
- Errors: AIC uses `Result<T,E>` + `?`; Python uses exceptions.
- Concurrency: AIC has `async/await`, tasks, channels; Python has `asyncio` with an event loop and a GIL for threads.
- Memory: AIC uses ARC; Python uses refcount + cycle GC.
- Tooling: AIC enforces formatting and offers typed holes + fix-its; Python relies on black/ruff/mypy conventions.

## When to Choose Which
- Choose AIC: deterministic binaries/WASM, strict typing, effect-checked IO/net, faster cold-start and lower footprint for services/CLIs.
- Choose Python: rapid prototyping, data science/ML ecosystems, scripting, glue code.

## Example: HTTP fetch + JSON decode

AIC
```aic
module http.client;
use std::net::http;
use std::json as json;
use std::fmt as fmt;

pub struct User { id: u64; name: string; }

pub enum HttpErr { Status(u16); Decode(string); Net(string); }

pub async fn fetch_user(id: u64) -> Result<User, HttpErr> effects(net) {
    let url = fmt::format("/users/{0}", id);
    let resp = await http.get(url);
    if resp.status != 200 { return Err(HttpErr::Status(resp.status)); }
    let u: User = json.decode(resp.body).map_err(HttpErr::Decode)?;
    return Ok(u);
}
```

Python (async, illustrative)
```py
from dataclasses import dataclass
import aiohttp, json

@dataclass
class User:
    id: int
    name: str

async def fetch_user(id: int) -> User:
    url = f"/users/{id}"
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            if resp.status != 200:
                raise RuntimeError(f"status {resp.status}")
            data = await resp.text()
            obj = json.loads(data)
            return User(**obj)
```

## Notable Differences
- Python’s exceptions vs AIC’s `Result` lead to different control-flow patterns; AIC favors explicit propagation with `?`.
- AIC’s effects system can statically forbid network/filesystem access in pure helpers.
- Interop: AIC can export WASM or C ABI; Python interop typically uses C-extensions, cffi, or FFI bridges.
