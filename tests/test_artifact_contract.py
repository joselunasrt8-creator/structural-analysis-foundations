from __future__ import annotations
import copy,json,unittest
from pathlib import Path
from tools.validate_artifact_contract import load, semantic_issues, validate_contract
ROOT=Path(__file__).resolve().parents[1]
class ArtifactContractTests(unittest.TestCase):
    def setUp(self):
        self.fixture=load(ROOT/'fixtures/artifact-registry/valid-end-to-end.json')
        self.index={(a['artifact_id'],a['version']):a for a in self.fixture['artifacts']}
    def test_contract_fixtures(self): self.assertEqual(validate_contract(ROOT),[])
    def test_every_required_relationship_is_exercised(self):
        actual={r['type'] for a in self.fixture['artifacts'] for r in a['relationships']}
        self.assertEqual(actual,{'produced_by','derived_from','supports','contradicts','supersedes','implements','validated_by','authorized_by','executed_as'})
    def test_compressed_chain_references_exact_inputs(self):
        chain=self.fixture['compressed_chain']
        for prior,current in zip(chain,chain[1:]): self.assertIn(prior,self.index[(current['artifact_id'],current['version'])]['inputs'])
    def test_reference_digest_mismatch_is_rejected(self):
        artifact=copy.deepcopy(self.fixture['artifacts'][4]); artifact['inputs'][0]['content_hash']='sha256:'+'0'*64
        self.assertTrue(any(i.constraint=='referenceIntegrity' for i in semantic_issues(artifact,self.index)))
    def test_payload_hashes_use_canonical_json(self):
        import hashlib
        for artifact in self.fixture['artifacts']:
            digest=hashlib.sha256(json.dumps(artifact['payload'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
            self.assertEqual(artifact['content_hash'],'sha256:'+digest)
    def test_identity_type_mismatch_is_rejected(self):
        artifact=copy.deepcopy(self.fixture['artifacts'][4]); artifact['artifact_type']='model_object'
        self.assertTrue(any(i.constraint=='identityType' for i in semantic_issues(artifact,self.index)))
if __name__=='__main__': unittest.main()
