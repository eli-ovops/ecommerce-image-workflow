const fs=require('fs'),path=require('path'),crypto=require('crypto');const sharp=require('/Users/USER/.local/share/deepseek-harness/node_modules/sharp');const B=__dirname;
const source=path.resolve(B,'../../products/主推花洒/结构基准20261027/原件/微信图片_20261027161226_345_2.jpg');
(async()=>{
const W=1780,H=980;
const original=await sharp(source).rotate().resize(1824,1368).extract({left:20,top:380,width:W,height:H}).removeAlpha().raw().toBuffer();
// Native local color masks, not silhouette cutouts. All coordinates retain original geometry.
const mask=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><rect width="100%" height="100%" fill="black"/><g transform="translate(-20 -380)" fill="white"><path d="M76 627 Q103 730 337 780 Q593 831 793 786 L764 892 Q545 946 317 890 Q92 847 76 732Z"/><path d="M1110 646 L1640 622 Q1673 652 1665 693 L1130 721Z"/></g></svg>`;
fs.writeFileSync(path.join(B,'金属去杂色蒙版.svg'),mask);
const m=await sharp(Buffer.from(mask)).blur(10).removeAlpha().raw().toBuffer();const out=Buffer.from(original);
for(let i=0;i<out.length;i+=3){const l=.2126*original[i]+.7152*original[i+1]+.0722*original[i+2];for(let c=0;c<3;c++){let v=original[i+c];v=v*(1-.65*m[i]/255)+l*.65*m[i]/255;v=255*Math.pow(v/255,.91);out[i+c]=Math.min(255,Math.round(v));}}
await sharp(original,{raw:{width:W,height:H,channels:3}}).png().toFile(path.join(B,'原照同尺度.png'));
await sharp(out,{raw:{width:W,height:H,channels:3}}).png().toFile(path.join(B,'可追溯像素母版.png'));
await sharp(out,{raw:{width:W,height:H,channels:3}}).jpeg({quality:97,chromaSubsampling:'4:4:4'}).toFile(path.join(B,'斜侧厚度_无字候选.jpg'));
await sharp(out,{raw:{width:W,height:H,channels:3}}).resize(720).jpeg({quality:95}).toFile(path.join(B,'缩略图.jpg'));
await sharp(out,{raw:{width:W,height:H,channels:3}}).extract({left:35,top:40,width:1020,height:570}).jpeg({quality:97,chromaSubsampling:'4:4:4'}).toFile(path.join(B,'侧壁与喷面近景.jpg'));
const a=await sharp(original,{raw:{width:W,height:H,channels:3}}).resize(890).png().toBuffer(),b=await sharp(out,{raw:{width:W,height:H,channels:3}}).resize(890).png().toBuffer();await sharp({create:{width:1792,height:490,channels:3,background:'#fff'}}).composite([{input:a,left:0,top:0},{input:b,left:902,top:0}]).jpeg({quality:96}).toFile(path.join(B,'原照对照_左原右修.jpg'));
fs.writeFileSync(path.join(B,'制作记录.json'),JSON.stringify({source,sha256:crypto.createHash('sha256').update(fs.readFileSync(source)).digest('hex'),operations:['EXIF normalize','whole-image isotropic resize to1824x1368','crop 20,380,1780,980','local metal 65% desaturation with soft source-coordinate mask','gamma .91 exposure correction'],geometryWarp:false,aiCalls:0,hand:'原实拍手持保留，未补画遮挡部位',review:'待用户审阅，不称广告质感通过',files:fs.readdirSync(B)},null,2));
})();
