"""Synthetic-only software checks. Fixtures are not product-quality evidence."""
import copy,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
from PIL import Image
S=importlib.util.spec_from_file_location('suite_gate',Path(__file__).parents[1]/'suite_release_gate.py');G=importlib.util.module_from_spec(S);S.loader.exec_module(G)
class SuiteGateChecks(unittest.TestCase):
 def rec(self,name):return {'path':name,'sha256':hashlib.sha256((self.root/name).read_bytes()).hexdigest()}
 def write(self,name,data):
  (self.root/name).write_text(json.dumps(data));return self.rec(name)
 def setUp(self):
  tmp=tempfile.TemporaryDirectory(prefix='synthetic-suite-gate-');self.addCleanup(tmp.cleanup);self.root=Path(tmp.name)
  Image.new('RGB',(20,20),'white').save(self.root/'source.jpg');source=self.rec('source.jpg')
  cats=[self.write(f'catalog{i}.json',{'sku_color':c,'asset_kind':'real_product_photos'}) for i,c in enumerate(['silver','黑色','枪灰色'])]
  coverage=self.write('coverage.json',{'entries':[{'reference_id':ref,'outputs':['M01'],'disposition':'ADAPTED_OR_MERGED','coverage_status':'CHECKED_IN_CURRENT_SUITE'} for ref in sorted(G.REFERENCES)]})
  self.m={'schema_version':4,'production_state':'EXPERIMENT_ENABLED','source_priority':'OWN_SKU_PHOTOS_PRIMARY_3D_SECONDARY','hard_shape_lock':False,'water_policy':'REAL_PHOTOS_UNASSIGNED_MODES','sku_photo_catalogs':cats,'reference_coverage':coverage,'assets':[]}
  for i,aid in enumerate(sorted(G.EXPECTED)):
   Image.new('RGB',(20,20),(i*10,65,124)).save(self.root/f'{aid}.jpg');jpg=self.rec(f'{aid}.jpg')
   rev=self.write(f'{aid}-review.json',{'status':'PASS','reviewer':'synthetic-only','reviewed_at':'TEST','jpg_sha256':jpg['sha256'],'finding':'SYNTHETIC SOFTWARE CHECK','checks':{k:'PASS' for k in ['product','reference_style','copy','layout','export']}})
   a={'id':aid,'has_model':False,'has_water':False,'refs_actual_viewed':[source],'actual_inputs':[source],'output':jpg,'dims':[20,20],'review':rev}
   if aid.startswith('L'):a['children']=['M01']
   self.m['assets'].append(a)
 def codes(self,stage='review'):return {x['code'] for x in G.evaluate(self.m,self.root,stage)['issues']}
 def test_complete_synthetic_control(self):self.assertEqual(self.codes(),set())
 def test_missing_current_image_is_not_complete(self):
  self.m['assets'].pop();self.assertIn('SUITE_SCOPE',self.codes())
 def test_unconfirmed_water_mode_cannot_be_attached_to_photo(self):
  a=self.m['assets'][0];a.update(has_water=True,water_mode_assignment={'source.jpg':'mist'},water_photo_sources=[self.rec('source.jpg')]);self.assertIn('WATER_MAPPING',self.codes())
 def test_missing_one_reference_cannot_pass_coverage(self):
  p=self.root/'coverage.json';d=json.loads(p.read_text());d['entries'].pop();self.m['reference_coverage']=self.write('coverage.json',d);self.assertIn('REFERENCE_SCOPE',self.codes())
 def test_old_review_cannot_certify_changed_jpg(self):
  a=self.m['assets'][0];Image.new('RGB',(20,20),'yellow').save(self.root/a['output']['path']);a['output']=self.rec(a['output']['path']);self.assertIn('VISUAL_REVIEW',self.codes())
 def test_three_copies_of_one_color_do_not_prove_three_skus(self):
  self.m['sku_photo_catalogs']=[self.m['sku_photo_catalogs'][0]]*3;self.assertIn('SKU_CATALOGS',self.codes())
 def test_customer_acceptance_not_inferred_from_internal_review(self):self.assertIn('CUSTOMER_ACCEPTANCE',self.codes('delivery'))
