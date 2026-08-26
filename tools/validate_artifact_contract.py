#!/usr/bin/env python3
"""Deterministically validate the documentation-first Artifact contract fixtures."""
from __future__ import annotations
import hashlib, json, sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parents[1]
SCHEMA_PATH=ROOT/'schemas/artifact.schema.json'
VALID_PATH=ROOT/'fixtures/artifact-registry/valid-end-to-end.json'
INVALID_PATH=ROOT/'fixtures/artifact-registry/invalid-artifacts.json'
@dataclass(frozen=True,order=True)
class Issue:
    path:str; constraint:str; message:str

def pointer(parts: Any)->str:
    return '$'+''.join('/'+str(p).replace('~','~0').replace('/','~1') for p in parts)
def schema_issues(artifact:dict[str,Any],schema:dict[str,Any])->list[Issue]:
    return [Issue(pointer(e.absolute_path),str(e.validator),e.message) for e in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(artifact)]
def semantic_issues(artifact:dict[str,Any], index:dict[tuple[str,int],dict[str,Any]])->list[Issue]:
    issues=[]
    identity_parts=artifact.get('artifact_id','').split(':')
    if len(identity_parts)==3 and identity_parts[1]!=artifact.get('artifact_type'):
        issues.append(Issue('$/artifact_type','identityType','artifact_id type segment must equal artifact_type'))
    canonical=json.dumps(artifact.get('payload',{}),sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
    expected_hash='sha256:'+hashlib.sha256(canonical).hexdigest()
    if artifact.get('content_hash')!=expected_hash:
        issues.append(Issue('$/content_hash','contentHash','digest must match the canonical payload'))
    def check_ref(ref,path):
        target=index.get((ref.get('artifact_id'),ref.get('version')))
        if target and ref.get('content_hash')!=target.get('content_hash'):
            issues.append(Issue(path+'/content_hash','referenceIntegrity','digest does not match referenced artifact'))
        if target and ref.get('artifact_type')!=target.get('artifact_type'):
            issues.append(Issue(path+'/artifact_type','referenceType','type does not match referenced artifact'))
    for field in ('inputs','outputs'):
        for i,ref in enumerate(artifact.get(field,[])): check_ref(ref,f'$/{field}/{i}')
    seen=set()
    previous=artifact.get('supersession',{}).get('previous')
    supersedes=[]
    for i,rel in enumerate(artifact.get('relationships',[])):
        aid=rel.get('assertion_id'); path=f'$/relationships/{i}'
        if aid in seen: issues.append(Issue(path+'/assertion_id','uniqueAssertionId','assertion_id must be unique within an artifact'))
        seen.add(aid); target=rel.get('target',{}); check_ref(target,path+'/target')
        if rel.get('type')=='supersedes':
            supersedes.append(target)
            if target.get('artifact_id')!=artifact.get('artifact_id'):
                issues.append(Issue(path+'/target/artifact_id','supersessionIdentity','supersession must retain logical artifact identity'))
            if isinstance(target.get('version'),int) and target['version']>=artifact.get('version',0):
                issues.append(Issue(path+'/target/version','supersessionOrder','superseded version must be older'))
    if supersedes and (previous is None or supersedes[0]!=previous):
        issues.append(Issue('$/supersession/previous','supersessionAgreement','previous and supersedes target must agree'))
    return issues
def validate_artifact(artifact,schema,index): return sorted(schema_issues(artifact,schema)+semantic_issues(artifact,index))
def load(path): return json.loads(path.read_text(encoding='utf-8'))
def validate_contract(root:Path=ROOT)->list[str]:
    schema=load(root/'schemas/artifact.schema.json'); Draft202012Validator.check_schema(schema)
    valid=load(root/'fixtures/artifact-registry/valid-end-to-end.json'); invalid=load(root/'fixtures/artifact-registry/invalid-artifacts.json')
    artifacts=valid['artifacts']; index={(a['artifact_id'],a['version']):a for a in artifacts}; errors=[]
    for i,a in enumerate(artifacts):
        for issue in validate_artifact(a,schema,index): errors.append(f'valid artifact {i} {issue.path} [{issue.constraint}] {issue.message}')
    for case in invalid['cases']:
        issues=validate_artifact(case['artifact'],schema,index); expected=case['expected']
        if not any(i.path==expected['path'] and i.constraint==expected['constraint'] for i in issues):
            errors.append(f"invalid case {case['name']} did not emit {expected['path']} [{expected['constraint']}]")
    return errors
def main()->int:
    errors=validate_contract()
    if errors: print('\n'.join(errors),file=sys.stderr); return 1
    print('artifact contract validation passed (10 valid artifacts, 8 invalid cases rejected)'); return 0
if __name__=='__main__': raise SystemExit(main())
