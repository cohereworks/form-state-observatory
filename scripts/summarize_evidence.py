"""Emit a GitHub Actions job summary from one browser evidence JSON file.

Research tests intentionally do not gate on speculative feature hypotheses.
"""
import json
import sys
from pathlib import Path

def render(path: Path) -> str:
    if not path.exists():
        return f'### Browser evidence unavailable\n\nNo evidence at `{path}`. Inspect logs.\n'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return f'### Browser evidence unreadable\n\n`{type(exc).__name__}` — inspect logs.\n'
    browser = data.get('browser', 'unknown')
    version = data.get('browserVersion', 'unknown')
    lines = [f'### {browser} {version}: browser-native state observations', '',
             '| Probe | Outcome |', '|---|---|']
    cases = data.get('cases', {})
    if data.get('fatal'):
        lines.append(f"| Fatal stage | `{data['fatal'].get('stage', 'unknown')}` |")
    for key, title in [('metric', 'Metric decoding'),
                       ('contextOrder', 'Order-sensitive shaping'),
                       ('manualAddressResult', 'Manual ADDR axis'),
                       ('scrollProgressResult', 'Scroll timeline'),
                       ('scrollAddressResult', 'Scroll-driven ADDR')]:
        outcome = cases.get(key, {}).get('classification', 'not captured')
        lines.append(f'| {title} | {outcome} |')
    for mode in ('liga', 'calt'):
        values = cases.get('tokenAssessment', {}).get(mode, {})
        states = [v.get('classification', 'unknown') for v in values.values()]
        aggregate = ('not captured' if not states else
                     states[0] if len(set(states)) == 1 else 'mixed: inspect JSON')
        lines.append(f'| Token shaping and decoding ({mode}) | {aggregate} |')
    canary = cases.get('containerQueryCanary', {}).get('probes', {})
    for name, info in canary.items():
        lines.append(f"| Container query: {name} | {'matched' if info.get('matched') else 'not matched'} ({info.get('boxWidth', '?')}px) |")
    dynamic = cases.get('dynamicContainerInvalidation', {})
    if dynamic:
        lines.append(f"| Dynamic anchored container width | {'responded' if dynamic.get('widthResponded') else 'not observed'} |")
        lines.append(f"| Dynamic CSS-query invalidation | {'responded' if dynamic.get('cssResponded') else 'not observed'} |")
    lines += ['', 'Research observations are non-gating. JSON, screenshots, and traces in workflow artifacts are authoritative.', '']
    return '\n'.join(lines)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python scripts/summarize_evidence.py <path-to-evidence.json>')
    print(render(Path(sys.argv[1])))
