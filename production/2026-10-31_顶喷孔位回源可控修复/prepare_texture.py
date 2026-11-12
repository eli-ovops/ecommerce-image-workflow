from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,csv,json
P=Path(__file__).resolve().parent
W,H=2400,1600
# Planar object-space registration from the existing photo-candidate circle table.
x=np.linspace(-.1474,.1474,W);y=np.linspace(.0974,-.0974,H);xx,yy=np.meshgrid(x,y)
src=Image.open(P/'372-front-rectified.jpg').convert('L')
sx=123/.0202;sy=60.7/.0101
image=src.transform((W,H),Image.Transform.AFFINE,(.2948*sx/W,0,903-.1474*sx,0,.1948*sy/H,590.6-.0974*sy),resample=Image.Resampling.BICUBIC)
raw=np.asarray(image.filter(ImageFilter.GaussianBlur(1.2)),dtype=float)/255
low=np.asarray(image.filter(ImageFilter.GaussianBlur(24)),dtype=float)/255
detail=np.clip((raw-low)*2.2,-.5,.5)
mask=np.ones_like(detail)
for a in csv.DictReader((P/'hole-map.csv').open()):
 d=np.hypot(xx-float(a['x_mm'])*.001,yy-float(a['y_mm'])*.001)
 mask*=np.clip((d-.0026)/.0007,0,1)
mask*=np.clip((np.hypot(xx,yy)-.014)/.003,0,1)
mask*=np.clip((.140-np.abs(xx))/.005,0,1)*np.clip((.090-np.abs(yy))/.005,0,1)
height=np.uint8(np.clip(.5+detail*mask,0,1)*255)
Image.fromarray(height).save(P/'372_registered_relief.png')
Image.fromarray(np.uint8(mask*255)).save(P/'photo_feature_mask.png')
(P/'texture-method.json').write_text(json.dumps({'source':'372-front-rectified.jpg derived from original372','purpose':'Non-color normal-height approximation only, not albedo or emission','large_scale_illumination_removed':'24px Gaussian high pass at2400x1600','photo_circle_exclusion_radius_m':[.0026,.0033],'red_knob_exclusion_radius_m':[.014,.017],'planar_registration':{'x0_px':903,'y0_px':590.6,'x_pixels_per_m':sx,'y_pixels_per_m':sy},'limitations':'Photographic shading remains in high frequency; not measured height. Circle registration is approximate; visual double-image check required.'},indent=2))
