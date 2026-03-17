"""
Password Generator — Command-line test runner
Run: python tests.py
Zero external dependencies — uses only Python stdlib.
"""

import re
import os
import sys
import secrets

# ---- Shim: replicate the JS generation logic in Python for CLI testing ----

CHAR_SETS = {
    "uppercase": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "lowercase": "abcdefghijklmnopqrstuvwxyz",
    "digits": "0123456789",
    "special": "!@#$%^&*()-_=+[]{}|;:'\",.<>?/",
}

AMBIGUOUS_CHARS = "0OolI1|"
SIMILAR_CHARS = "{}[]()/<>\\'\"`~,;:."


def secure_random_index(max_val):
    return secrets.randbelow(max_val)


def shuffle(arr):
    for i in range(len(arr) - 1, 0, -1):
        j = secure_random_index(i + 1)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def generate_password(
    length=20,
    include_uppercase=True,
    include_lowercase=True,
    include_digits=True,
    include_special=True,
    exclude_ambiguous=False,
    exclude_similar=False,
    no_consecutive_repeats=True,
    begin_with_letter=False,
):
    if length < 8 or length > 128:
        return {"error": "Password length must be between 8 and 128."}

    def filter_chars(chars):
        result = chars
        if exclude_ambiguous:
            result = "".join(c for c in result if c not in AMBIGUOUS_CHARS)
        if exclude_similar:
            result = "".join(c for c in result if c not in SIMILAR_CHARS)
        return result

    enabled_sets = []
    if include_uppercase:
        enabled_sets.append(("uppercase", filter_chars(CHAR_SETS["uppercase"])))
    if include_lowercase:
        enabled_sets.append(("lowercase", filter_chars(CHAR_SETS["lowercase"])))
    if include_digits:
        enabled_sets.append(("digits", filter_chars(CHAR_SETS["digits"])))
    if include_special:
        enabled_sets.append(("special", filter_chars(CHAR_SETS["special"])))

    if not enabled_sets:
        return {"error": "At least one character set must be enabled."}

    empty = [name for name, chars in enabled_sets if len(chars) == 0]
    if empty:
        return {"error": f'Character set "{empty[0]}" is empty after applying filters.'}

    pool = "".join(chars for _, chars in enabled_sets)

    if len(pool) < 2 and no_consecutive_repeats:
        return {"error": "Character pool is too small to avoid consecutive repeats."}

    guaranteed = [chars[secure_random_index(len(chars))] for _, chars in enabled_sets]

    remaining = length - len(guaranteed)
    if remaining < 0:
        return {"error": f"Password length ({length}) too short for {len(enabled_sets)} sets."}

    pw = list(guaranteed)
    for _ in range(remaining):
        pw.append(pool[secure_random_index(len(pool))])

    shuffle(pw)

    if no_consecutive_repeats:
        for i in range(1, len(pw)):
            attempts = 0
            while pw[i] == pw[i - 1] and attempts < 100:
                pw[i] = pool[secure_random_index(len(pool))]
                attempts += 1

    if begin_with_letter:
        letter_pool = ""
        for name, chars in enabled_sets:
            if name in ("uppercase", "lowercase"):
                letter_pool += chars
        if not letter_pool:
            return {"error": "Begin with letter enabled but no letter sets active."}
        if not pw[0].isalpha():
            letter = letter_pool[secure_random_index(len(letter_pool))]
            swap_idx = 1 + secure_random_index(len(pw) - 1)
            pw[swap_idx] = pw[0]
            pw[0] = letter

    if no_consecutive_repeats:
        for i in range(1, len(pw)):
            attempts = 0
            while pw[i] == pw[i - 1] and attempts < 100:
                pw[i] = pool[secure_random_index(len(pool))]
                attempts += 1

    return {"password": "".join(pw)}


# ---- Test runner ----

passed = 0
failed = 0


def assert_test(condition, message):
    global passed, failed
    if condition:
        passed += 1
        print(f"  \033[32m✓ {message}\033[0m")
    else:
        failed += 1
        print(f"  \033[31m✗ {message}\033[0m")


def section(name):
    print(f"\n{name}")


# ---- Tests ----

section("1. Default generation")
r = generate_password()
assert_test("error" not in r, "No error on defaults")
assert_test(len(r["password"]) == 20, "Default length is 20")
assert_test(bool(re.search(r"[A-Z]", r["password"])), "Contains uppercase")
assert_test(bool(re.search(r"[a-z]", r["password"])), "Contains lowercase")
assert_test(bool(re.search(r"[0-9]", r["password"])), "Contains digit")
assert_test(bool(re.search(r"[^a-zA-Z0-9]", r["password"])), "Contains special character")

section("2. Length bounds")
r8 = generate_password(length=8)
assert_test("error" not in r8 and len(r8["password"]) == 8, "Length 8 produces 8-char password")
r128 = generate_password(length=128)
assert_test("error" not in r128 and len(r128["password"]) == 128, "Length 128 produces 128-char password")
r_low = generate_password(length=3)
assert_test("error" in r_low, "Length 3 returns error")
r_high = generate_password(length=200)
assert_test("error" in r_high, "Length 200 returns error")

section("3. Individual character sets")
r_upper = generate_password(include_lowercase=False, include_digits=False, include_special=False)
assert_test("error" not in r_upper and bool(re.match(r"^[A-Z]+$", r_upper["password"])), "Uppercase-only")
r_lower = generate_password(include_uppercase=False, include_digits=False, include_special=False)
assert_test("error" not in r_lower and bool(re.match(r"^[a-z]+$", r_lower["password"])), "Lowercase-only")
r_digits = generate_password(include_uppercase=False, include_lowercase=False, include_special=False)
assert_test("error" not in r_digits and bool(re.match(r"^[0-9]+$", r_digits["password"])), "Digits-only")
r_special = generate_password(include_uppercase=False, include_lowercase=False, include_digits=False)
assert_test("error" not in r_special and bool(re.match(r"^[^a-zA-Z0-9]+$", r_special["password"])), "Special-only")

section("4. Guaranteed inclusion (30 runs, length=8)")
all_good = True
for _ in range(30):
    r = generate_password(length=8)
    if "error" in r:
        all_good = False
        break
    pw = r["password"]
    if not (re.search(r"[A-Z]", pw) and re.search(r"[a-z]", pw) and re.search(r"[0-9]", pw) and re.search(r"[^a-zA-Z0-9]", pw)):
        all_good = False
        break
assert_test(all_good, "All 4 sets represented in 30 consecutive 8-char passwords")

section("5. Exclude ambiguous")
clean = True
for _ in range(30):
    r = generate_password(exclude_ambiguous=True)
    if "error" in r:
        clean = False
        break
    if any(c in r["password"] for c in AMBIGUOUS_CHARS):
        clean = False
        break
assert_test(clean, "No ambiguous characters in 30 passwords")

section("6. Exclude similar")
clean = True
for _ in range(30):
    r = generate_password(exclude_similar=True)
    if "error" in r:
        clean = False
        break
    if any(c in r["password"] for c in SIMILAR_CHARS):
        clean = False
        break
assert_test(clean, "No similar characters in 30 passwords")

section("7. No consecutive repeats")
good = True
for _ in range(50):
    r = generate_password(no_consecutive_repeats=True)
    if "error" in r:
        good = False
        break
    if re.search(r"(.)\1", r["password"]):
        good = False
        break
assert_test(good, "No consecutive repeats in 50 passwords")

found_repeat = False
for _ in range(200):
    r = generate_password(
        length=128, no_consecutive_repeats=False,
        include_uppercase=False, include_lowercase=False, include_special=False,
    )
    if "password" in r and re.search(r"(.)\1", r["password"]):
        found_repeat = True
        break
assert_test(found_repeat, "Consecutive repeats possible when toggle OFF (digits-only 128-char)")

section("8. Begin with letter")
good = True
for _ in range(50):
    r = generate_password(begin_with_letter=True)
    if "error" in r:
        good = False
        break
    if not r["password"][0].isalpha():
        good = False
        break
assert_test(good, "First character is a letter in 50 passwords")
r_err = generate_password(begin_with_letter=True, include_uppercase=False, include_lowercase=False)
assert_test("error" in r_err, "Error when beginWithLetter ON but no letter sets enabled")

section("9. All character sets disabled")
r = generate_password(include_uppercase=False, include_lowercase=False, include_digits=False, include_special=False)
assert_test("error" in r, "Returns error when all sets disabled")
assert_test("At least one" in r["error"], "Error message mentions requirement")

section("10. Edge cases")
r = generate_password(length=3)
assert_test("error" in r, "Error when length < minimum (8)")
r2 = generate_password(include_uppercase=False, include_lowercase=False, include_special=False, exclude_ambiguous=True)
assert_test("error" not in r2, "Digits with excludeAmbiguous still works")
assert_test(bool(re.match(r"^[2-9]+$", r2["password"])), "Only non-ambiguous digits present")
r3 = generate_password(exclude_ambiguous=True, exclude_similar=True)
assert_test("error" not in r3, "Both exclude filters with all sets works")
assert_test(len(r3["password"]) == 20, "Still produces 20-char password")

section("11. Bulk / fuzz run (50 passwords, default settings)")
failures = 0
for _ in range(50):
    r = generate_password()
    if "error" in r:
        failures += 1
        continue
    pw = r["password"]
    if len(pw) != 20:
        failures += 1
    if not re.search(r"[A-Z]", pw):
        failures += 1
    if not re.search(r"[a-z]", pw):
        failures += 1
    if not re.search(r"[0-9]", pw):
        failures += 1
    if not re.search(r"[^a-zA-Z0-9]", pw):
        failures += 1
    if re.search(r"(.)\1", pw):
        failures += 1
assert_test(failures == 0, f"All 50 default passwords valid (failures: {failures})")

# ---- Summary ----

total = passed + failed
print()
if failed == 0:
    print(f"\033[32m=== ALL {total} TESTS PASSED ===\033[0m")
else:
    print(f"\033[31m=== {failed} of {total} TESTS FAILED ===\033[0m")
sys.exit(0 if failed == 0 else 1)
