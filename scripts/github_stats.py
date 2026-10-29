"""Builds site/data/orbit.json: real GitHub numbers that drive the "outros projetos" orbit.

For each project: my commits (size of the disc), when the repo was created (which ring)
and my last activity (how fast it turns). Runs locally with `gh` or in a GitHub Action
with GH_TOKEN set; only public data is read.
"""
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

USER = 'EduardoPaim5'
# disc index in the page -> repository
REPOS = ['EduardoPaim5/pulseapi', 'EduardoPaim5/Nexilum', 'EduardoPaim5/jungle-backend-challenge', 'EduardoPaim5/betalent-payments-api',
         'EduardoPaim5/performance-reproducibility', 'EduardoPaim5/pvault', 'EduardoPaim5/edge-cloud-task-allocation-simulator', 'Thoth2023/thoth-remake']


def gh(path):
    out = subprocess.run(['gh', 'api', path], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def my_commits(repo):
    for page in range(1, 6):
        people = gh(f'repos/{repo}/contributors?per_page=100&page={page}')
        for p in people:
            if p['login'].lower() == USER.lower():
                return p['contributions']
        if len(people) < 100:
            break
    return 0


def main():
    now = datetime.now(timezone.utc)
    items = []
    for i, repo in enumerate(REPOS):
        info = gh(f'repos/{repo}')
        last = gh(f'repos/{repo}/commits?author={USER}&per_page=1')
        last_at = last[0]['commit']['author']['date'] if last else info['pushed_at']
        items.append({
            'i': i, 'repo': repo, 'commits': my_commits(repo), 'created': info['created_at'], 'last': last_at,
            'days_idle': (now - datetime.fromisoformat(last_at.replace('Z', '+00:00'))).days,
        })
    out = Path(os.environ.get('ORBIT_OUT') or Path(__file__).resolve().parent.parent / 'site' / 'data' / 'orbit.json')
    out.write_text(json.dumps({'generated': now.isoformat(timespec='seconds'), 'projects': items}, indent=1))
    for it in items:
        print(f"{it['repo']:52} commits={it['commits']:4} idle={it['days_idle']:4}d created={it['created'][:10]}")


if __name__ == '__main__':
    main()
