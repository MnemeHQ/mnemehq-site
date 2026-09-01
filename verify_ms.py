import json, sys, subprocess

result = subprocess.run([
    'curl.exe', '-s', '-X', 'POST', 
    'https://mneme-audit-api-842519822929.us-central1.run.app/api/audit',
    '-F', 'repository_url=https://github.com/microsoft/agent-governance-toolkit'
], capture_output=True, text=True)

d = json.loads(result.stdout)
print(f'Total: {d["summary"]["totalDecisions"]}')
print(f'Enforceable: {d["summary"]["enforceable"]}')
print(f'Partial: {d["summary"]["partial"]}')
print(f'Guidance: {d["summary"]["guidance"]}')
print(f'By Category: {d["summary"].get("byCategory", {})}')
print()
print("Sample decisions (first 10):")
for dec in d['decisions'][:10]:
    print(f'  [{dec["governability"]}] {dec["title"]} (cat: {dec["category"]})')
    if dec['proposedRule']:
        print(f'    Proposed: {dec["proposedRule"]["type"]} {dec["proposedRule"]["pattern"]}')