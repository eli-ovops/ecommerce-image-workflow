"""Synthetic-only checks for photo-source lineage and bounded typesetting."""
import importlib.util
import copy
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image

SPEC=importlib.util.spec_from_file_location('photo_gate',Path(__file__).parents[1]/'photo_guided_gate.py')
G=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


class PhotoGuidedGateRegression(unittest.TestCase):
    def rec(self,name):
        import hashlib
        return {'path':name,'sha256':hashlib.sha256((self.root/name).read_bytes()).hexdigest()}

    def write(self,name,value):
        (self.root/name).write_text(json.dumps(value))
        return self.rec(name)

    def setUp(self):
        tmp=tempfile.TemporaryDirectory(prefix='photo-guided-gate-software-test-')
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        for name in ['photo1.jpg','photo2.jpg','clay.jpg']:
            Image.new('RGB',(12,12),'white').save(self.root/name)
        catalog=self.write('catalog.json',{'files':[{'id':f'S{i}','project_path':f'photo{i}.jpg','sha256':self.rec(f'photo{i}.jpg')['sha256']} for i in [1,2]]})
        sources=[{'id':f'S{i}','file':self.rec(f'photo{i}.jpg')} for i in [1,2]]
        self.hashes=sorted({x['file']['sha256'] for x in sources})
        self.m={'schema_version':3,'production_state':'EXPERIMENT_ENABLED','task_scope':'THREE_PHOTO_GUIDED_MAIN_IMAGES',
            'source_priority':'OWN_SKU_PHOTOS_PRIMARY_3D_SECONDARY','hard_shape_lock':False,'source_catalog':catalog,
            'appearance_sources':sources,'secondary_geometry_reference':self.rec('clay.jpg'),'assets':[]}
        for i in [1,2,3]:
            key=f'R0{i}';im=Image.new('RGB',(12,12),(20*i,20,20));im.save(self.root/f'{key}-native.png');im.save(self.root/f'{key}.png');im.save(self.root/f'{key}.jpg')
            prompt=self.write(f'{key}-prompt.json',{'text':'SYNTHETIC TEST ONLY'})
            native=self.rec(f'{key}-native.png');candidate=self.rec(f'{key}.png');jpg=self.rec(f'{key}.jpg')
            generation=self.write(f'{key}-generation.json',{'tool':'builtin_image_gen','native_sha256':native['sha256'],
                'prompt_sha256':prompt['sha256'],'appearance_source_sha256':self.hashes})
            review=self.write(f'{key}-review.json',{'status':'PASS','candidate_sha256':candidate['sha256'],'jpg_sha256':jpg['sha256'],
                'appearance_source_sha256':self.hashes,'reviewer':'synthetic-test-only','reviewed_at':'TEST','finding':'SYNTHETIC SOFTWARE CONTROL',
                'checks':{k:'PASS' for k in ['photo_appearance','geometry','reference_style','copy','no_model','export']}})
            self.m['assets'].append({'id':key,'has_person':False,'has_water':False,'appearance_source_ids':['S1','S2'],
                'style_references':[],'prompt':prompt,'generated_native':native,'generation_receipt':generation,
                'candidate':candidate,'client_jpg':jpg,'review':review,'text_edit_regions':[]})

    def codes(self,stage='review'):
        return {i['code'] for i in G.evaluate(self.m,self.root,stage)['issues']}

    def test_valid_software_control(self):
        self.assertEqual(self.codes(),set())

    def test_ai_reference_route_cannot_claim_shape_lock(self):
        self.m['hard_shape_lock']=True
        self.assertIn('FALSE_CONTROL_CLAIM',self.codes())

    def test_replacing_photo_with_unregistered_input_is_rejected(self):
        self.m['appearance_sources'][0]['file']=self.rec('clay.jpg')
        self.assertIn('SOURCE_CATALOG',self.codes())

    def test_product_repainting_outside_text_zone_is_rejected(self):
        p=self.root/'R01.png'
        with Image.open(p) as im:
            im.putpixel((8,8),(255,0,0));im.save(p)
        self.m['assets'][0]['candidate']=self.rec('R01.png')
        self.assertIn('POST_GENERATION_CHANGE',self.codes())

    def test_exempting_most_of_canvas_is_rejected(self):
        self.m['assets'][0]['text_edit_regions']=[[0,0,11,11]]
        self.assertIn('TYPESETTING_SCOPE',self.codes())

    def test_missing_customer_acceptance_still_blocks_delivery(self):
        self.assertIn('CUSTOMER_ACCEPTANCE',self.codes('delivery'))

    def test_uniform_scaling_cannot_enlarge_or_distort(self):
        with self.assertRaises(ValueError):
            G.typesetting_baseline(Image.new('RGB',(10,20)),{'native_transform':{'uniform_scale':2}})

    def test_local_repair_cannot_hide_changes_elsewhere(self):
        asset=self.m['assets'][0]
        with Image.open(self.root/'R01-native.png') as native:
            repaired=native.copy();repaired.putpixel((8,8),(255,0,0));repaired.save(self.root/'repair.png')
        mask=Image.new('L',(12,12));mask.putpixel((0,0),255);mask.save(self.root/'repair-mask.png')
        evidence=self.write('repair-evidence.json',{'synthetic':True})
        asset['local_repair']={'file':self.rec('repair.png'),'mask':self.rec('repair-mask.png'),
            'tool_patch':self.rec('R01-native.png'),'evidence':evidence,
            'base_sha256':asset['generated_native']['sha256'],'tool':'builtin_image_gen'}
        self.assertIn('LOCAL_REPAIR_OUTSIDE_CHANGED',self.codes())

    def use_multisku_batch(self):
        catalogs=[]; sources=[]
        for prefix,color in [('S','银色'),('B','黑色'),('G','枪灰色')]:
            catalogs.append(self.write(f'{prefix}-catalog.json',{'sku_color':'silver' if prefix=='S' else color,'files':[
                {'id':f'{prefix}{i}','project_path':f'photo{i}.jpg','sha256':self.rec(f'photo{i}.jpg')['sha256']}
                for i in [1,2]]}))
            sources.extend({'id':f'{prefix}{i}','file':self.rec(f'photo{i}.jpg')} for i in [1,2])
        template=copy.deepcopy(self.m['assets'][0]); assets=[]
        for n,(key,prefix,color) in enumerate([('R04','S','银色'),('R05','S','银色'),('R06','S','银色'),('K01','B','黑色'),('K02','G','枪灰色')],1):
            a=copy.deepcopy(template); im=Image.new('RGB',(12,12),(n*35,18,29))
            for suffix in ['-native.png','.png','.jpg']:im.save(self.root/f'{key}{suffix}')
            a.update(id=key,sku=color,appearance_source_ids=[f'{prefix}1',f'{prefix}2'],style_references=[self.rec('clay.jpg')],
                generated_native=self.rec(f'{key}-native.png'),candidate=self.rec(f'{key}.png'),client_jpg=self.rec(f'{key}.jpg'))
            generation=json.loads((self.root/template['generation_receipt']['path']).read_text())
            generation['native_sha256']=a['generated_native']['sha256']
            a['generation_receipt']=self.write(f'{key}-generation.json',generation)
            review=json.loads((self.root/template['review']['path']).read_text())
            review.update(candidate_sha256=a['candidate']['sha256'],jpg_sha256=a['client_jpg']['sha256'])
            a['review']=self.write(f'{key}-review.json',review);assets.append(a)
        self.m.update(task_scope='FIVE_PHOTO_GUIDED_DETAILS_AND_SKUS',source_catalogs=catalogs,appearance_sources=sources,assets=assets)

    def test_multisku_batch_uses_own_catalogs(self):
        self.use_multisku_batch()
        self.assertEqual(self.codes(),set())

    def test_black_sku_cannot_reuse_silver_sources(self):
        self.use_multisku_batch()
        self.m['assets'][3]['appearance_source_ids']=['S1','S2']
        self.assertIn('SKU_SOURCE',self.codes())

    def test_multisku_batch_cannot_omit_one_color_catalog(self):
        self.use_multisku_batch()
        self.m['source_catalogs']=self.m['source_catalogs'][:2]
        self.assertIn('SOURCE_CATALOG',self.codes())
