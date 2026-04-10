/* ============================================================
   Password Generator — app.js
   Pure client-side password generator. Zero dependencies.
   ============================================================ */

// ---- Character sets ----

const CHAR_SETS = {
  uppercase: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
  lowercase: 'abcdefghijklmnopqrstuvwxyz',
  digits: '0123456789',
  special: '!@#$%^&*()-_=+[]{}|;:\'",.<>?/',
};

const AMBIGUOUS_CHARS = '0OolI1|';
const SIMILAR_CHARS = '{}[]()/<>\\\'"`~,;:.';

// ---- Cryptographically secure random helpers ----

function secureRandomIndex(max) {
  const array = new Uint32Array(1);
  crypto.getRandomValues(array);
  return array[0] % max;
}

function shuffleArray(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = secureRandomIndex(i + 1);
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

// ---- Core generation logic ----

function generatePassword(options = {}) {
  const {
    length = 20,
    includeUppercase = true,
    includeLowercase = true,
    includeDigits = true,
    includeSpecial = true,
    excludeAmbiguous = false,
    excludeSimilar = false,
    noConsecutiveRepeats = true,
    beginWithLetter = false,
  } = options;

  // Validate length
  if (length < 8 || length > 128) {
    return { error: 'Password length must be between 8 and 128.' };
  }

  // Build per-set pools (filtered)
  const filterChars = (chars) => {
    let result = chars;
    if (excludeAmbiguous) {
      result = result.split('').filter((c) => !AMBIGUOUS_CHARS.includes(c)).join('');
    }
    if (excludeSimilar) {
      result = result.split('').filter((c) => !SIMILAR_CHARS.includes(c)).join('');
    }
    return result;
  };

  const enabledSets = [];
  if (includeUppercase) enabledSets.push({ name: 'uppercase', chars: filterChars(CHAR_SETS.uppercase) });
  if (includeLowercase) enabledSets.push({ name: 'lowercase', chars: filterChars(CHAR_SETS.lowercase) });
  if (includeDigits) enabledSets.push({ name: 'digits', chars: filterChars(CHAR_SETS.digits) });
  if (includeSpecial) enabledSets.push({ name: 'special', chars: filterChars(CHAR_SETS.special) });

  if (enabledSets.length === 0) {
    return { error: 'At least one character set must be enabled.' };
  }

  // Check for empty sets after filtering
  const emptySets = enabledSets.filter((s) => s.chars.length === 0);
  if (emptySets.length > 0) {
    return {
      error: `Character set "${emptySets[0].name}" is empty after applying filters. Disable a filter or enable more character sets.`,
    };
  }

  // Full pool
  const pool = enabledSets.map((s) => s.chars).join('');

  if (pool.length < 2 && noConsecutiveRepeats) {
    return { error: 'Character pool is too small to avoid consecutive repeats. Adjust your settings.' };
  }

  // Guarantee at least one character from each enabled set
  const guaranteed = enabledSets.map((s) => s.chars[secureRandomIndex(s.chars.length)]);

  // Fill the rest
  const remaining = length - guaranteed.length;
  if (remaining < 0) {
    return { error: `Password length (${length}) is too short to include at least one character from each enabled set (${enabledSets.length} sets).` };
  }

  const passwordChars = [...guaranteed];
  for (let i = 0; i < remaining; i++) {
    passwordChars.push(pool[secureRandomIndex(pool.length)]);
  }

  // Shuffle so guaranteed chars aren't always at the start
  shuffleArray(passwordChars);

  // Enforce noConsecutiveRepeats
  if (noConsecutiveRepeats) {
    for (let i = 1; i < passwordChars.length; i++) {
      let attempts = 0;
      while (passwordChars[i] === passwordChars[i - 1] && attempts < 100) {
        passwordChars[i] = pool[secureRandomIndex(pool.length)];
        attempts++;
      }
    }
  }

  // Enforce beginWithLetter
  if (beginWithLetter) {
    const letterPool = (enabledSets.find((s) => s.name === 'uppercase')?.chars || '') +
                       (enabledSets.find((s) => s.name === 'lowercase')?.chars || '');
    if (letterPool.length === 0) {
      return { error: '"Begin with letter" is enabled but no letter character sets are active.' };
    }
    if (!/[a-zA-Z]/.test(passwordChars[0])) {
      // Swap first char with a random letter, put old first char elsewhere
      const letterChar = letterPool[secureRandomIndex(letterPool.length)];
      const swapIndex = 1 + secureRandomIndex(passwordChars.length - 1);
      passwordChars[swapIndex] = passwordChars[0];
      passwordChars[0] = letterChar;
    }
  }

  // Final consecutive-repeat check after beginWithLetter swap
  if (noConsecutiveRepeats) {
    for (let i = 1; i < passwordChars.length; i++) {
      let attempts = 0;
      while (passwordChars[i] === passwordChars[i - 1] && attempts < 100) {
        passwordChars[i] = pool[secureRandomIndex(pool.length)];
        attempts++;
      }
    }
  }

  return { password: passwordChars.join('') };
}

// ---- DOM wiring ----

function registerServiceWorker() {
  const isSupportedProtocol = window.location.protocol === 'http:' || window.location.protocol === 'https:';

  if (!('serviceWorker' in navigator) || !window.isSecureContext || !isSupportedProtocol) {
    return;
  }

  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js').catch((error) => {
      console.warn('Service worker registration failed.', error);
    });
  }, { once: true });
}

registerServiceWorker();

document.addEventListener('DOMContentLoaded', () => {
  const els = {
    lengthSlider: document.getElementById('length-slider'),
    lengthValue: document.getElementById('length-value'),
    includeUppercase: document.getElementById('include-uppercase'),
    includeLowercase: document.getElementById('include-lowercase'),
    includeDigits: document.getElementById('include-digits'),
    includeSpecial: document.getElementById('include-special'),
    excludeAmbiguous: document.getElementById('exclude-ambiguous'),
    excludeSimilar: document.getElementById('exclude-similar'),
    noConsecutiveRepeats: document.getElementById('no-consecutive-repeats'),
    beginWithLetter: document.getElementById('begin-with-letter'),
    generateBtn: document.getElementById('generate-btn'),
    copyBtn: document.getElementById('copy-btn'),
    passwordOutput: document.getElementById('password-output'),
    errorMsg: document.getElementById('error-msg'),
  };

  if (Object.values(els).some((el) => el === null)) {
    return;
  }

  const charSetToggles = [els.includeUppercase, els.includeLowercase, els.includeDigits, els.includeSpecial];

  // Sync slider ↔ display
  els.lengthSlider.addEventListener('input', () => {
    els.lengthValue.textContent = els.lengthSlider.value;
  });

  // Prevent disabling all character-set toggles
  charSetToggles.forEach((toggle) => {
    toggle.addEventListener('change', () => {
      const anyOn = charSetToggles.some((t) => t.checked);
      if (!anyOn) {
        toggle.checked = true;
        showError('At least one character set must be enabled.');
      } else {
        clearError();
      }
    });
  });

  function showError(msg) {
    els.errorMsg.textContent = msg;
    els.errorMsg.classList.add('visible');
  }

  function clearError() {
    els.errorMsg.textContent = '';
    els.errorMsg.classList.remove('visible');
  }

  function readOptions() {
    return {
      length: parseInt(els.lengthSlider.value, 10),
      includeUppercase: els.includeUppercase.checked,
      includeLowercase: els.includeLowercase.checked,
      includeDigits: els.includeDigits.checked,
      includeSpecial: els.includeSpecial.checked,
      excludeAmbiguous: els.excludeAmbiguous.checked,
      excludeSimilar: els.excludeSimilar.checked,
      noConsecutiveRepeats: els.noConsecutiveRepeats.checked,
      beginWithLetter: els.beginWithLetter.checked,
    };
  }

  function handleGenerate() {
    clearError();
    const result = generatePassword(readOptions());
    if (result.error) {
      showError(result.error);
      els.passwordOutput.textContent = '';
      els.copyBtn.disabled = true;
      return;
    }
    els.passwordOutput.textContent = result.password;
    els.copyBtn.disabled = false;
  }

  els.generateBtn.addEventListener('click', handleGenerate);

  // Enter key shortcut
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.target.tagName !== 'BUTTON') {
      handleGenerate();
    }
  });

  // Copy to clipboard
  els.copyBtn.addEventListener('click', () => {
    const pw = els.passwordOutput.textContent;
    if (!pw) return;
    navigator.clipboard.writeText(pw).then(() => {
      els.copyBtn.textContent = 'Copied!';
      els.copyBtn.classList.add('copied');
      setTimeout(() => {
        els.copyBtn.textContent = 'Copy';
        els.copyBtn.classList.remove('copied');
      }, 1500);
    });
  });

  // Generate one on load
  handleGenerate();
});
