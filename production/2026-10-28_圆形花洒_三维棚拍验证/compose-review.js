const fs=require('fs'),path=require('path'),sharp=require('/Users/USER/.local/share/deepseek-harness/node_modules/sharp');
const B=__dirname,ROOT=path.resolve(B,'../..');
(async()=>{
const raw=await sharp(path.join(B,'sources/photo339.jpg')).extract({left:400,top:850,width:5100,height:2500}).png().toBuffer();
const photo=await sharp(raw).rotate(90).resize(700,1400,{fit:'contain',background:'#eeeeee'}).png().toBuffer();
const clay=await sharp(path.join(B,'front-clay.png')).resize(1000,1400).png().toBuffer();
const label=Buffer.from('<svg width="1700" height="100"><rect width="1700" height="100" fill="#eeeeee"/><text x="30" y="42" font-family="Arial" font-size="26">339 photo | uniform crop / rotation / scale</text><text x="760" y="42" font-family="Arial" font-size="26">Reopened model | front orthographic clay</text><text x="30" y="82" font-family="Arial" font-size="22">Approximate view comparison, not calibrated camera matching or dimensional proof.</text></svg>');
await sharp({create:{width:1700,height:1500,channels:3,background:'#eeeeee'}}).composite([{input:label,top:0,left:0},{input:photo,top:100,left:0},{input:clay,top:100,left:700}]).jpeg({quality:93}).toFile(path.join(B,'实拍与灰模对照.jpg'));
await sharp(path.join(B,'studio-exposure-corrected.png')).resize(400).png().toFile(path.join(B,'phone-preview.png'));
})();
