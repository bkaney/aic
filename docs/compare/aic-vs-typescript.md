# AIC vs TypeScript

AIC is a compiled, mid‑level language optimized for first‑try correctness from AI models. TypeScript is a gradually‑typed superset of JavaScript targeting JS runtimes.

## Summary
- Runtime: AIC compiles to native/WASM; TS runs on JS engines (Node/Browser/Deno).
- Types: AIC has nominal types, enums, traits, monomorphized generics; TS has structural types, unions/intersections, and erasure at runtime.
- Errors: AIC uses `Result<T,E>` and `?`; TS uses exceptions/promises.
- Concurrency: Both use `async/await`; AIC ships one canonical runtime, effects are statically checked.
- Memory: AIC uses ARC; TS/JS uses tracing GC.

## When to Choose Which
- Choose AIC: predictable builds, static binaries/WASM modules, strict typing, effect‑checked IO/net, machine‑readable diagnostics and fix‑its for LLM workflows.
- Choose TS: browser apps, rich JS ecosystems, dynamic metaprogramming, rapid UI prototyping.

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

TypeScript
```ts
type User = { id: number; name: string };

export async function fetchUser(id: number): Promise<User> {
  const resp = await fetch(`/users/${id}`);
  if (resp.status !== 200) throw new Error(`status ${resp.status}`);
  const u = (await resp.json()) as User;
  return u;
}
```

## Notable Differences
- No macros in AIC (use functions like `fmt::format`), avoiding multiple metaprogramming styles.
- No implicit preludes: imports are explicit; modules are one per file with `module path.name;`.
- Effects in AIC prevent accidental network/filesystem in pure functions.
