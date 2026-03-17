# Password Generator — Project Instructions

## Overview

This is a **password generator** application. Its sole purpose in this first iteration is to
generate strong, random passwords suitable for use across popular internet services.

> **Future scope:** A later iteration may extend this app to also *store* passwords (vault
> functionality). That is explicitly **out of scope** for v1 — this version focuses only on
> generation.

---

## Target Compatibility

Generated passwords **must** be accepted by at least the following services:

| Service   | Min Length | Max Length | Required Character Types                            | Notable Restrictions                     |
|-----------|-----------|-----------|-----------------------------------------------------|------------------------------------------|
| Microsoft | 8         | 256       | At least 3 of 4: uppercase, lowercase, digit, symbol | No Unicode; no leading/trailing spaces   |
| Google    | 8         | 100       | None strictly enforced (mix recommended)            | No leading/trailing spaces               |
| Facebook  | 6         | 128*      | None strictly enforced (mix recommended)            | Standard ASCII symbols                   |

\* Practical upper limits; exact maximums may vary.

To satisfy **all three** services simultaneously, generated passwords should always contain
uppercase letters, lowercase letters, digits, **and** special characters, with a default length
well above the minimum.

---

## Password Parameters

The generator must support the following configurable parameters. Each boolean parameter acts as
a **toggle** that can be easily switched on or off.

### Length

| Parameter        | Type    | Default | Constraints       | Description                                    |
|------------------|---------|---------|-------------------|------------------------------------------------|
| `length`         | integer | 20      | 8 – 128           | Total number of characters in the password      |

- The minimum of **8** ensures compatibility with all target services.
- The default of **20** follows NIST recommendations for strong passwords (≥ 16 characters).

### Character-Set Toggles

Each toggle controls whether a class of characters may appear in the generated password.
**At least one toggle must be enabled.**

| Parameter             | Type    | Default | Character Pool                                                  |
|-----------------------|---------|---------|-----------------------------------------------------------------|
| `includeUppercase`    | boolean | ON      | `A B C D E F G H I J K L M N O P Q R S T U V W X Y Z`         |
| `includeLowercase`    | boolean | ON      | `a b c d e f g h i j k l m n o p q r s t u v w x y z`         |
| `includeDigits`       | boolean | ON      | `0 1 2 3 4 5 6 7 8 9`                                          |
| `includeSpecial`      | boolean | ON      | `! @ # $ % ^ & * ( ) - _ = + [ ] { } \| ; : ' " , . < > ? /`  |

### Additional Toggles

| Parameter                  | Type    | Default | Description                                                                  |
|----------------------------|---------|---------|------------------------------------------------------------------------------|
| `excludeAmbiguous`         | boolean | OFF     | Remove visually similar characters: `0 O o l 1 I \| ` (helps when reading passwords aloud or on paper) |
| `excludeSimilar`           | boolean | OFF     | Remove characters that look alike in certain fonts: `{ } [ ] ( ) / \ ' " ` ~ , ; : . < >` |
| `noConsecutiveRepeats`     | boolean | ON      | Prevent the same character from appearing twice in a row                      |
| `beginWithLetter`          | boolean | OFF     | Ensure the first character is always a letter (some legacy systems require this) |

### Guaranteed Inclusion

When a character-set toggle is **ON**, the generator **must** guarantee that **at least one**
character from that set appears in the output. This ensures passwords satisfy services that
require a mix of character types (e.g., Microsoft's "3 of 4" rule).

---

## Default Preset

With all defaults applied, the generator should produce passwords that:

1. Are **20 characters** long.
2. Contain at least one uppercase letter, one lowercase letter, one digit, and one special character.
3. Do **not** repeat the same character consecutively.
4. Use only ASCII-printable characters (no Unicode, no spaces).
5. Are fully compatible with Microsoft, Google, and Facebook account creation.

### Quick-Start Example

```
Parameters used:
  length              = 20
  includeUppercase     = ON
  includeLowercase     = ON
  includeDigits        = ON
  includeSpecial       = ON
  excludeAmbiguous     = OFF
  excludeSimilar       = OFF
  noConsecutiveRepeats = ON
  beginWithLetter      = OFF

Sample output:  k7$Tq2!mZx9&wR4@nBv5
```

---

## Toggle Behaviour Guidelines

- **Toggling OFF all four character-set switches is invalid** — the app should prevent this and
  display a clear error message.
- When `excludeAmbiguous` or `excludeSimilar` is turned ON, the removed characters must be
  subtracted from every enabled character set before generation.
- When the effective character pool becomes too small to satisfy the requested length uniquely
  (edge case), the app should warn the user rather than silently produce weak passwords.

---

## Security Considerations

- Use a **cryptographically secure** random number generator (e.g., `crypto.getRandomValues`,
  `secrets` module, or platform equivalent). Do **not** use `Math.random()` or similar PRNGs.
- Generated passwords must **never** be logged, cached to disk, or transmitted over a network.
- No analytics or telemetry should capture password content.

---

## Technology Stack

This application must be built as a **client-side only** web application using:

- **HTML5** — semantic markup and structure
- **CSS3** — styling and responsive layout (no preprocessors)
- **Vanilla JavaScript (ES6+)** — all logic, DOM manipulation, and password generation

### No External Dependencies

This project must have **zero external dependencies**. Specifically:

- **No npm packages, CDN imports, or third-party libraries** (no React, Vue, Angular, jQuery,
  Bootstrap, Tailwind, etc.)
- **No build tools or bundlers** (no Webpack, Vite, Rollup, etc.)
- **No CSS frameworks or icon libraries**
- **No server-side runtime** (no Node.js, no .NET, no backend of any kind for v1)

The entire application must consist of plain `.html`, `.css`, and `.js` files that run directly
in any modern browser by opening the HTML file — no compilation, transpilation, or installation
step required.

### Cryptography

Use the browser-native **`crypto.getRandomValues()`** API for all random number generation.
This is a cryptographically secure source built into every modern browser and requires no
external library.

### Future Consideration

If a later iteration adds password storage (vault), a .NET backend may be introduced at that
point. The JavaScript frontend should be structured so it can later communicate with a backend
API without major refactoring.

---

## Testing

Automated tests **must** be created and **run on every change** before committing. This is a
non-negotiable quality gate.

### Requirements

- A dedicated test file (`tests.js`) must exist alongside the application code.
- Tests must run via a single command (`python tests.js` or opening `tests.html` in a browser)
  with **no external test frameworks** (consistent with the zero-dependency rule).
- Tests must use a lightweight, built-in assertion approach (e.g., a simple `assert` helper that
  throws on failure and logs pass/fail results).
- **Every pull request / change must pass all existing tests before being committed.**
- **New functionality must include corresponding new tests.**

### What to Test

At a minimum, the test suite must cover:

1. **Default generation** — output is 20 characters, contains uppercase, lowercase, digit, and
   special character.
2. **Length bounds** — lengths 8 and 128 produce correct-length output; values outside 8–128
   return an error.
3. **Individual character sets** — toggling a single set ON (others OFF) produces passwords
   using only that set.
4. **Guaranteed inclusion** — when multiple sets are ON, at least one character from each set
   appears in the output.
5. **Exclude ambiguous** — filtered characters (`0 O o l 1 I |`) never appear when the toggle
   is ON.
6. **Exclude similar** — filtered characters never appear when the toggle is ON.
7. **No consecutive repeats** — no two adjacent characters are identical when the toggle is ON.
8. **Begin with letter** — first character is `[a-zA-Z]` when the toggle is ON.
9. **All character sets disabled** — returns an appropriate error.
10. **Edge cases** — length too short for guaranteed inclusion, empty pool after filtering, etc.
11. **Bulk / fuzz run** — generate at least 50 passwords with defaults and verify all constraints
    hold consistently.

### Test Workflow

```
1. Make a code change
2. Run tests          →  All tests must pass
3. Commit the change  →  Include a meaningful commit message
```

If any test fails, the change must be fixed before committing.

---

## Source Control

This project must be maintained in a **Git repository**.

### Rules

- The repository must be initialised at the project root (`passwordgenerator/`).
- **Every meaningful change must be committed** with a clear, descriptive commit message.
- Commit messages should follow conventional style: a short summary line (≤ 72 chars) describing
  *what* changed, optionally followed by a blank line and more detail.
- Do **not** commit generated or temporary files. Use a `.gitignore` where appropriate.
- Logical units of work should be committed separately (e.g., don't lump a new feature and a
  bug fix into one commit).

### Example Commit Messages

```
Add password generation engine with crypto.getRandomValues

Scaffold HTML layout with toggle controls and output area

Add automated test suite for generation engine

Fix edge case: pool too small when both exclude filters enabled
```

---

## Out of Scope (v1)

The following features are **not** part of this iteration but may be added later:

- Password storage / vault
- Master-password or biometric unlock
- Browser extension or auto-fill integration
- Password strength meter / scoring
- Passphrase generation (word-based)
- Cloud sync

---

*Last updated: March 2026*
