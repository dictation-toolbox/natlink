"""PlayString key expansion — pure logic, no COM or state dependencies.

Transforms extended playString syntax into basic Dragon syntax:
  1. Repeat:  {key_N} or {key N} -> {key} repeated N times
  2. Hold/release:  {Mod hold}...{Mod release} -> {Mod+key} for each key
"""

import re

_BRACE_RE = re.compile(r'\{([^}]*)\}')
_REPEAT_SUFFIX_RE = re.compile(r'^(.+)[_ ](\d+)$')
_HOLD_RE = re.compile(r'\{(\w+)[_ ]hold\}', re.IGNORECASE)


def expand_keys(keys: str) -> str:
    """Pre-expand extended playString syntax into basic Dragon syntax.

    Two transformations, applied in order:
      1. Repeat:  {key_N} or {key N} -> {key} repeated N times
      2. Hold/release:  {Mod hold}...{Mod release} -> prepend modifier
         to each {key} inside the span.

    All other syntax (plain text, {Enter}, {Ctrl+a}, etc.) passes through.
    """
    # --- Pass 1: expand repeats ({Backspace_3} -> {Backspace}{Backspace}{Backspace})
    def _expand_repeat(m):
        content = m.group(1)
        rm = _REPEAT_SUFFIX_RE.match(content)
        if rm:
            base, count_str = rm.group(1), rm.group(2)
            count = int(count_str)
            # Don't expand if base looks like hold/release (those are pass 2)
            low = base.lower()
            if low.endswith(' hold') or low.endswith('_hold') or \
               low.endswith(' release') or low.endswith('_release'):
                return m.group(0)
            return ('{' + base + '}') * count
        return m.group(0)

    keys = _BRACE_RE.sub(_expand_repeat, keys)

    # --- Pass 2: expand hold/release spans
    # Find {Mod hold} ... {Mod release} and prepend Mod+ to each {key} inside
    result = keys
    # Process iteratively — each pass resolves one modifier layer
    changed = True
    while changed:
        changed = False
        m = _HOLD_RE.search(result)
        if not m:
            break
        mod = m.group(1)
        # Find matching release
        release_pat = re.compile(
            r'\{' + re.escape(mod) + r'[_ ]release\}', re.IGNORECASE)
        rm = release_pat.search(result, m.end())
        if not rm:
            break  # No matching release — leave as-is
        # Extract the span between hold and release
        inner = result[m.end():rm.start()]
        # Prepend modifier to each {key} in the inner span
        def _prepend_mod(bm, _mod=mod):
            content = bm.group(1)
            return '{' + _mod + '+' + content + '}'
        new_inner = _BRACE_RE.sub(_prepend_mod, inner)
        result = result[:m.start()] + new_inner + result[rm.end():]
        changed = True

    return result
