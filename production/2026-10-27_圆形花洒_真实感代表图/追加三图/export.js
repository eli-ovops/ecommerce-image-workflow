const fs=require('fs'),path=require('path'),sharp=require('/Users/USER/.local/share/deepseek-harness/node_modules/sharp');
const names={A:'A_下键切档.jpg',B:'B_红钮细节.jpg',C:'C_圆盘厚边.jpg'};
(async()=>{for(let k of (process.argv[2]||'ABC')){const out=path.join(__dirname,names[k]);if(fs.existsSync(out))throw new Error('Selected JPG already exists; preserve it: '+out);let info=await sharp(fs.readFileSync(path.join(__dirname,k+'-editable.svg'))).jpeg({quality:96,chromaSubsampling:'4:4:4'}).toFile(out);console.log(k,JSON.stringify(info))}})().catch(e=>{console.error(e);process.exit(1)});
