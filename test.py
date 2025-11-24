"""
Roman Numeral Converter - Test Suite

Test Coverage:
- 3,999 round-trip validations 
- Invalid Roman numeral rejection tests  
- Invalid integer input rejection tests
- Exit code validation 

Usage:
    python test.py           # Standard test run
    python test.py -regex    # Test regex validator
    python test.py -v        # Verbose output mode
    python test.py -r        # Rebuild and test

Author: Daniel Landuche
"""

import os, platform, subprocess, time, sys

EXIT_OK = 0
EXIT_INVALID_INPUT = 4
EXIT_INVALID_NUMERAL = 5

EXIT_CODES = {
    0: "EXIT_OK",
    4: "EXIT_INVALID_INPUT",
    5: "EXIT_INVALID_NUMERAL"
}

# INVALID format: (input_string, expected_exit_code)
INVALID_ROMANS = [
    # Invalid repeat cases 
    ("VV", EXIT_INVALID_NUMERAL),
    ("LL", EXIT_INVALID_NUMERAL),
    ("DD", EXIT_INVALID_NUMERAL),
    ("IIII", EXIT_INVALID_NUMERAL),
    ("XXXX", EXIT_INVALID_NUMERAL),
    ("CCCC", EXIT_INVALID_NUMERAL),
    ("MMMM", EXIT_INVALID_NUMERAL),
    ("VIV", EXIT_INVALID_NUMERAL),
    ("DCD", EXIT_INVALID_NUMERAL),

    # Invalid subtraction / ordering 
    ("IL", EXIT_INVALID_NUMERAL),
    ("IC", EXIT_INVALID_NUMERAL),
    ("XM", EXIT_INVALID_NUMERAL),
    ("XD", EXIT_INVALID_NUMERAL),
    ("VC", EXIT_INVALID_NUMERAL),
    ("LC", EXIT_INVALID_NUMERAL),
    ("DM", EXIT_INVALID_NUMERAL),
    ("IXCM", EXIT_INVALID_NUMERAL),

    # Invalid structure / nesting 
    ("IIX", EXIT_INVALID_NUMERAL),
    ("XXC", EXIT_INVALID_NUMERAL),
    ("IXIX", EXIT_INVALID_NUMERAL),
    ("MCMC", EXIT_INVALID_NUMERAL),
    ("XCX", EXIT_INVALID_NUMERAL),
    ("XLX", EXIT_INVALID_NUMERAL),
    ("XCL", EXIT_INVALID_NUMERAL),
    ("XLC", EXIT_INVALID_NUMERAL),
    ("ICX", EXIT_INVALID_NUMERAL),
    ("MCMCM", EXIT_INVALID_NUMERAL),

    # Additional tricky edge cases 
    ("IXI", EXIT_INVALID_NUMERAL),       
    ("XCIXIX", EXIT_INVALID_NUMERAL),     
    ("IIV", EXIT_INVALID_NUMERAL),        
    ("XXL", EXIT_INVALID_NUMERAL),        
    ("CCD", EXIT_INVALID_NUMERAL),        
    ("MMMCMCM", EXIT_INVALID_NUMERAL),    
    ("IIIIX", EXIT_INVALID_NUMERAL),      
    ("MCMXCIVI", EXIT_INVALID_NUMERAL),

    # Incorrect length 
    ("IIIIIIIIIIIIIIIIIIII", EXIT_INVALID_INPUT),    

    # Garbage input 
    ("ABC", EXIT_INVALID_NUMERAL),
    ("M1X", EXIT_INVALID_INPUT),
    ("IX!", EXIT_INVALID_INPUT),        
    ("MXI$", EXIT_INVALID_INPUT), 
    (" ", EXIT_INVALID_INPUT),
    ("I V", EXIT_INVALID_INPUT),
    ("IV I", EXIT_INVALID_INPUT),
    ("MCM XCVIII", EXIT_INVALID_INPUT),
    ("MCM XCV III", EXIT_INVALID_INPUT),
    ("MM M", EXIT_INVALID_INPUT),      
]

INVALID_INTS = [
    # Out ouf range
    ("0", EXIT_INVALID_NUMERAL),
    ("-5", EXIT_INVALID_NUMERAL),
    ("4000", EXIT_INVALID_NUMERAL),

    # Garbage input
    ("19$98", EXIT_INVALID_INPUT),
    ("19 98", EXIT_INVALID_INPUT),
    ("1998a", EXIT_INVALID_INPUT),
    ("1998 a", EXIT_INVALID_INPUT),
    ("19.98", EXIT_INVALID_INPUT),
]

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = os.path.join(ROOT, "converter.c")
BINARY_FILE = os.path.join(
    ROOT,
    "converter.exe" if platform.system() == "Windows" else "converter"
)

ROMAN_CONVERTER_PROMPT = "Enter a Roman numeral or 'Q' to quit: "
INT_CONVERTER_PROMPT = "Enter a number up to 3999 or 'Q' to quit: "

MAX_ROMAN = 3999
TOTAL_INVALID = len(INVALID_ROMANS + INVALID_INTS)
TOTAL_VALID = MAX_ROMAN
TOTAL_TESTS = TOTAL_INVALID + TOTAL_VALID

def main():
    args = set(sys.argv)
    regex = True if "-regex" in args else False
    rebuild = any(flag in args for flag in ("-r", "-rebuild"))
    verbose = any(flag in args for flag in ("-v", "-verbose"))

    if not os.path.exists(BINARY_FILE) or rebuild:
        compile()

    passed = tester(verbose, regex)

    print(f"Summary: {passed}/{TOTAL_TESTS} tests passed {'✅' if passed == TOTAL_TESTS else '❌'}")


def compile():
    print(f"Compiling converter.c...")
    result = subprocess.run(["gcc", "-Wall", "-Werror", SOURCE_FILE, "-o", BINARY_FILE],
                            text=True,
                            capture_output=True
                            )
    if result.returncode != EXIT_OK:
        output = "\n".join(line for line in result.stderr.splitlines()
                            if not (line.startswith("cc1.exe:") or line.startswith("cc1:")))
        print(output)
        print(f"Compilation failed.")
        exit(1)
    print(f"Binary compiled successfully.")


def tester(verbose = False, regex = False):
    start = time.time()

    if not verbose:
        print(f"Performing round-trip verification...")
    round_trip_results = round_trip(verbose, regex)

    if not verbose:
        print(f"Testing invalid Romans...")
    roman_results = test_loop(verbose, regex)

    if not verbose:
        print(f"Testing invalid Integers...")
    int_results = test_loop(verbose, regex, 2)

    duration = time.time() - start

    if duration > 60:
        minutes = int(duration // 60)
        seconds = duration % 60
        formatted_duration = f"{minutes} minute{'s' if minutes > 1 else ''} and {seconds:.0f} second{'s' if seconds > 1 else ''}"
    else:
        formatted_duration = f"{duration:.2f} seconds"

    print(f"Test duration: {formatted_duration}")

    return roman_results + int_results + round_trip_results

def round_trip(verbose = False, regex = False):
    passed = 0

    command = [BINARY_FILE, "-test"] + (["-regex"] if regex else [])

    for i in range(1, 4000):
        roman_result = subprocess.run(command, input=f"2\n{i}\n", capture_output=True, text=True)
        roman = roman_result.stdout.replace(INT_CONVERTER_PROMPT, "").strip()

        integer_result = subprocess.run([BINARY_FILE, "-test"], input=f"1\n{roman}\n", capture_output=True, text=True)
        integer = integer_result.stdout.replace(ROMAN_CONVERTER_PROMPT, "").strip()

        try:
            assert integer == str(i) 
        except AssertionError:
            print(f" ❌ Test '{i:<40}' → Roman: {roman:40} | → Int: {integer}")
            print("Validation failed, exiting test suite.")
            sys.exit(1)

        if verbose:
            print(f"✅ Test '{i:<20}' → Roman: {roman:40} | → Int: {integer}")

        else:
            sys.stdout.write(f"\rProgress: {i}/3999")
            sys.stdout.flush()

        passed += 1

    if not verbose:
        print(" ✅")

    return passed

def test_loop(verbose = False, regex = False, option = 1):
    passed = 0

    command = [BINARY_FILE, "-test"]

    if option == 1:
        prompt = ROMAN_CONVERTER_PROMPT
        prefix = "1\n"
        tests = INVALID_ROMANS
        if regex:
            command.append("-regex")

    elif option == 2:
        prompt = INT_CONVERTER_PROMPT
        prefix = "2\n"
        tests = INVALID_INTS

    total_tests = len(tests)

    for idx, (inp, expected_code) in enumerate(tests, start=1):
        result = subprocess.run([BINARY_FILE, "-test"], input=f"{prefix}{inp}\n", capture_output=True, text=True)
        output = (result.stdout + result.stderr).replace(prompt, "").strip()
        code = result.returncode
        code_name = EXIT_CODES.get(code, f"UNKNOWN ({code})")
        expected_code_name = EXIT_CODES.get(expected_code, "UNKNOWN")

        if expected_code != code:
            print(f" ❌ Test '{inp:<20}' → Result: {output:40} | → Return code: {code_name} | → Expected code: {expected_code_name}")
            continue

        if verbose:
            print(f"✅ Test '{inp:<20}' → Result: {output:40} | → Return code: {code_name}")

        else:
            sys.stdout.write(f"\rProgress: {idx}/{total_tests}")
            sys.stdout.flush()

        passed += 1
    if not verbose:
        print(" ✅")
        
    return passed


if __name__ == "__main__":
    main()