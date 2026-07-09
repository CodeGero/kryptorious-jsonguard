# jsonguard

> Validate, format, and lint JSON — including real JSON Schema validation.

[![PyPI](https://img.shields.io/pypi/v/kryptorious-jsonguard)](https://pypi.org/project/kryptorious-jsonguard/) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Part of the [Kryptorious developer toolkit](https://kryptorious.gumroad.com/l/jbvet) — 31 open-source tools, one $9 lifetime license.

## Install

```bash
pip install kryptorious-jsonguard
```

## Quickstart

```bash
printf '{"name":"x","age":"bad"}\n' > data.json
printf '{"type":"object","properties":{"name":{"type":"string"},"age":{"type":"integer"}},"required":["name"]}\n' > schema.json
jsonguard check data.json --schema schema.json
# -> ✗ Schema mismatch: 'bad' is not of type 'integer'
```

## Commands

| Command | Description |
|---------|-------------|
| `jsonguard check data.json` | Validate syntax and structure. |
| `jsonguard check data.json --schema schema.json` | Validate against a JSON Schema (requires `jsonschema`). |
| `jsonguard format data.json -o pretty.json` | Pretty-print and format. |
| `jsonguard view data.json` | Pretty-print JSON to the terminal. |



## License

MIT — free for personal and commercial use. The $9 lifetime license adds DevFlow Premium (multi-environment CI/CD, approval gates, infrastructure-as-code). Get it at [kryptorious.gumroad.com/l/jbvet](https://kryptorious.gumroad.com/l/jbvet).
