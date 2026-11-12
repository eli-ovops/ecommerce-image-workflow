"""Synthetic software regression cases, never physical/visual acceptance evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image

SPEC = importlib.util.spec_from_file_location('gate', Path(__file__).parents[1] / 'release_gate.py')
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)

class Regression(unittest.TestCase):
    def write(self, name, data):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data))
        return {'path': name, 'sha256': GATE.digest(p)}

    def record(self, name):
        return {'path': name, 'sha256': GATE.digest(self.root / name)}

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='ecommerce-gate-test-')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        Image.new('RGB', (8, 8), 'gray').save(self.root / 'real.jpg')
        Image.new('RGBA', (8, 8), 'white').save(self.root / 'base.png')
        mask = Image.new('L', (8, 8), 255)
        mask.putpixel((7, 7), 0)
        mask.save(self.root / 'mask.png')
        catalog = self.write('products/主推花洒/银色/manifest.json', {'asset_kind':'real_product_photos',
            'files':[{'id':'REAL','project_path':'real.jpg','sha256':self.record('real.jpg')['sha256']}]})
        self.manifest = {'schema_version':1,'experiment_id':'SYNTHETIC-TEST-ONLY',
            'production_state':'EXPERIMENT_ENABLED','source_catalog':catalog,
            'sources':[{'id':'REAL','kind':'real_photo','sku':'silver','file':self.record('real.jpg')}], 'assets':[]}
        for i in range(1,4):
            key = f'E0{i}'
            im = Image.new('RGBA',(8,8),'white')
            im.putpixel((7,7),(i*60,0,255,255))
            im.save(self.root / f'{key}.png')
            im.convert('RGB').save(self.root / f'{key}.jpg', quality=95)
            asset = {'id':key,'role':'synthetic task','producer':'synthetic-producer',
                'geometry_source_ids':['REAL'],'geometry_route':'photo_locked','local_repairs':0,
                'has_water':key=='E02','has_person':key=='E03','candidate':self.record(f'{key}.png'),
                'protected_baseline':self.record('base.png'),'protected_mask':self.record('mask.png'),
                'client_jpg':self.record(f'{key}.jpg'),'checks':{}}
            required = ['geometry','mask_scope','reference_style','copy'] + (['water'] if i==2 else []) + (['person'] if i==3 else [])
            for check in required:
                data = {'status':'PASS','subject_sha256':asset['candidate']['sha256'],
                    'source_sha256':[self.record('real.jpg')['sha256']], 'asset_id':key,'check_type':check,
                    'experiment_id':self.manifest['experiment_id'],'asset_scope_sha256':GATE.asset_scope_sha256(asset),
                    'protected_baseline_sha256':asset['protected_baseline']['sha256'],
                    'protected_mask_sha256':asset['protected_mask']['sha256'],'reviewer':'synthetic-reviewer',
                    'reviewed_at':'test-only','finding':'SYNTHETIC SOFTWARE CONTROL; not product evidence'}
                asset['checks'][check] = self.write(f'{key}-{check}.json',data)
            asset['export_review'] = self.write(f'{key}-export.json', {'status':'PASS',
                'subject_sha256':asset['client_jpg']['sha256'],'native_sha256':asset['candidate']['sha256'],
                'asset_id':key,'check_type':'export','experiment_id':self.manifest['experiment_id'],
                'reviewer':'synthetic-reviewer','reviewed_at':'test-only','finding':'Synthetic export control'})
            self.manifest['assets'].append(asset)

    def codes(self, stage='review'):
        return {i['code'] for i in GATE.evaluate(self.manifest,self.root,stage)['issues']}

    def change(self, check, key='E01', **changes):
        asset = next(a for a in self.manifest['assets'] if a['id']==key)
        old = asset['checks'][check]
        data = json.loads((self.root / old['path']).read_text())
        data.update(changes)
        asset['checks'][check] = self.write(old['path'],data)

    def accept(self):
        assets=self.manifest['assets']
        receipt=self.root/'receipt.txt';receipt.write_text('SYNTHETIC RECEIPT; SOFTWARE TEST ONLY')
        data={'status':'ACCEPTED','source_sha256':[self.record('real.jpg')['sha256']],
            'experiment_id':self.manifest['experiment_id'],
            'baseline_sha256':sorted({a['protected_baseline']['sha256'] for a in assets}),
            'mask_sha256':sorted({a['protected_mask']['sha256'] for a in assets}),
            'geometry_candidate_sha256':assets[0]['candidate']['sha256'],
            'accepted_jpg_sha256':{a['id']:a['client_jpg']['sha256'] for a in assets},
            'reviewed_at':'test-only','finding':'Synthetic acceptance','receipt':self.record('receipt.txt')}
        self.manifest['baseline_acceptance']=self.write('accept.json',data)

    def test_positive_control_only_proves_software_behavior(self):
        self.assertEqual(self.codes(),set())
    def test_paused_rejected(self):
        self.manifest['production_state']='PAUSED';self.assertIn('PAUSED',self.codes())
    def test_conditional_unknown_failed_unrun_rejected(self):
        for status in ['PASS_WITH_LIMITATIONS','UNKNOWN','FAIL','NOT_RUN']:
            self.change('geometry',status=status);self.assertIn('CHECK_NOT_PASS',self.codes())
    def test_old_candidate_review_rejected(self):
        self.change('geometry',subject_sha256='old');self.assertIn('STALE_REVIEW',self.codes())
    def test_generated_source_rejected(self):
        self.manifest['sources'][0]['kind']='generated_image';self.assertIn('UNSUPPORTED_SOURCE',self.codes())
    def test_fake_real_photo_label_rejected_by_catalog(self):
        a=self.manifest['sources'][0];a['file']=self.record('E01.png');self.assertIn('SOURCE_CATALOG',self.codes())
    def test_self_review_rejected(self):
        self.change('geometry',reviewer='synthetic-producer');self.assertIn('INDEPENDENCE',self.codes())
    def test_changed_product_rgb_rejected(self):
        a=self.manifest['assets'][0]
        with Image.open(self.root/'E01.png') as im:
            im.putpixel((3,3),(0,0,0,255));im.save(self.root/'E01.png')
        a['candidate']=self.record('E01.png');self.assertIn('PRODUCT_CHANGED',self.codes())
    def test_changed_product_alpha_rejected(self):
        a=self.manifest['assets'][0]
        with Image.open(self.root/'E01.png') as im:
            im.putpixel((3,3),(255,255,255,0));im.save(self.root/'E01.png')
        a['candidate']=self.record('E01.png');self.assertIn('PRODUCT_CHANGED',self.codes())
    def test_empty_mask_rejected(self):
        Image.new('L',(8,8),0).save(self.root/'mask.png')
        self.manifest['assets'][0]['protected_mask']=self.record('mask.png');self.assertIn('PIXEL_PROOF',self.codes())
    def test_shrunken_mask_invalidates_old_review(self):
        m=Image.new('L',(8,8),0);m.putpixel((0,0),255);m.save(self.root/'small.png')
        self.manifest['assets'][0]['protected_mask']=self.record('small.png');self.assertIn('STALE_PROTECTION_REVIEW',self.codes())
    def test_swapped_baseline_invalidates_old_review(self):
        self.manifest['assets'][0]['protected_baseline']=self.record('E01.png');self.assertIn('STALE_PROTECTION_REVIEW',self.codes())
    def test_missing_water_review_rejected(self):
        del self.manifest['assets'][1]['checks']['water'];self.assertIn('MISSING_FILE',self.codes())
    def test_water_cannot_be_disabled(self):
        self.manifest['assets'][1]['has_water']=False;self.assertIn('TASK_APPLICABILITY',self.codes())
    def test_person_cannot_be_disabled(self):
        self.manifest['assets'][2]['has_person']=False;self.assertIn('TASK_APPLICABILITY',self.codes())
    def test_unknown_applicability_rejected(self):
        self.manifest['assets'][0]['has_person']=None;self.assertIn('APPLICABILITY',self.codes())
    def test_wrong_check_attachment_rejected(self):
        a=self.manifest['assets'][0];a['checks']['copy']=a['checks']['geometry'];self.assertIn('REVIEW_SCOPE',self.codes())
    def test_wrong_experiment_rejected(self):
        self.change('geometry',experiment_id='other');self.assertIn('REVIEW_SCOPE',self.codes())
    def test_budget_and_modified_source_rejected(self):
        self.manifest['assets'][0]['local_repairs']=3
        (self.root/'real.jpg').write_bytes(b'changed')
        self.assertTrue({'REPAIR_BUDGET','HASH_CHANGED'} <= self.codes())
    def test_review_pass_is_not_customer_acceptance(self):
        self.assertEqual(self.codes(),set());self.assertIn('MISSING_FILE',self.codes('delivery'))
    def test_customer_receipt_required_and_hashed(self):
        self.accept();self.assertEqual(self.codes('delivery'),set())
        (self.root/'receipt.txt').write_text('changed');self.assertIn('HASH_CHANGED',self.codes('delivery'))
    def test_empty_export_cannot_bypass_review(self):
        self.manifest['assets'][0]['export_review']=self.write('empty-export.json',{})
        self.assertIn('EXPORT_REVIEW',self.codes())
    def test_empty_acceptance_cannot_bypass_customer_gate(self):
        self.manifest['baseline_acceptance']=self.write('empty-accept.json',{})
        self.assertIn('CUSTOMER_ACCEPTANCE',self.codes('delivery'))
    def test_old_customer_acceptance_does_not_follow_new_baseline(self):
        self.accept();self.manifest['assets'][0]['protected_baseline']=self.record('E01.png')
        self.assertIn('STALE_CUSTOMER_ACCEPTANCE',self.codes('delivery'))
    def test_old_customer_acceptance_does_not_follow_new_candidate(self):
        self.accept();self.manifest['assets'][0]['candidate']=self.record('E02.png')
        self.assertIn('STALE_CUSTOMER_ACCEPTANCE',self.codes('delivery'))
    def test_duplicate_task_output_rejected(self):
        self.manifest['assets'][1]['candidate']=self.record('E01.png');self.assertIn('DUPLICATE_OUTPUT',self.codes())

if __name__=='__main__':unittest.main()
