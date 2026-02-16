# AIC vs Go

AIC targets first-try correctness from AI models with a mid-level, safe, compiled design. Go is a pragmatic, GC-managed systems language emphasizing simplicity and concurrency.

## Summary
- Runtime: both compile to native; AIC also targets WASM. Go uses tracing GC; AIC uses ARC with a small cycle breaker.
- Errors: AIC uses `Result<T,E>` and `?`; Go uses multi-return with `error` and `if err != nil`.
- Concurrency: AIC has `async/await`, tasks, structured concurrency, and channels; Go uses goroutines and channels.
- Effects: AIC statically checks `effects(io, net, fs, ...)`; Go has no built-in effect typing.
- Generics: AIC monomorphizes generics with trait bounds; Go has type parameters with constraints (since 1.18).
- Tooling: both enforce formatters (`aic fmt`, `gofmt`); AIC adds typed holes and machine-readable fix-its.

## When to Choose Which
- Choose AIC: strict typing, effect-checked IO/net, canonical runtime, machine-readable diagnostics for LLM workflows.
- Choose Go: simple deployment, large ecosystem, fast compile times, goroutine-first concurrency model.

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

Go (roughly equivalent)
```go
package client

import (
    "encoding/json"
    "fmt"
    "net/http"
)

type User struct { Id uint64 `json:"id"`; Name string `json:"name"` }

func FetchUser(id uint64) (User, error) {
    url := fmt.Sprintf("/users/%d", id)
    resp, err := http.Get(url)
    if err != nil { return User{}, err }
    defer resp.Body.Close()
    if resp.StatusCode != 200 { return User{}, fmt.Errorf("status %d", resp.StatusCode) }
    var u User
    if err := json.NewDecoder(resp.Body).Decode(&u); err != nil { return User{}, err }
    return u, nil
}
```

## Notable Differences
- Go’s goroutines favor fire-and-forget; AIC prefers structured task scopes and `await`.
- AIC’s effects prevent accidental network/filesystem in pure helpers.
- AIC forbids operator overloading and macros; Go similarly keeps the surface minimal.
