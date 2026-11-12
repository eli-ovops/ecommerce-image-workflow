const fs = require('fs');
const sharp = require('/Users/USER/.local/share/deepseek-harness/node_modules/sharp');
const path = require('path');
const dir = __dirname;
const orig = path.resolve(dir, '../../products/主推花洒/结构基准20261027/原件/微信图片_20261027161143_339_2.jpg');
const data = (file, mime) => `data:${mime};base64,${fs.readFileSync(file).toString('base64')}`;
const mask = fs.readFileSync(path.join(dir, '实拍轮廓蒙版.svg'), 'utf8');
const outline = mask.match(/<path d="([^"]+)"/)[1];
const bg = data(path.join(dir, '背景原图.png'), 'image/png');
const photo = data(orig, 'image/jpeg');
const svg = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1254" height="1254" viewBox="0 0 1254 1254">
<defs><clipPath id="product"><path d="${outline}"/></clipPath>
<filter id="shadow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="21"/></filter>
<filter id="contact" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5"/></filter>
<filter id="metalLight"><feComponentTransfer><feFuncR type="linear" slope="1.25" intercept="0.08"/><feFuncG type="linear" slope="1.21" intercept="0.07"/><feFuncB type="linear" slope="1.16" intercept="0.05"/></feComponentTransfer></filter><filter id="blendEdge"><feGaussianBlur stdDeviation="3"/></filter><mask id="metalMask"><rect width="1824" height="1368" fill="black"/><g fill="white" filter="url(#blendEdge)"><path d="M 1104 602 C 1278 613 1485 600 1658 601 Q 1669 603 1670 617 L 1670 734 Q 1668 742 1657 744 C 1480 744 1252 750 1106 755 L 1084 759 C 1106 725 1117 688 1110 648 Q 1108 620 1104 602 Z"/><path d="M 953 631 C 978 625 1014 627 1037 636 C 1062 645 1068 668 1064 695 C 1059 719 1045 727 1018 728 L 953 728 C 930 725 923 716 923 692 L 924 660 Q 925 638 953 631 Z"/></g></mask><linearGradient id="gold" x2="0" y2="1"><stop stop-color="#fff4d5"/><stop offset="1" stop-color="#dda456"/></linearGradient></defs>
<image xlink:href="${bg}" width="1254" height="1254"/>
<g transform="translate(340 545) rotate(27) scale(.68) translate(-535 -680)">
<path d="${outline}" transform="translate(30 40)" fill="#633d20" opacity=".28" filter="url(#shadow)"/>
<path d="${outline}" transform="translate(8 11)" fill="#423126" opacity=".34" filter="url(#contact)"/>
<image xlink:href="${photo}" width="1824" height="1368" clip-path="url(#product)"/><image xlink:href="${photo}" width="1824" height="1368" mask="url(#metalMask)" filter="url(#metalLight)"/>
</g>
<g transform="translate(640 92) skewX(-7)" font-family="Heiti SC, PingFang SC, sans-serif" font-weight="900" paint-order="stroke fill">
<text x="6" y="151" font-size="126" fill="#653217" stroke="#fff4d5" stroke-width="5">三档出水</text>
<text x="6" y="151" font-size="126" fill="#633316" stroke="#ffe1a3" stroke-width="1">三档出水</text>
<path d="M0 203 H575 L560 291 H-15 Z" fill="#743e24"/>
<text x="13" y="267" font-size="70" fill="#fff4df">按键切换</text></g></svg>`;
fs.writeFileSync(path.join(dir, '可编辑合成.svg'), svg);
(async()=>{ await sharp(Buffer.from(svg)).jpeg({quality:95, chromaSubsampling:'4:4:4'}).toFile(path.join(dir,'实拍整件_广告候选.jpg')); console.log('OK'); })().catch(e=>{console.error(e);process.exit(1)});
