# AIC vs C# (.NET)

AIC is a mid-level compiled language with ARC and explicit `Result` errors. C# targets the .NET runtime with JIT/GC, exceptions, and a rich framework ecosystem.

## Summary
- Runtime: AIC compiles to native/WASM with a small runtime; C# targets .NET CLR with JIT and tracing GC.
- Memory: AIC uses ARC; C# uses GC.
- Errors: AIC uses `Result<T,E>` + `?`; C# uses exceptions and `Try*` patterns.
- Generics: AIC monomorphizes; C# generics are reified at runtime.
- Concurrency: Both have `async/await`; AIC ships one canonical runtime, C# integrates with TPL and a broad ecosystem.
- Effects: AIC statically checks `effects(io, net, fs, ...)`; C# has no built-in effect typing.

## When to Choose Which
- Choose AIC: small, static artifacts, strict typing, effect-checked IO/net, LLM-first tooling.
- Choose C#: desktop/mobile via .NET MAUI, enterprise stacks, deep framework integration, Windows ecosystem.

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

C# (illustrative)
```csharp
using System.Net.Http;
using System.Text.Json;

record User(ulong id, string name);

async Task<User> FetchUser(HttpClient http, ulong id) {
    var url = $"/users/{id}";
    var resp = await http.GetAsync(url);
    if (!resp.IsSuccessStatusCode)
        throw new HttpRequestException($"status {(int)resp.StatusCode}");
    var jsonText = await resp.Content.ReadAsStringAsync();
    var user = JsonSerializer.Deserialize<User>(jsonText)!;
    return user;
}
```

## Notable Differences
- Exceptions vs `Result`: AIC avoids exceptions for predictability and simpler LLM-authored control flow.
- Effects: AIC can forbid network/filesystem in selected scopes at compile time.
- Packaging: AIC favors static binaries/WASM; C# typically ships assemblies with a runtime (AOT options exist).
