# AIC vs Rust

This comparison highlights how AIC differs from Rust with an AI‑first, mid‑level focus.

## Summary
- Positioning: AIC is mid‑level, safe, compiled; Rust is systems‑level, zero‑cost.
- Authoring: AIC favors first‑try compilation (simpler surface, typed holes, canonical runtime). Rust favors ultimate control (lifetimes, borrow checker, many runtimes).
- Performance: Rust typically wins peak perf; AIC aims for predictable, fast iteration and sufficient perf.

## Key Differences
- Memory: AIC uses ARC + small cycle breaker; no lifetimes or borrows. Rust uses ownership/borrows with compile‑time checks.
- Effects: AIC has `effects(io, net, fs, ...)` on functions with static checking. Rust has no built‑in effect typing.
- Surface: No macros, no operator overloading, explicit imports, shadowing off by default, required semicolons.
- Concurrency: AIC includes one canonical async runtime and channels. Rust requires choosing a runtime (Tokio/async‑std/etc.).
- Diagnostics: AIC has typed holes (`_`), machine‑readable fix‑its, and format‑or‑fail. Rust has excellent diagnostics but no typed holes.
- Modules: AIC enforces one module per file; path must match file; explicit `module path.name;`.

## When to Choose Which
- Choose AIC: services, CLIs, data transforms, WASM apps, concurrent workers where developer speed and LLM‑authored code reliability matter.
- Choose Rust: kernels/embedded/real‑time or tight loops where ARC overhead is unacceptable, or when macros/advanced traits are needed.

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

Rust (roughly equivalent)
```rust
use reqwest; use serde::Deserialize;

#[derive(Deserialize)]
struct User { id: u64, name: String }

enum HttpErr { Status(u16), Decode(String), Net(String) }

async fn fetch_user(id: u64) -> Result<User, HttpErr> {
    let url = format!("/users/{}", id);
    let resp = reqwest::get(&url).await.map_err(|e| HttpErr::Net(e.to_string()))?;
    if resp.status() != 200 { return Err(HttpErr::Status(resp.status().as_u16())); }
    let u: User = resp.json().await.map_err(|e| HttpErr::Decode(e.to_string()))?;
    Ok(u)
}
```
