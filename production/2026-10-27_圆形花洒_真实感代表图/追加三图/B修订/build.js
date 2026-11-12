const fs=require('fs'),path=require('path'),sharp=require('/Users/USER/.local/share/deepseek-harness/node_modules/sharp');
const B=__dirname,P=path.resolve(B,'../..');
const template=path.join(B,'sources/base-layout.svg');if(!fs.existsSync(template))fs.copyFileSync(path.join(P,'main-editable.svg'),template);
let svg=fs.readFileSync(template,'utf8').replace('translate(900 900) rotate(110) scale(.83) translate(-950 -679)','translate(750 920) rotate(100) scale(1.38) translate(-540 -679)').replaceAll('按压除垢','中央红钮').replace('三档出水 · 随手切换','手动按压 · 辅助除垢').replace('H662 L647','H662 L647');
// No retouch layer used: button and handle naturally exit below frame.
svg=svg.replace(/<image xlink:href="[^"]*" width="1824" height="1368" mask="url\(#reflection\)"\/>/,'');
fs.writeFileSync(path.join(B,'B-editable.svg'),svg);
(async()=>{await sharp(Buffer.from(svg)).png().toFile(path.join(B,'preview.png'));await sharp(Buffer.from(svg)).resize(360).png().toFile(path.join(B,'phone.png'));})();
