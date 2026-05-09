<h1 align="center">PeriphForge</h1>

<p align="center">
  A Python CLI tool that reads a peripheral config file (JSON) and generates C header boilerplate using Jinja2 templating.
</p>

<p align="center">
  <a href="#introduction">Introduction</a> •
  <a href="#usage">Usage</a> •
  <a href="#build">Build</a> •
  <a href="#project-progress">Project Progress</a> •
  <a href="#what-ive-learned">What I've Learned</a>
</p>

---

## Introduction

PeriphForge was built to learn core Python tooling — file I/O, data validation, templating,
and CLI design — in a practical embedded-systems context.

The tool takes a JSON peripheral definition (register map, base address, config) and produces
a `.h` header file from a Jinja2 template. The pipeline is: config in → validate → render → C code out.

Built with:

- **Pydantic** — validates the config and rejects badly formed input before anything renders
- **Jinja2** — templates the C header output
- **Click** — wraps everything in a proper CLI with flags, help text, and clean error messages

---

## Usage

### Basic

```bash
periforge inputs/uart.json
```

### Full options

```bash
periforge inputs/uart.json --template UART_periph_template.h.jinja --output output/UART0.h --verbose
```

### All flags

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--template` | `-t` | `UART_periph_template.h.jinja` | Jinja2 template filename |
| `--template-dir` | `-d` | `templates/` | Directory containing templates |
| `--output` | `-o` | `output/out.h` | Output `.h` file path |
| `--verbose` | `-v` | off | Print config details during generation |
| `--help` | | | Show usage and exit |

### Example input (`inputs/uart.json`)

```json
{
    "name": "UART0",
    "base_address": 1073750016,
    "size": 256,
    "enabled": true,
    "registers": [
        { "offset": 0,  "name": "CR"  },
        { "offset": 4,  "name": "SR"  },
        { "offset": 8,  "name": "DR"  },
        { "offset": 12, "name": "BRR" }
    ]
}
```

### Example output (`output/UART0.h`)

```c
#ifndef UART0_H
#define UART0_H

#include <stdint.h>

#define UART0_BASE    1073750016

/* Register Offsets */
#define UART0_CR     0
#define UART0_SR     4
#define UART0_DR     8
#define UART0_BRR    12

/* Declarations / Function Prototypes */
void UART0_init(void);
void UART0_open(void);
void UART0_close(void);
void UART0_write(uint8_t data);
uint8_t UART0_read(void);

typedef struct {
    uint32_t baud_rate;
    uint8_t  data_len;
    int8_t   UART_PARITY   : 1;
    int8_t   UART_STOP_BIT : 1;
} uart_comm_sett_t;

typedef enum {
    UART_INIT,
    UART_OPEN,
    UART_CLOSE,
    UART_READ,
    UART_WRITE
} uart_handle_t;

#endif /* UART0_H */
```

---

## Build

### Requirements

- Python 3.11+
- pip

### Dependencies

| Package | Purpose |
|---------|---------|
| `pydantic` | Config validation |
| `jinja2` | C header templating |
| `click` | CLI interface |

### Setup

#### 1. Clone the repository

```bash
git clone https://github.com/LewisNA14/PeriphForge.git
cd PeriphForge
```

#### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate    # Linux / macOS
.venv\Scripts\activate       # Windows
```

#### 3. Install dependencies and the CLI

```bash
pip install -r requirements.txt
pip install -e .
```

The `-e .` installs PeriphForge as an editable package, making the `periforge` command
available anywhere inside the virtual environment.

#### 4. Run the tool

```bash
periforge inputs/uart.json --output output/UART0.h --verbose
```

---

## Project Progress

| # | Milestone | Status |
|---|-----------|--------|
| 1 | Read a JSON file and print its contents | ✅ Done |
| 2 | Add Pydantic validation to reject badly formed input | ✅ Done |
| 3 | Understand what a peripheral header should look like | ✅ Done |
| 4 | Create a peripheral header based on what you've learnt | ✅ Done |
| 5 | Write a Jinja2 template that produces a C header file | ✅ Done |
| 6 | Connect them — config in, C code out | ✅ Done |
| 7 | Wrap it in a Click CLI | ✅ Done |
| 8 | Push to GitHub with a proper README | ✅ Done |

### Planned / Stretch Goals

- YAML config support alongside JSON
- Support for multiple peripheral types (GPIO, SPI, I2C)
- Pydantic Logfire observability integration

---

## What I've Learned

### Part 1 — JSON File I/O

- Reading and parsing JSON files using Python's built-in `json` module
- Python file handling with `with open(...) as f` and why it matters (automatic close on error)

---

### Part 2 — Pydantic Validation

**What is Pydantic?**

Pydantic is a data validation library for Python. You define a model — a class describing
the expected shape and types of your data — and Pydantic validates any incoming data
against it automatically.

```python
from pydantic import BaseModel, Field

class Register(BaseModel):
    offset: int = Field(ge=0)
    name: str = Field(pattern="^[A-Za-z_][A-Za-z0-9_]*$")

class Peripheral(BaseModel):
    name: str = Field(pattern="^[A-Za-z_][A-Za-z0-9_]*$")
    base_address: int
    size: int
    enabled: bool
    registers: list[Register]
```

Calling `Peripheral(**data)` raises a `ValidationError` with a clear message if anything
is missing, the wrong type, or fails a constraint.

**Key things learned:**

- Nested Pydantic models for structured data
- Python class definition order — a class must be defined before it can be referenced
- Using `Field(pattern=...)` to enforce valid C identifiers via regex
- The difference between `ge=0` (≥ 0) and `gt=0` (> 0) — relevant for register offsets,
  which can legitimately start at 0

**Valid vs Invalid JSON:**

```json
// ❌ Bad — common mistakes
{
    name: "UART0",               // keys must be quoted
    "base_address": 0x40002000,  // hex literals not valid in JSON
    "enabled": True,             // must be lowercase true
    "registers": [
        {"offset": 0, "name": "CR",}  // trailing comma
    ]
}
```

```json
// ✅ Good
{
    "name": "UART0",
    "base_address": 1073750016,
    "size": 256,
    "enabled": true,
    "registers": [
        {"offset": 0, "name": "CR"}
    ]
}
```

---

### Part 3 — Jinja2 Templating

**What is Jinja2?**

Jinja2 is a templating engine for Python. You write a template file with placeholders,
then render it by passing in a Python object — Jinja2 fills in the values.

```jinja
#ifndef {{ peripheral.name | upper }}_H
#define {{ peripheral.name | upper }}_H

{%- for register in peripheral.registers %}
#define {{ peripheral.name | upper }}_{{ register.name }}    {{ register.offset }}
{%- endfor %}
```

**Key things learned:**

- `{{ variable }}` for output, `{% %}` for logic (loops, conditionals)
- Jinja2 filters like `| upper` to transform values inline
- `FileSystemLoader` to load templates from a directory rather than inline strings
- Separating template files from Python logic — the template knows nothing about Python,
  Python knows nothing about C syntax

---

### Part 4 — Click CLI

**What is Click?**

Click is a Python library for building CLI tools. Instead of `argparse` or `sys.argv`,
you decorate functions — the function becomes the command.

```python
@click.command()
@click.argument("config", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", default="output/out.h")
@click.option("--verbose", "-v", is_flag=True)
def generate(config, output, verbose):
    """Generate a C peripheral header from a JSON config file."""
    ...
```

**Key things learned:**

- The difference between `@click.argument` (positional, required) and `@click.option` (named flag, optional)
- `click.Path(exists=True)` validates the file exists before your code runs
- `click.ClickException` for clean error messages — Click handles formatting and exit codes
- `click.secho` for coloured terminal output
- Separating CLI concerns from core logic — `generate()` only wires inputs to functions;
  the actual work happens in `load_config()`, `render_template()`, and `write_output()`
- Packaging with `pyproject.toml` and `pip install -e .` to install a real terminal command