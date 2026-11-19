const {chromium}=require('playwright-core');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true,args:['--enable-unsafe-swiftshader']});
 try{
  const page=await browser.newPage();const errors=[];
  page.on('pageerror',err=>errors.push(err.message));
  await page.goto(process.env.GAME_URL||'http://127.0.0.1:7421/',{waitUntil:'domcontentloaded'});
  const button=name=>page.getByRole('button',{name,exact:true});
  await button('拼合报废单').waitFor();
  assert.equal(await page.locator('#overlay').isVisible(),false);
  const canvas=page.locator('#world');
  const before=await canvas.screenshot();
  await page.mouse.move(400,320);await page.mouse.down();await page.mouse.move(560,330);await page.mouse.up();
  assert.deepEqual(await canvas.screenshot(),before,'鼠标拖动不应改变视角');
  for(const action of ['拼合报废单','核对签名','重听家庭留言','接起内线','接通外线','与 008 交接','走出北门']){
   await button(action).click();
   assert.equal(await page.locator('#choices button').count(),1);
   await page.locator('#choices button').click();
  }
  await button('拼合报废单').waitFor();assert.deepEqual(errors,[]);
  console.log('直接入场、固定视角拖动检查、七个主线节点、结局和重玩通过');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
