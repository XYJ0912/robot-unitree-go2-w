"""Read-only package checks. No network, dependency installation, build or robot access."""
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote

root = Path(__file__).resolve().parents[1]
required = ['README.md', 'START_AGENT_PROMPT.md', 'CURRENT_RESULTS.md',
            'LOCAL_PREPARATION.md', 'INTEGRATION_RESULT_TEMPLATE.md', 'HANDOFF.md',
            'SOURCE_VERSION.json', 'patches/executor-lifecycle.patch',
            'source/robonix/Cargo.toml', 'source/robonix/Cargo.lock',
            'source/robonix/AGENTS.md', 'source/robonix/LICENSE',
            'source/robonix/system/executor/src/lifecycle.rs',
            'source/robonix/pylib/robonix-api/pyproject.toml',
            'evidence/main-acceptance.export.json']
missing = [rel for rel in required if not (root / rel).is_file()]
version = json.loads((root / 'SOURCE_VERSION.json').read_text(encoding='utf-8'))
submodules = {rel: any(p.is_file() for p in (root / 'source/robonix' / rel).rglob('*'))
              for rel in version['submodules']}
links = []
for path in list(root.glob('*.md')) + list((root / 'reports').glob('*.md')):
    content = path.read_text(encoding='utf-8')
    for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', content):
        target = target.strip('<>').split('#', 1)[0]
        if not target or '://' in target or target.startswith('mailto:'):
            continue
        resolved = (path.parent / unquote(target)).resolve()
        if not resolved.is_relative_to(root) or not resolved.exists():
            links.append({'file': str(path.relative_to(root)), 'target': target})
main = (root / 'source/robonix/system/executor/src/main.rs').read_text(encoding='utf-8')
gate = (root / 'source/robonix/system/executor/src/lifecycle.rs').read_text(encoding='utf-8')
result = {'passed': not missing and not links and all(submodules.values())
          and version['patch_applied_to_bundled_source']
          and 'RobonixLifecycleDriverServer' in main and 'accepting: false' in gate,
          'missing_files': missing, 'broken_handoff_links': links,
          'submodule_source_present': submodules,
          'lifecycle_patch_in_source': 'RobonixLifecycleDriverServer' in main and 'accepting: false' in gate,
          'git_metadata_present': (root / 'source/robonix/.git').exists(),
          'scope': 'Package readiness only; not build success or robot acceptance.'}
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if result['passed'] else 1)
