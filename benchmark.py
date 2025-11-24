"""
Roman Numeral Converter — Benchmark Tool

Measures performance of:
- Manual validator 
- Regex-based validator (Unix only)

Process:
1. Builds Roman samples (1–3999) if needed
2. Runs repeated conversions (Roman → Integer)
3. Averages execution time across N iterations

Usage:
    python benchmark.py           # Run benchmark
    python benchmark.py -r        # Rebuild binary and regenerate romans.json

Author: Daniel Landuche
"""

import json, sys, subprocess, os, platform, time

EXIT_OK = 0

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = os.path.join(ROOT, "converter.c")
BINARY_FILE = os.path.join(
    ROOT,
    "converter.exe" if platform.system() == "Windows" else "converter"
)
ROMANS_FILE = os.path.join(ROOT, "romans.json")

def main():
    args = set(sys.argv)
    rebuild = any(flag in args for flag in ("-r", "-rebuild"))
    iterations = 5

    if rebuild:
        compile()
        generate_romans()

    if not os.path.exists(BINARY_FILE):
        compile()

    if not os.path.exists(ROMANS_FILE):
        generate_romans()

    print("Running benchmarks...")

    manual_times = []
    regex_times = []

    if platform.system() == "Windows":
        print("Regex validator not available on Windows")

    for i in range(iterations):
        print(f"Run {i+1}/{iterations}:")

        if platform.system() != "Windows":
            regex_time = benchmark(True, f"Regex  {i+1}")
            regex_times.append(regex_time)

        manual_time = benchmark(False, f"Manual {i+1}")
        manual_times.append(manual_time)

    manual_avg = sum(manual_times) / len(manual_times)

    print("\n" + "="*50)
    print("BENCHMARK RESULTS")
    print("="*50)
    print(f"Manual Validator: {manual_avg:.2f}s average")

    if regex_times:
        regex_avg = sum(regex_times) / len(regex_times)
        delta = ((regex_avg - manual_avg) / regex_avg) * 100
        print(f"Regex Validator:  {regex_avg:.2f}s average")
        if delta > 0:
            print(f"Manual was {delta:.1f}% faster than Regex")
        elif delta < 0:
            print(f"Regex was {abs(delta):.1f}% faster than Manual")
        else:
            print("Both validators have identical performance")

    print(f"Platform: {platform.system()}")
    print(f"Test: Int→Roman conversion (1-3999), {iterations} iterations")


def generate_romans():
    print(f"Generating Roman numerals...")
    romans = []
    for i in range(1, 4000):
        result = subprocess.run([BINARY_FILE, "-test"], input=f"2\n{i}\n", capture_output=True, text=True)
        roman = result.stdout.replace("Enter a number up to 3999 or 'Q' to quit: ", "").strip()
        if roman:
            romans.append((roman, str(i)))
        else:
            raise RuntimeError(f"Failed to generate Roman numeral {i}")

    with open(ROMANS_FILE, "w") as f:
        json.dump(romans, f)


def benchmark(regex=False, label="Benchmark"):
    start = time.time()

    command = [BINARY_FILE, "-test"] + (["-regex"] if regex else [])

    with open(ROMANS_FILE) as f:
        romans = json.load(f)

    # Run all conversions from 1 to 3999
    for roman, value in romans:
        result = subprocess.run(command, input=f"1\n{roman}\n",
                              capture_output=True, text=True)
        if result.returncode != EXIT_OK:
            print(f"Error in conversion for {roman}: {result.stderr}")

    duration = time.time() - start

    # Progress indicator
    print(f"  {label}: {duration:.2f}s")

    return duration

def compile():
    print(f"Compiling converter.c...")
    result = subprocess.run(["gcc", "-Wall", "-Werror", SOURCE_FILE, "-o", BINARY_FILE],
                          text=True, capture_output=True)
    if result.returncode != EXIT_OK:
        output = "\n".join(line for line in result.stderr.splitlines()
                          if not (line.startswith("cc1.exe:") or line.startswith("cc1:")))
        print(output)
        print(f"Compilation failed.")
        exit(1)
    print(f"Binary compiled successfully.")

if __name__ == "__main__":
    main()
