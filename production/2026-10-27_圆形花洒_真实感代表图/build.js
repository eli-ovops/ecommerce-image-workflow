const fs=require('fs'); const path=require('path');
const sharp=require('/Users/USER/.local/share/deepseek-harness/node_modules/sharp');
const B=__dirname, S=path.join(B,'sources');
const root=path.resolve(B,'../..');
const original=path.join(root,'products/主推花洒/结构基准20261027/原件/微信图片_20261027161143_339_2.jpg');
const bgOriginal='/Users/USER/.codex/generated_images/01a17c88-9784-7202-9a4a-0bf7830010e6/exec-2cbd5e3e-7168-45d9-85f9-de6838412129.png';
const retouchOriginal='/Users/USER/.codex/generated_images/01a17c88-9784-7202-9a4a-0bf7830010e6/exec-37a5ad89-f69a-467e-8f0e-a929dc705502.png';
for(const [src,dst] of [[original,'product-original-339.jpg'],[bgOriginal,'background-native.png'],[retouchOriginal,'reflection-retouch-native.png']]) if(!fs.existsSync(path.join(S,dst))) fs.copyFileSync(src,path.join(S,dst));
const data=(f,m)=>`data:${m};base64,${fs.readFileSync(path.join(S,f)).toString('base64')}`;
const outline='M 540 303 C 414 300 307 355 226 461 C 157 551 140 641 157 753 C 176 888 261 987 384 1033 C 492 1076 616 1053 711 1007 C 795 966 844 900 898 843 C 945 795 1010 780 1096 770 C 1270 756 1485 762 1658 760 Q 1675 758 1681 744 L 1687 730 C 1708 735 1736 735 1745 723 C 1754 702 1753 642 1745 621 C 1738 608 1711 607 1685 613 L 1680 601 Q 1673 583 1656 584 C 1480 583 1264 595 1080 579 C 984 571 918 536 860 476 C 766 369 678 306 540 303 Z';
const metal='M 1104 602 C 1278 613 1485 600 1658 601 Q 1669 603 1670 617 L 1670 734 Q 1668 742 1657 744 C 1480 744 1252 750 1106 755 L 1084 759 C 1106 725 1117 688 1110 648 Q 1108 620 1104 602 Z';
const button='M 953 631 C 978 625 1014 627 1037 636 C 1062 645 1068 668 1064 695 C 1059 719 1045 727 1018 728 L 953 728 C 930 725 923 716 923 692 L 924 660 Q 925 638 953 631 Z';
fs.writeFileSync(path.join(B,'product-mask.svg'),`<svg xmlns="http://www.w3.org/2000/svg" width="1824" height="1368"><path d="${outline}" fill="white"/></svg>`);
fs.writeFileSync(path.join(B,'reflection-mask.svg'),`<svg xmlns="http://www.w3.org/2000/svg" width="1824" height="1368"><path d="${metal}" fill="white"/><path d="${button}" fill="white"/></svg>`);
const svg=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1440" height="1440" viewBox="0 0 1440 1440">
<defs>
<clipPath id="product"><path d="${outline}"/></clipPath>
<filter id="feather" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="2.4"/></filter>
<mask id="reflection"><rect width="1824" height="1368" fill="black"/><g filter="url(#feather)" fill="white"><path d="${metal}"/><path d="${button}"/></g></mask>
<filter id="softShadow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="19"/></filter>
<filter id="contactShadow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="4"/></filter>
</defs>
<image xlink:href="${data('background-native.png','image/png')}" width="1440" height="1440"/>
<g transform="translate(900 900) rotate(110) scale(.83) translate(-950 -679)">
<path d="${outline}" fill="#5d4f41" opacity=".20" filter="url(#softShadow)" transform="translate(20 21)"/>
<path d="${outline}" fill="#463d34" opacity=".23" filter="url(#contactShadow)" transform="translate(4 5)"/>
<g clip-path="url(#product)">
<image xlink:href="${data('product-original-339.jpg','image/jpeg')}" width="1824" height="1368"/>
<image xlink:href="${data('reflection-retouch-native.png','image/png')}" width="1824" height="1368" mask="url(#reflection)"/>
</g></g>
<g transform="translate(82 55) skewX(-9)"><text x="12" y="137" font-family="Heiti SC" font-size="140" font-weight="bold" fill="#c7aa7d" stroke="#c7aa7d" stroke-width="5">按压除垢</text><text x="8" y="132" font-family="Heiti SC" font-size="140" font-weight="bold" fill="#241c17" stroke="#241c17" stroke-width="4">按压除垢</text></g>
<path d="M82 241 H662 L647 319 H67 Z" fill="#c9ae83"/>
<path d="M85 236 H653 L640 310 H72 Z" fill="#805336"/>
<text x="104" y="288" font-family="Heiti SC" font-size="45" font-weight="bold" fill="#fff9ee">三档出水 · 随手切换</text>
</svg>`;
fs.writeFileSync(path.join(B,'main-editable.svg'),svg);
(async()=>{await sharp(Buffer.from(svg)).png().toFile(path.join(S,'review-preview.png'));await sharp(Buffer.from(svg)).resize(360,360).png().toFile(path.join(S,'phone-preview.png'));console.log('PREVIEW_RENDERED')})().catch(e=>{console.error(e);process.exit(1)});
