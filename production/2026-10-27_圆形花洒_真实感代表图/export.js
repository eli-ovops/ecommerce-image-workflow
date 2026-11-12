const fs=require('fs'),path=require('path');const sharp=require('/Users/USER/.local/share/deepseek-harness/node_modules/sharp');
const out=path.join(__dirname,'银色花洒_暖白浴室主图.jpg');if(fs.existsSync(out))throw new Error('Final JPG exists: preserve the selected export; choose a new authorized revision filename.');
sharp(fs.readFileSync(path.join(__dirname,'main-editable.svg'))).jpeg({quality:96,chromaSubsampling:'4:4:4'}).toFile(out).then(info=>console.log(JSON.stringify(info)));
