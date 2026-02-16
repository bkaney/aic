# AIC vs Java

AIC is a mid‑level compiled language with a small runtime and explicit errors. Java is a GC‑managed, VM‑hosted language with exceptions and a large standard ecosystem.

## Summary
- Runtime: AIC compiles to native/WASM with a tiny runtime; Java targets the JVM with JIT/GC.
- Memory: AIC uses ARC; Java uses tracing GC.
- Errors: AIC uses `Result<T,E>` + `?`; Java uses checked/unchecked exceptions.
- Generics: AIC monomorphizes generics (reified at codegen); Java erases types at runtime.
- Concurrency: AIC ships one canonical async runtime and channels; Java has threads, virtual threads (Loom), and many frameworks.

## When to Choose Which
- Choose AIC: small, fast CLIs/services with strict typing, deterministic builds, and strong LLM tooling.
- Choose Java: enterprise ecosystems, large frameworks, long‑running services needing JVM tooling and libraries.

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

Java (illustrative)
```java
record Config(String path) {}

Config readConfig(Path path) throws IOException {
  String data = Files.readString(path);
  Config conf = new Gson().fromJson(data, Config.class);
  return conf;
}
```

## Notable Differences
- Exceptions vs Results: AIC opts out of exceptions for predictability and simpler LLM‑authored control flow.
- Boilerplate: AIC aims for terse syntax; Java is improving (records, var), but remains more ceremonial.
- Packaging: AIC favors deterministic, static artifacts; Java’s JARs/wrappers add runtime dependencies.
