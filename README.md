# Roman Numeral Converter (C)

![C99](https://img.shields.io/badge/C-99-blue)
![Tested on Windows/Linux](https://img.shields.io/badge/Platforms-Windows%20%7C%20Linux-green)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Tests](https://img.shields.io/badge/Tests-4,053%20passing-brightgreen)

A fully validated Roman numeral conversion engine built to explore defensive C programming, algorithm design, and cross-platform reliability.

## Features

- **Two-way conversion**: Convert between Roman numerals and integers (1-3999)
  - **Roman → Integer**
  - **Integer → Roman**
- **Dual validation engines for roman validation**:
  - **Manual algorithm** (All platforms): Custom state-machine validator
  - **Regex-based** (Linux/Mac): POSIX-compliant alternative for comparison
- **Interactive CLI**: Simple menu-driven interface
- **Strict validation**: Detects complex edge cases
- **Cross-platform**: Fully compatible with Windows and Linux/Unix systems
- **Comprehensive testing**: 4,053 test cases with round-trip verification

## Requirements

- GCC-compatible C compiler
- Python 3.6+ (for automated tests and benchmarking)
- POSIX regex (Linux/Mac - for regex validator)

## Build & Run

### Compile:

```bash
gcc converter.c -o converter
```

### Run:

```bash
./converter
```

### Regex Mode (Linux/Mac):

```bash
./converter -regex
```

This mode uses the POSIX regex validator, included primarily for comparison
and benchmarking against the manual algorithm. It is not the default validator.

### Usage Examples

Roman → Integer

```bash
1) Roman to Int
2) Int to Roman
Q) Quit

Select an option: 1
Enter a Roman numeral or 'Q' to quit: MCMXCVIII
1998
Enter a Roman numeral or 'Q' to quit: MCMXCXVIII
MCMXCXVIII is not a valid Roman numeral.
```

Integer → Roman

```bash
1) Roman to Int
2) Int to Roman
Q) Quit

Select an option: 2
Enter a number up to 3999 or 'Q' to quit: 3888
MMMDCCCLXXXVIII
Enter a number up to 3999 or 'Q' to quit: 5000
Out of range (1-3999).
```

## Program Architecture

### Cross-Platform Validation

The program implements two validation approaches:

- **Primary:** Manual validator using state machine approach
- **Secondary:** POSIX regex (Unix systems only)

The regex validator is optional and exists only for comparison and benchmarking; the manual algorithm is the authoritative validator used on all platforms.

### Roman Validation Algorithm

The custom validator implements a state machine with multi-stage validation:

1. **Character & Format Validation:** Ensures input contains only valid Roman symbols and handles normalization safely.
2. **Repetition Rules Enforcement:** Uses state machine to track repeat counts and prevent illegal repetitions.
3. **Subtractive Notation Validation:** Validates only legal subtractive pairs.
4. **Structural Integrity Check:** Ensures proper descending order and blocks invalid patterns.
5. **Safe Conversion Process:** Converts the validated numeral to an integer using controlled pointer advancement to avoid partial or ambiguous parses.

### Performance Optimization

- **Theoretical:** O(n) where n is the numeral length
- **Practical:** O(1) - input size bounded by Roman numeral constraints
- Single-pass validation without backtracking
- Early rejection of invalid inputs

Benchmark results demonstrate the manual validator outperforms POSIX regex:

| Validator        | Average Time |
| ---------------- | ------------ |
| Manual Algorithm | 3.90s        |
| POSIX Regex      | 4.50s        |

### Input Safety

- `fgets()` with static buffers to prevent overflows
- `input_overflow_check()` detects and discards excess input
- Comprehensive input validation before processing

## Testing

- 4,053 test cases, including valid and invalid
- Round-trip verification
- Progress reporting and duration tracking

### Run tests

```bash
python test.py
```

### Example output:

```bash
Performing round-trip verification...
Progress: 3999/3999 ✅
Testing invalid Romans...
Progress: 46/46 ✅
Testing invalid Integers...
Progress: 8/8 ✅
Test duration: 11.64 seconds
Summary: 4053/4053 tests passed ✅
```

### Verbose mode

For detailed test output, use the `-verbose` or `-v` flag:

```bash
python test.py -v
```

Example verbose output:

```bash
✅ Test '1                   ' → Roman: I                                        | → Int: 1
✅ Test '2                   ' → Roman: II                                       | → Int: 2
✅ Test '3                   ' → Roman: III                                      | → Int: 3
✅ Test '4                   ' → Roman: IV                                       | → Int: 4
```

## Benchmarking

- Comparative performance testing
- Multiple iterations for more accurate data
- Performance delta reporting

### Run benchmark

```bash
python benchmark.py
```

### Example output:

```bash
Running benchmarks...
Run 1/5:
  Regex  1: 4.83s
  Manual 1: 3.90s
Run 2/5:
  Regex  2: 4.51s
  Manual 2: 3.95s
Run 3/5:
  Regex  3: 4.50s
  Manual 3: 3.85s
Run 4/5:
  Regex  4: 4.47s
  Manual 4: 3.89s
Run 5/5:
  Regex  5: 4.57s
  Manual 5: 3.82s

==================================================
BENCHMARK RESULTS
==================================================
Manual Validator: 3.88s average
Regex Validator:  4.58s average
Manual was 15.2% faster than Regex
Platform: Linux
Test: Int→Roman conversion (1-3999), 5 iterations
```

## Exit Codes

| Code | Name                 | Meaning                                             |
| ---- | -------------------- | --------------------------------------------------- |
| -1   | EXIT_PROGRAM         | User exited the program                             |
| 0    | EXIT_OK              | Success                                             |
| 1    | EXIT_INPUT_ERR       | fgets error                                         |
| 2    | EXIT_EMPTY_ERR       | Empty input                                         |
| 3    | EXIT_MALLOC_ERR      | Memory allocation error                             |
| 4    | EXIT_INVALID_INPUT   | Non numeric / non alphabetic input                  |
| 5    | EXIT_INVALID_NUMERAL | Input is valid but not a valid Roman / out of range |

## Project Structure

```
├── converter.c
├── test.py
├── benchmark.py
├── LICENSE
└── README.md
```

## Design Focus

This project is a demonstration of:

- Defensive programming and validation
- Modular algorithm design
- User-safe input handling in C
- Comprehensive testing via round-trip conversions

## License

MIT License - see LICENSE file for details.

---

**Author:** Daniel Landuche
