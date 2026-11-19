const {chromium}=require('playwright-core');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true,args:['--enable-unsafe-swiftshader']});
 try{
  const page=await browser.newPage();const errors=[];
  page.on('pageerror',err=>errors.push(err.message));
  await page.goto(process.env.GAME_URL||'http://127.0.0.1:7421/',{waitUntil:'domcontentloaded'});
  const button=name=>page.getByRole('button',{name,exact:true});
  for(const name of ['夜班','签收','今晚的工单']){
   await page.getByRole('heading',{name,exact:true}).waitFor();
   await button(name==='今晚的工单'?'进入档案室':'下一张').click();
  }
  await button('拼合报废单').waitFor();
  assert.equal(await page.locator('#overlay').isVisible(),false);
  const canvas=page.locator('#world');
  const before=await canvas.screenshot();
  await page.keyboard.down('ArrowRight');await page.waitForTimeout(350);await page.keyboard.up('ArrowRight');
  assert.ok(!(await canvas.screenshot()).equals(before),'方向键应转身');
  await button('前往目标').click();
  await button('右转').click();assert.ok(!(await canvas.screenshot()).equals(before),'屏幕转身键应即时生效');
  await button('前往目标').click();await page.mouse.click(450,300);
  await page.waitForFunction(()=>document.pointerLockElement===document.querySelector('canvas'));
  await page.mouse.move(620,340,{steps:6});assert.ok(!(await canvas.screenshot()).equals(before),'移动鼠标应环视');
  await page.evaluate(()=>document.exitPointerLock());await button('前往目标').click();
  for(const action of ['拼合报废单','核对签名','重听家庭留言','接起内线','接通外线','与 008 交接','走出北门']){
   await button(action).click();
   assert.equal(await page.locator('#choices button').count(),1);
   await page.locator('#choices button').click();
  }
  await button('拼合报废单').waitFor();assert.deepEqual(errors,[]);
  await page.reload({waitUntil:'domcontentloaded'});await button('跳过前情').click();await button('拼合报废单').waitFor();
  console.log('前情翻页与跳过、三种转向、七个主线节点、结局和重玩通过');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
