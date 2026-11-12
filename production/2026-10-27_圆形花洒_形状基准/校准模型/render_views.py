import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;F=B/'圆形红钮花洒_银色形状校准_v1.blend';bpy.ops.wm.open_mainfile(filepath=str(F));S=bpy.context.scene;cam=S.camera;O=B/'审查图';O.mkdir(exist_ok=True)
views=[('01_正面',0,.0,.31,(0,.015,.137)),('02_背面',180,0,.31,(0,.015,.137)),('03_右侧',90,0,.31,(0,.015,.137)),('04_左侧',-90,0,.31,(0,.015,.137)),('05_前斜',42,.08,.31,(0,.015,.137)),('06_后斜',138,.08,.31,(0,.015,.137)),('07_头颈局部',55,.015,.19,(0,.018,.185)),('08_圆盘顶边',90,.35,.16,(0,.018,.218))]
files=[]
for name,a,e,scale,t in views:
 T=Vector(t);a=math.radians(a);cam.location=T+Vector((.7*math.sin(a),-.7*math.cos(a),e));cam.rotation_euler=(T-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;S.render.filepath=str(O/(name+'.jpg'));bpy.ops.render.render(write_still=True);files.append(S.render.filepath)
report={'reopened_successfully':True,'blender_version':bpy.app.version_string,'source_blend':str(F),'sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'all_views_from_same_reopened_file':True,'rendered_jpg_files':files,'model_dimensions_mm':{o.name:[round(x*1000,3) for x in o.dimensions] for o in bpy.data.objects if o.type=='MESH'},'dimensions_are_physical_measurements':False}
(B/'reopen-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('REOPEN_RENDER_COMPLETE')
