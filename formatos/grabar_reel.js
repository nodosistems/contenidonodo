// Graba un reel HTML (que expone window.renderAt(ms) y window.DURACION) a frames PNG y MP4.
// Uso: NODE_PATH=/opt/node22/lib/node_modules node grabar_reel.js <reel.html> <salida.mp4> [audio.m4a]
const {chromium}=require('playwright'); const fs=require('fs'); const path=require('path'); const {execSync}=require('child_process');
(async()=>{
  const [html,out,audio]=process.argv.slice(2); const fps=30;
  const dir=fs.mkdtempSync(path.join(require('os').tmpdir(),'frames-'));
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  await pg.goto('file://'+path.resolve(html)); await pg.evaluate(()=>document.fonts.ready); await pg.waitForTimeout(300);
  const dur=await pg.evaluate(()=>window.DURACION); const N=Math.round(dur/1000*fps);
  for(let i=0;i<N;i++){ await pg.evaluate(t=>window.renderAt(t), i*1000/fps); await pg.screenshot({path:`${dir}/${String(i).padStart(4,'0')}.png`}); }
  await b.close();
  const a = audio ? `-i "${audio}" -c:a aac -b:a 160k -shortest` : '';
  execSync(`ffmpeg -loglevel error -y -framerate ${fps} -i ${dir}/%04d.png ${a} -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart "${out}"`);
  fs.rmSync(dir,{recursive:true,force:true}); console.log('ok', out, (dur/1000).toFixed(1)+'s', N,'frames');
})();
