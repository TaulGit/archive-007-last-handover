const fs=require('node:fs');
const html=fs.readFileSync('index.html','utf8').replace('<base href="./dist/">','');
fs.writeFileSync('dist/index.html',html);
