import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const $=id=>document.getElementById(id);
const stations={
 shred:['档案室 · 碎纸机',-14.7,5.75], files:['人事室 · 签收副本',0,5.75],
 tape:['宿舍 · 家庭留言',-12,-8.2], tools:['维修间 · 外传线路',-2,-8.4],
 hand:['交接室 · 008',11,5.75], panel:['控制室 · 调度台',14,-5.75],
 north:['交接室 · 放行门',15.1,9.7],south:['控制室 · 维修出口',15.1,-9.7]
};
const beats=[
 ['shred',1,'拼合报废单','两条纸带','我把两个撕口合在一起。报废对象一栏，是我的名字。编号 007，今晚交接后生效。经办人的签名很眼熟。'],
 ['files',2,'核对签名','折起的表头','我把 006 的黄页举到灯前。“终止服务”四个字藏在折痕里。下面是我的笔迹。入职那天，我以为自己签的是设备收据。我把原件收进口袋。'],
 ['tape',2,'重听家庭留言','同一声水壶响','“回来前说一声，我给你留灯。”三盘磁带标着不同的日期，水壶却总在同一个字上响起来。最后一盘多录了半句：“好了，换下一位。”'],
 ['hand',3,'接起内线','第八位夜班员','交接窗后的人用我的声音问：“做完就能回家吗？”他翻出工牌。008。我递过那张黄页，让他看清我的签名。他把笔放下：“那我们能把这张纸带出去吗？”'],
 ['tools',4,'接通外线','门外有人','我接通楼外的回路。许临听见 006 的编号，沉默了一会儿。“他借我的笔还没还。你把原件带来，我在北门等。”'],
 ['panel',5,'与 008 交接','第一次回执','008 自己敲完报文。打印机吐出一行字：“北门已收。”他把原件塞回我手里：“你去交给许临。最后这几页，我来发。”'],
 ['north',5,'走出北门','最后一次交接','许临在清晨的站牌下接过原件。维修门响了，008 捏着外传回执跑过来。第一辆班车还没到。他借走那支笔，在工牌背面写下了自己选的名字。']
];
let step=0,busy=true,finished=false,target=false,panelMode='';
let pos={x:0,z:0},yaw=0,pitch=-.16;
const keys=new Set(),solids=[],scene=new T.Scene(),camera=new T.PerspectiveCamera(67,1,.05,85);
let renderer;
const world=$('world');
function show(tag,title,body,action,callback){
 busy=true;keys.clear();$('overlay').hidden=false;$('hud').hidden=true;
 $('tag').textContent=tag;$('title').textContent=title;$('copy').textContent=body;
 const button=document.createElement('button');button.textContent=action;button.onclick=callback;
 $('choices').replaceChildren(button);button.focus();
}
function resume(){busy=false;panelMode='';$('overlay').hidden=true;$('hud').hidden=false;
 const [id,chapter,action]=beats[step];$('chapter').textContent='档案员 007　／　第 '+chapter+' 章';
 $('goal').textContent=stations[id][0]+'　·　'+action;
}
function arrive(){
 const [id]=beats[step], [,x,y]=stations[id];
 const approach=(id==='tape'||id==='tools'||id==='panel')?1:-1;
 pos={x,z:-(y+approach*1.6)};yaw=approach===1?Math.PI:0;pitch=-.19;target=true;
 resume();update(0);
}
function interact(){
 if(!target){arrive();return}
 const [id,,action,title,body]=beats[step];
 finished=step===beats.length-1;panelMode='story';
 show(stations[id][0]+'　／　'+action,title,body,finished?'重新值班':'继续主线',()=>{
 step=finished?0:step+1;finished=false;arrive();
 });
}
function journal(){panelMode='journal';show('档案 007','调查手记',beats.slice(0,step).map(b=>b[3]+'　'+b[4]).join('\n\n')||'今天的最后一项工单：检查卡纸的碎纸机。','返回现场',resume)}
$('map').textContent='前往目标';$('map').onclick=arrive;$('journal').onclick=journal;$('prompt').onclick=interact;
function blocked(x,z){return Math.abs(x)>17.8||Math.abs(z)>11||solids.some(b=>x>b.min.x-.2&&x<b.max.x+.2&&z>b.min.z-.2&&z<b.max.z+.2)}
function update(dt){
 if(!busy){const val=k=>Number(keys.has(k)),f=val('KeyW')-val('KeyS'),s=val('KeyD')-val('KeyA');
 yaw+=(val('ArrowLeft')-val('ArrowRight'))*dt*1.9;const stride=dt*3/Math.max(1,Math.hypot(f,s));
 const x=pos.x+(-Math.sin(yaw)*f+Math.cos(yaw)*s)*stride,z=pos.z+(-Math.cos(yaw)*f-Math.sin(yaw)*s)*stride;
 if(!blocked(x,pos.z))pos.x=x;if(!blocked(pos.x,z))pos.z=z;
 const [,a,b]=stations[beats[step][0]],dx=a-pos.x,dz=-b-pos.z;
 target=Math.hypot(dx,dz)<2.7&&(-Math.sin(yaw)*dx-Math.cos(yaw)*dz)>.2;
 $('prompt').textContent=target?beats[step][2]:'面向当前目标';
 }
 camera.position.set(pos.x,1.67,pos.z);camera.rotation.set(pitch,yaw,0,'YXZ');
}
onkeydown=e=>{if(e.repeat)return;if(busy){if(e.code==='Escape'&&panelMode==='journal')resume();return}
 keys.add(e.code);if(e.code==='KeyE')interact();if(e.code==='KeyJ')journal();if(e.code==='KeyM')arrive()};
onkeyup=e=>keys.delete(e.code);onblur=()=>keys.clear();
for(const button of document.querySelectorAll('[data-key]')){
 button.onpointerdown=e=>{button.setPointerCapture(e.pointerId);keys.add(button.dataset.key)};
 button.onlostpointercapture=()=>keys.delete(button.dataset.key);
}
async function build(){
 renderer=new T.WebGLRenderer({canvas:world,antialias:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,1.6));scene.background=new T.Color(0x243335);
 scene.add(new T.HemisphereLight(0xfff3d7,0x7a918d,1.9));const sun=new T.DirectionalLight(0xffe9c5,1.5);sun.position.set(4,8,6);scene.add(sun);
 const model=(await new GLTFLoader().loadAsync('facility.glb')).scene;scene.add(model);model.updateMatrixWorld(true);
 model.traverse(o=>{if(!o.isMesh)return;const box=new T.Box3().setFromObject(o);if(box.min.y<1.6&&box.max.y>.24)solids.push(box);if(/^(RECORDS|PERSONNEL|HANDOVER|QUARTERS|WORKSHOP|DISPATCH|EXIT)/.test(o.name))o.visible=false});
 for(const [id,[name,x,y]] of Object.entries(stations)){
 const c=document.createElement('canvas');c.width=768;c.height=128;const g=c.getContext('2d');g.fillStyle='#1a302f';g.fillRect(0,0,768,128);g.fillStyle='#e1b971';g.fillRect(0,0,12,128);g.font='bold 62px Microsoft YaHei, sans-serif';g.fillStyle='#ede6cf';g.textAlign='center';g.fillText(name.split(' · ')[1],384,87);
 const tex=new T.CanvasTexture(c);tex.colorSpace=T.SRGBColorSpace;const sprite=new T.Sprite(new T.SpriteMaterial({map:tex}));sprite.position.set(x,1.86,-y);sprite.scale.set(1.72,.29,1);scene.add(sprite);
 }
 // The arriving clerk wears the same uniform as the player.
 const clerk=new T.Group();clerk.position.set(11,0,-6.48);scene.add(clerk);
 for(const [w,h,d,y,color] of [[.44,.66,.28,1.13,0x455d55],[.27,.32,.24,1.63,0xc8ab88],[.31,.1,.26,1.82,0x253b36],[.34,.8,.23,.43,0x263b3a],[.12,.07,.015,1.29,0xe4bd76]]){
 const m=new T.Mesh(new T.BoxGeometry(w,h,d),new T.MeshStandardMaterial({color}));m.position.set(0,y,y===1.29?.15:0);clerk.add(m)}
 function resize(){renderer.setSize(innerWidth,innerHeight,false);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix()}onresize=resize;resize();
 let prev=performance.now();renderer.setAnimationLoop(now=>{update(Math.min(.05,(now-prev)/1000));prev=now;clerk.visible=step>=3;if(step===5)clerk.position.set(13,0,6.1);else clerk.position.set(11,0,-6.48);renderer.render(scene,camera)});arrive()
}
build().catch(e=>{console.error(e);show('设施连接失败','地图未能打开','请使用支持 WebGL 2 的浏览器打开游戏预览。','重新连接',()=>location.reload())});
