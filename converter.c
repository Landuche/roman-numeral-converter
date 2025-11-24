/**
 * Roman Numeral Converter
 * 
 * Features:
 * - Bidirectional conversion (integer ↔ Roman numeral)
 * - Dual validation engines (state machine + POSIX regex)
 * - Comprehensive input validation and error handling
 * 
 * Usage:
 *   ./converter          # Interactive mode
 *   ./converter -test    # Automated test mode  
 *   ./converter -regex   # Use regex validator (Unix systems)
 *
 * Platform Notes:
 * - Regex validator disabled on Windows (<regex.h> unavailable)
 * - Manual state machine validator used as default on all platforms
 *
 * Author: Daniel Landuche
 */

#include <ctype.h>
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
    #define REGEX_AVAILABLE 0
#else
    #define REGEX_AVAILABLE 1
    #include <regex.h>
#endif

#define MAX_ROMAN_LENGTH 20
#define MAX_INT_LENGTH 10
#define MAIN_BUFFER_LENGTH 10
#define ROMAN_MAX 3999
#define ROMAN_MIN 1

// Exit codes
#define EXIT_PROGRAM          -1 // exit
#define EXIT_OK                0 // valid
#define EXIT_INPUT_ERR         1 // fgets failed
#define EXIT_EMPTY_ERR         2 // empty input
#define EXIT_MALLOC_ERR        3 // Memory allocation error
#define EXIT_INVALID_INPUT     4 // Invalid input
#define EXIT_INVALID_NUMERAL   5 // Invalid numeral

bool use_regex = false;

int roman_converter(const char *roman);
static int roman_value(char c);
int roman_to_int(void);
int int_to_roman(void);
int validate_input(char *input);
bool validate_roman(const char *roman);
char *int_converter(int num);
bool input_overflow_check(char *input);
static bool is_valid_subtractive(int prev_value, int current_value);
static bool can_subsequently_repeat(int value, int repeat_count);
static bool cannot_repeat(int value, bool *v_repeat, bool *l_repeat, bool *d_repeat);
#if REGEX_AVAILABLE
    bool regex_roman(const char *roman);
#endif

int main(int argc, char *argv[])
{
    bool test_mode = false;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-test") == 0) {
            test_mode = true;
        }
        else if (strcmp(argv[i], "-regex") == 0) {
            use_regex = true;
        }
    }

    int status;

    char buffer[MAIN_BUFFER_LENGTH];
    buffer[0] = '\0';
    while(1) {
        // Test mode hide the main menu
        if (!test_mode)
        {
            printf("\n1) Roman to Int\n");
            printf("2) Int to Roman\n");
            printf("Q) Quit\n");
            printf("\nSelect an option: ");
        }

        if (fgets(buffer, sizeof(buffer), stdin) == NULL)
        {
            fprintf(stderr, "Input error.\n");
            return EXIT_INPUT_ERR;
        }

        // Validate input
        int validation_status = validate_input(buffer);
        if (validation_status != EXIT_OK)
        {
            if (validation_status == EXIT_PROGRAM)
            {
                return EXIT_PROGRAM;
            }
            fprintf(stderr, "Invalid input.\n");
            return validation_status;
        }

        if (strcmp(buffer, "1") == 0)
        {
            do {
                status = roman_to_int();
            } while (!test_mode && status != EXIT_PROGRAM);
            if (test_mode) return status;
        }

        else if (strcmp(buffer, "2") == 0)
        {
            do {
                status = int_to_roman();
            } while (!test_mode && status != EXIT_PROGRAM);
            if (test_mode) return status;
        }

        else
        {
            fprintf(stderr, "\nInvalid input.\n");
        }

    }

    return status;
}

int validate_input(char *input)
{
    // Detect overflow
    if (input_overflow_check(input)) {
        return EXIT_INVALID_INPUT;
    }

    // Remove newline
    input[strcspn(input, "\n")] = '\0';

    // Detect empty input
    if (input[0] == '\0')
    {
        return EXIT_EMPTY_ERR;
    }

    // Quit if user enters Q
    if (toupper(input[0]) == 'Q' && input[1] == '\0')
    {
        return EXIT_PROGRAM;
    }

    return EXIT_OK;
}

bool input_overflow_check(char *input)
{
    if (!strchr(input, '\n')) {
        for (int c; (c = getchar()) != '\n' && c != EOF; );
        return true;
    }
    return false;
}

int int_to_roman(void)
{
    char input[MAX_INT_LENGTH];

    // Get number
    printf("Enter a number up to 3999 or 'Q' to quit: ");
    if (fgets(input, sizeof(input), stdin) == NULL)
    {
        fprintf(stderr, "Input error.\n");
        return EXIT_INPUT_ERR;
    }

    // Validate input
    int validation_status = validate_input(input);
    if (validation_status != EXIT_OK)
    {
        if (validation_status == EXIT_PROGRAM)
        {
            return EXIT_PROGRAM;
        }
        fprintf(stderr, "Invalid input.\n");
        return validation_status;
    }

    // Convert input
    long num;
    char *ptr;
    errno = 0;
    num = strtol(input, &ptr, 10);

    if (*ptr != '\0' || errno != 0)
    {
        fprintf(stderr, "Invalid input.\n");
        return EXIT_INVALID_INPUT;
    }

    // Check if number is inside the range
    if (num > ROMAN_MAX || num < ROMAN_MIN)
    {
        fprintf(stderr, "Out of range (1-3999).\n");
        return EXIT_INVALID_NUMERAL;
    }

    char *r = int_converter(num);
    if (r == NULL)
    {
        fprintf(stderr, "Memory allocation error.\n");
        return EXIT_MALLOC_ERR;
    }

    printf("%s\n", r);
    free(r);
    return EXIT_OK;
}

char *int_converter(int num)
{
    char *roman = malloc(MAX_ROMAN_LENGTH);
    if (!roman)
    {
        return NULL;
    }
    roman[0] = '\0';

    const int values[] = {1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1};
    const char *symbols[] = {"M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"};

    for (size_t i = 0; num > 0 && i < sizeof(values)/sizeof(values[0]); i++)
    {
        while (num >= values[i])
        {
            strcat(roman, symbols[i]);
            num -= values[i];
        }
    }

    return roman;
}

int roman_to_int(void)
{
    char roman[MAX_ROMAN_LENGTH];

    // Get number
    printf("Enter a Roman numeral or 'Q' to quit: ");
    if (fgets(roman, sizeof(roman), stdin) == NULL)
    {
        fprintf(stderr, "Input error.\n");
        return EXIT_INPUT_ERR;
    }

    // Validate input
    int validation_status = validate_input(roman);
    if (validation_status != EXIT_OK)
    {
        if (validation_status == EXIT_PROGRAM)
        {
            return EXIT_PROGRAM;
        }
        fprintf(stderr, "Invalid input.\n");
        return validation_status;
    }

    // Convert to upper case
    for (size_t i = 0; roman[i] != '\0'; i++)
    {
        if (!isalpha((unsigned char)roman[i]))
        {
            fprintf(stderr, "Invalid input.\n");
            return EXIT_INVALID_INPUT;
        }
        roman[i] = toupper((unsigned char)roman[i]);
    }

    // Validate number before converting
    if (REGEX_AVAILABLE && use_regex)
    {
#if REGEX_AVAILABLE
        if (!regex_roman(roman))
        {
            fprintf(stderr, "%s is not a valid Roman numeral.\n", roman);
            return EXIT_INVALID_NUMERAL;
        }
#else
        fprintf(stderr, "Regex validator not available on this platform\n");
        return EXIT_INVALID_NUMERAL;
#endif
    }
    else
    {
        if (!validate_roman(roman))
        {
            fprintf(stderr, "%s is not a valid Roman numeral.\n", roman);
            return EXIT_INVALID_NUMERAL;
        }
    }

    printf("%i\n", roman_converter(roman));

    return EXIT_OK;
}

static int roman_value(char c)
{
    switch (c)
    {
        case 'I':
            return 1;
        case 'V':
            return 5;
        case 'X':
            return 10;
        case 'L':
            return 50;
        case 'C':
            return 100;
        case 'D':
            return 500;
        case 'M':
            return 1000;
        default:
            return 0;
    }
}

int roman_converter(const char *roman)
{
    int total = 0;
    for (size_t i = 0; roman[i]; i++)
    {
        int current_value = roman_value(roman[i]);
        int next_value = roman[i + 1] ? roman_value(roman[i + 1]) : 0;

        if (current_value < next_value)
        {
            total -= current_value;
        }
        else
        {
            total += current_value;
        }
    }
    return total;
}

#if REGEX_AVAILABLE
bool regex_roman(const char *roman)
{
    regex_t regex;
    const char *pattern = "^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$";

    if (regcomp(&regex, pattern, REG_EXTENDED) != 0)
    {
        return false;
    }

    int result = regexec(&regex, roman, 0, NULL, 0);

    regfree(&regex);
    return result == 0;
}
#endif

bool validate_roman(const char *roman)
{
    int repeat = 1;
    int max = 1000;
    int last_subtractive_value = 0;
    bool last_subtractive = false;
    bool v_repeat = false;
    bool l_repeat = false;
    bool d_repeat = false;

    for (size_t i = 0; roman[i]; i++)
    {
        int current_value = roman_value(roman[i]);

        // Validate character
        if (current_value == 0)
        {
            return false;
        }

        // Track non-repeatable numerals
        if (cannot_repeat(current_value, &v_repeat, &l_repeat, &d_repeat))
        {
            return false;
        }

        if (i == 0)
        {
            continue;
        }

        int prev_value = roman_value(roman[i - 1]);

        // Handle consecutive repeats
        if (current_value == prev_value)
        {
            repeat++;
            if (!can_subsequently_repeat(current_value, repeat))
            {
                return false;
            }
        }
        else
        {
            repeat = 1;
        }

        // Validate subtractive notation
        if (prev_value < current_value)
        {
            if (!is_valid_subtractive(prev_value, current_value) ||
                last_subtractive ||
                current_value > max ||
                prev_value == last_subtractive_value)
            {
                return false;
            }

            last_subtractive_value = prev_value;
            max = current_value;
            last_subtractive = true;
        }

        else
        {
            if (prev_value > max || current_value == last_subtractive_value)
            {
                return false;
            }
            max = prev_value;
            last_subtractive = false;
        }

        // Prevent double subtraction
        if (i > 1)
        {
            int prev_prev = roman_value(roman[i - 2]);
            if (prev_prev < current_value && prev_value < current_value)
            {
                return false;
            }
        }

        // Next-character check for trailing subtractives
        if (last_subtractive && roman[i + 1] && roman_value(roman[i + 1]) > last_subtractive_value)
        {
            return false;
        }
    }
    return true;
}

static bool is_valid_subtractive(int prev, int curr)
{
    return (prev == 1   && (curr == 5 || curr == 10))   ||  // IV, IX
           (prev == 10  && (curr == 50 || curr == 100)) ||  // XL, XC
           (prev == 100 && (curr == 500 || curr == 1000));  // CD, CM
}

static bool can_subsequently_repeat(int value, int repeat_count)
{
    // I, X, C, M can repeat 3 times
    if ((value == 1 || value == 10 || value == 100 || value == 1000) && repeat_count > 3)
        return false;

    return true;
}

static bool cannot_repeat(int value, bool *v_repeat, bool *l_repeat, bool *d_repeat)
{
    switch(value)
    {
        // V, L, D cannot repeat
        case 5: if (*v_repeat) return true; *v_repeat = true; break;
        case 50: if (*l_repeat) return true; *l_repeat = true; break;
        case 500: if (*d_repeat) return true; *d_repeat = true; break;
    }
    return false;
}