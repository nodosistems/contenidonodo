// Renderiza láminas estáticas 1080×1350 desde un JSON: {"laminas":[{formato:...}, ...]}
// Uso: NODE_PATH=/opt/node22/lib/node_modules node render_estatico.js pieza.json <carpeta_salida>
const {chromium}=require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{
  const [json,out]=process.argv.slice(2); const P=JSON.parse(fs.readFileSync(json,'utf8'));
  fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
  await pg.goto('file://'+path.join(__dirname,'estaticos.html')); await pg.evaluate(()=>document.fonts.ready);
  for(const [i,L] of P.laminas.entries()){ await pg.evaluate(L=>window.pintar(L),L); await pg.waitForTimeout(80);
    await pg.screenshot({path:path.join(out,String(i+1).padStart(2,'0')+'.png')}); }
  await b.close(); console.log('ok',P.laminas.length,'láminas →',out);
})();
