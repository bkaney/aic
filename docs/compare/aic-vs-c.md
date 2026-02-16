# AIC vs C

AIC aims for safe, productive development with predictable performance. C offers maximal control with manual memory and minimal runtime.

## Summary
- Safety: AIC is memory‑safe by default (ARC, no raw pointer arithmetic). C gives full control with high foot‑gun risk.
- Types: AIC has enums (tagged unions), generics, traits, and pattern matching. C uses structs/enums/macros without generics.
- Errors: AIC uses `Result<T,E>` with `?`; C uses return codes/errno or out params.
- Concurrency: AIC has async/await, tasks, channels. C uses threads/APIs (pthreads, OS primitives) and manual coordination.
- Tooling: AIC has enforced formatter, typed holes, machine‑readable diagnostics. C depends on external tooling and conventions.

## When to Choose Which
- Choose AIC: services, tools, and WASM modules with strong safety and fast iteration.
- Choose C: kernels, bare‑metal, or ultra‑tight embedded loops where every byte and cycle must be hand‑tuned.

## Example: Read + decode config

AIC
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

Notes
- In AIC, errors are explicit and bubble with `?`; resources are ARC‑managed.
- In C, the equivalent requires manual file IO, buffer management, JSON lib setup, and hand‑rolled error paths.
