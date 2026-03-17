# 🔐 Password Generator

A lightweight, client-side password generator that creates strong, random passwords suitable for
use with Microsoft, Google, Facebook, and other internet services.

**No installation. No dependencies. No server.** Open `index.html` in any modern browser and
start generating passwords.

---

## Quick Start

1. Open **`index.html`** in your browser (Chrome, Firefox, Edge, or Safari).
2. Adjust the settings using the toggle switches and length slider.
3. Click **Generate** (or press **Enter**).
4. Click **Copy** to copy the password to your clipboard.

That's it — no build step, no terminal commands, no internet connection required.

---

## Features

- **Cryptographically secure** — uses the browser-native `crypto.getRandomValues()` API; never
  uses `Math.random()`.
- **Configurable** — toggle character sets on/off, adjust length, and apply filters with a
  single click.
- **Compatible** — default settings produce passwords accepted by Microsoft, Google, Facebook,
  and virtually all other services.
- **Zero dependencies** — pure HTML, CSS, and JavaScript. No frameworks, no npm, no build tools.
- **Private** — passwords are generated entirely in your browser. Nothing is stored, logged, or
  sent over a network.

---

## Settings Reference

### Length

| Control          | Default | Range   | Description                                |
|------------------|---------|---------|--------------------------------------------|
| Length slider     | 20      | 8 – 128 | Total number of characters in the password |

### Character Set Toggles

| Toggle               | Default | Characters Included                                          |
|----------------------|---------|--------------------------------------------------------------|
| Uppercase (A–Z)      | ON      | `ABCDEFGHIJKLMNOPQRSTUVWXYZ`                                 |
| Lowercase (a–z)      | ON      | `abcdefghijklmnopqrstuvwxyz`                                 |
| Digits (0–9)         | ON      | `0123456789`                                                 |
| Special (!@#$…)      | ON      | `!@#$%^&*()-_=+[]{}|;:'",.<>?/`                             |

At least one character set must remain enabled. When a set is ON, the generated password is
**guaranteed** to contain at least one character from that set.

### Additional Options

| Toggle                    | Default | Effect                                                      |
|---------------------------|---------|-------------------------------------------------------------|
| Exclude ambiguous         | OFF     | Removes `0 O o l 1 I \|` — useful when reading aloud       |
| Exclude similar           | OFF     | Removes `{ } [ ] ( ) / \ ' " \` ~ , ; : . < >`            |
| No consecutive repeats    | ON      | Prevents the same character from appearing twice in a row   |
| Begin with a letter       | OFF     | Ensures the first character is always a letter (a–z, A–Z)  |

---

## Design

### Architecture

The application is a single-page web app with a clear separation of concerns:

```
passwordgenerator/
├── index.html        UI structure and element wiring
├── style.css         All visual styling (dark theme, responsive layout)
├── app.js            Password generation engine + DOM event handling
├── tests.html        Browser-based test suite (open in browser to run)
├── tests.py          Command-line test suite (run with: python tests.py)
├── INSTRUCTIONS.md   Full project specification and requirements
└── README.md         This file
```

### Generation Engine (`app.js`)

The core `generatePassword(options)` function:

1. **Builds a character pool** from the enabled character-set toggles.
2. **Applies exclusion filters** (`excludeAmbiguous`, `excludeSimilar`) by removing matched
   characters from the pool.
3. **Guarantees inclusion** — picks one random character from each enabled set first.
4. **Fills the remainder** from the combined pool using `crypto.getRandomValues()`.
5. **Shuffles** the result with a Fisher-Yates shuffle (also cryptographically random).
6. **Enforces constraints** — `noConsecutiveRepeats` and `beginWithLetter` are applied as
   post-processing passes.
7. **Validates** inputs and returns clear error messages for invalid configurations.

The generation logic is a standalone function at the top of `app.js` with no DOM dependencies,
making it easy to extract into a module or call from a future backend API.

### UI (`index.html` + `style.css`)

- Dark theme with accessible contrast ratios.
- Pure-CSS toggle switches (styled checkboxes — no JavaScript for the switch animation).
- Responsive layout that works on desktop and mobile.
- Password output uses `user-select: all` for easy manual selection and a dedicated **Copy**
  button with brief "Copied!" feedback.
- Inline error messages appear when settings are invalid (e.g., all character sets disabled).
- A password is generated automatically on page load with the default settings.

### Security Model

- All randomness comes from `crypto.getRandomValues()` — a CSPRNG.
- Passwords exist only in JavaScript memory and the clipboard. They are **never** written to
  `localStorage`, cookies, disk, or any network endpoint.
- No analytics, telemetry, or third-party scripts are loaded.

---

## Running Tests

Tests must be run before every commit. Two equivalent test suites are provided:

### Browser

Open **`tests.html`** in any browser. Results appear on-screen with a pass/fail summary.

### Command Line

```bash
python tests.py
```

Requires Python 3.6+ (uses only the standard library). Exits with code `0` on success, `1` on
failure.

### Test Coverage

The test suite covers all 11 areas specified in `INSTRUCTIONS.md`:

1. Default generation (length, character mix)
2. Length bounds (min/max, out-of-range errors)
3. Individual character sets (isolation)
4. Guaranteed inclusion (multi-set representation)
5. Exclude ambiguous filter
6. Exclude similar filter
7. No consecutive repeats (on/off)
8. Begin with letter (on/off, error when no letters available)
9. All character sets disabled (error handling)
10. Edge cases (short length, small pool, combined filters)
11. Bulk / fuzz run (50 passwords under default settings)

---

## Service Compatibility

With default settings, generated passwords satisfy:

| Service   | Min Length | Char Types Required               | ✓ Met by Defaults |
|-----------|-----------|------------------------------------|--------------------|
| Microsoft | 8         | 3 of 4 (upper, lower, digit, sym) | Yes (all 4)        |
| Google    | 8         | Mix recommended, not enforced      | Yes                |
| Facebook  | 6         | Mix recommended, not enforced      | Yes                |

---

## Keeping This README Up to Date

> **Important:** This README must be updated whenever the application changes. Specifically:
>
> - **New features or settings** — add them to the Settings Reference and Design sections.
> - **New files** — update the Architecture file tree.
> - **Changed defaults** — update the Settings Reference tables.
> - **New test categories** — update the Test Coverage list.
> - **New service compatibility** — update the Compatibility table.
> - **Breaking changes** — note them prominently at the top of this file.
>
> A pull request that changes functionality without updating this README is incomplete.

---

## Future Roadmap (Out of Scope for v1)

- Password storage / vault (with .NET backend)
- Master-password or biometric unlock
- Browser extension and auto-fill
- Password strength meter
- Passphrase generation (word-based)
- Cloud sync

See `INSTRUCTIONS.md` for the full project specification.

---

*Last updated: March 2026*
