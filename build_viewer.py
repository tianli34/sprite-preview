# -*- coding: utf-8 -*-
"""生成自包含的动画预览页 viewer.html（帧图内嵌为 data URI，双击即可播放）。"""
import base64
import io
import json
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "frames.json"), encoding="utf-8") as f:
    manifest = json.load(f)

for action, seq in manifest["actions"].items():
    for fr in seq:
        im = Image.open(os.path.join(HERE, fr["file"])).convert("RGBA")
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=90, method=6)
        fr["src"] = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()

frames_json = json.dumps(manifest["actions"], ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>精灵动画预览 · model10040118_2</title>
<style>
  :root{
    --bg:#0d1014; --panel:#151a21; --line:#252c36; --text:#e9eef6; --muted:#8d9aab;
    --accent:#ff7a3d; --accent-soft:rgba(255,122,61,.16);
  }
  *{box-sizing:border-box}
  html,body{height:100%}
  body{
    margin:0;background:
      radial-gradient(900px 520px at 18% -10%, #1b2430 0%, transparent 60%),
      radial-gradient(700px 420px at 100% 110%, #2a1712 0%, transparent 55%),
      var(--bg);
    color:var(--text);font-family:"Segoe UI","Microsoft YaHei",system-ui,-apple-system,sans-serif;
    display:flex;flex-direction:column;min-height:100vh;
  }
  header{display:flex;align-items:baseline;gap:14px;padding:22px 30px 6px}
  header h1{font-size:19px;font-weight:650;margin:0;letter-spacing:.02em}
  header .meta{font-size:12.5px;color:var(--muted)}
  main{flex:1;display:flex;gap:26px;padding:10px 30px 26px;align-items:stretch;min-height:0}
  .stage-wrap{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:0}
  .stage{
    position:relative;width:min(62vh,560px,100%);aspect-ratio:1;border-radius:20px;
    border:1px solid var(--line);
    background:
      radial-gradient(circle at 50% 56%, rgba(255,122,61,.10) 0%, rgba(255,122,61,0) 55%),
      repeating-linear-gradient(0deg, rgba(255,255,255,.025) 0 1px, transparent 1px 40px),
      repeating-linear-gradient(90deg, rgba(255,255,255,.025) 0 1px, transparent 1px 40px),
      #10141a;
    box-shadow:inset 0 0 80px rgba(0,0,0,.45), 0 30px 60px rgba(0,0,0,.35);
    overflow:hidden;
  }
  .stage img{
    position:absolute;inset:0;width:100%;height:100%;object-fit:contain;
    filter:drop-shadow(0 18px 30px rgba(255,90,30,.22));
    image-rendering:auto;
  }
  .badge{
    position:absolute;left:14px;top:12px;z-index:2;font-size:12px;color:var(--muted);
    background:rgba(13,16,20,.72);border:1px solid var(--line);border-radius:8px;
    padding:5px 9px;font-variant-numeric:tabular-nums;backdrop-filter:blur(4px);
  }
  .badge b{color:var(--text);font-weight:600}
  .progress{height:3px;width:min(62vh,560px,100%);background:#1c232c;border-radius:3px;margin-top:14px;overflow:hidden}
  .progress > i{display:block;height:100%;width:0;background:linear-gradient(90deg,#ff9d5c,#ff5f2e);transition:width .05s linear}
  .panel{
    width:330px;flex:none;display:flex;flex-direction:column;gap:18px;padding:18px;
    background:var(--panel);border:1px solid var(--line);border-radius:18px;
    box-shadow:0 20px 50px rgba(0,0,0,.25);
  }
  .group-title{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:0 0 8px}
  .actions{display:flex;gap:8px}
  .actions button{flex:1}
  button{
    appearance:none;border:1px solid var(--line);background:#1a212a;color:var(--text);
    border-radius:10px;padding:9px 12px;font-size:13px;cursor:pointer;
    transition:border-color .15s,background .15s,color .15s;
    font-family:inherit;
  }
  button:hover{background:#202936;border-color:#33404f}
  button.active{background:var(--accent-soft);border-color:rgba(255,122,61,.55);color:#ffb489}
  .transport{display:flex;gap:8px;align-items:center}
  .transport .play{
    flex:1;display:flex;align-items:center;justify-content:center;gap:8px;font-weight:600;
    background:linear-gradient(180deg,#ff8a50,#f2632d);border-color:#ff9160;color:#1a0d07;
  }
  .transport .play:hover{filter:brightness(1.06);background:linear-gradient(180deg,#ff8a50,#f2632d)}
  .transport .icon{width:38px;flex:none;padding:9px 0;font-size:14px}
  .row{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--muted)}
  .row strong{color:var(--text);font-weight:600;min-width:46px;text-align:right;font-variant-numeric:tabular-nums}
  input[type=range]{
    -webkit-appearance:none;appearance:none;flex:1;height:4px;border-radius:4px;outline:none;
    background:linear-gradient(90deg,var(--accent) 0%,var(--accent) 50%,#2a333f 50%);
  }
  input[type=range]::-webkit-slider-thumb{
    -webkit-appearance:none;width:15px;height:15px;border-radius:50%;background:#fff;
    border:3px solid var(--accent);cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.4);
  }
  .check{display:flex;align-items:center;gap:8px;cursor:pointer;user-select:none}
  input[type=checkbox]{accent-color:var(--accent);width:15px;height:15px;cursor:pointer}
  .timeline{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
  .thumb{
    position:relative;border:1px solid var(--line);border-radius:10px;background:#10151b;
    padding:0;overflow:hidden;cursor:pointer;aspect-ratio:1;display:block;
  }
  .thumb img{width:100%;height:100%;object-fit:cover;display:block;opacity:.78;transition:opacity .15s}
  .thumb:hover img{opacity:1}
  .thumb span{
    position:absolute;left:0;right:0;bottom:0;padding:3px 0;font-size:10.5px;color:#cfd8e3;
    background:linear-gradient(transparent,rgba(0,0,0,.8));text-align:center;font-variant-numeric:tabular-nums;
  }
  .thumb.sel{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent) inset}
  .thumb.sel img{opacity:1}
  .hint{font-size:11.5px;line-height:1.8;color:#6f7c8c;margin:auto 0 0}
  .hint kbd{
    font-family:inherit;font-size:10.5px;padding:1px 5px;border-radius:4px;color:#a9b6c6;
    border:1px solid #2b3542;background:#1b232c;
  }
  @media (max-width:900px){
    main{flex-direction:column;align-items:center;padding:8px 16px 20px}
    header{padding:16px 18px 4px;flex-wrap:wrap}
    .panel{width:min(560px,100%)}
    .stage{width:min(78vw,440px)}
    .progress{width:min(78vw,440px)}
  }
</style>
</head>
<body>
<header>
  <h1>精灵动画预览</h1>
  <div class="meta">model10040118_2 · 图集 1012×954 · attack8 / idle8</div>
</header>
<main>
  <div class="stage-wrap">
    <div class="stage">
      <div class="badge"><b id="badgeAction">attack8</b> · 原始帧 <span id="badgeIndex">8</span> · <span id="badgeHold">330</span>ms</div>
      <img id="char" alt="精灵帧">
    </div>
    <div class="progress"><i id="bar"></i></div>
  </div>

  <aside class="panel">
    <div>
      <p class="group-title">动作</p>
      <div class="actions" id="actions"></div>
    </div>

    <div>
      <p class="group-title">播放</p>
      <div class="transport">
        <button class="icon" id="prev" title="上一帧 (←)">◀</button>
        <button class="play" id="play">⏸ 暂停</button>
        <button class="icon" id="next" title="下一帧 (→)">▶</button>
      </div>
    </div>

    <div>
      <div class="row" style="justify-content:space-between">
        <span>速度</span><strong id="speedVal">1.00×</strong>
      </div>
      <div class="row" style="margin-top:8px">
        <input type="range" id="speed" min="0.25" max="2" step="0.25" value="1">
      </div>
      <label class="row check" style="margin-top:12px">
        <input type="checkbox" id="loop" checked> 循环播放
      </label>
    </div>

    <div>
      <p class="group-title">序列帧</p>
      <div class="timeline" id="timeline"></div>
    </div>

    <p class="hint">
      <kbd>空格</kbd> 播放 / 暂停　<kbd>←</kbd><kbd>→</kbd> 逐帧<br>
      时长按原始帧号间隔估算（30fps），缺帧处保留停留时间。
    </p>
  </aside>
</main>

<script>
const DATA = __FRAMES__;
let action = "attack8", idx = 0, playing = true, speed = 1, loop = true, acc = 0, last = 0;

const $ = id => document.getElementById(id);
const char = $("char"), bar = $("bar"), timeline = $("timeline");

function frames(){ return DATA[action]; }

function buildActions(){
  const box = $("actions");
  const labels = {attack8:"攻击 attack8", idle8:"待机 idle8"};
  Object.keys(DATA).forEach(key => {
    const b = document.createElement("button");
    b.textContent = labels[key] || key;
    b.dataset.action = key;
    b.onclick = () => switchAction(key);
    box.appendChild(b);
  });
}

function buildTimeline(){
  timeline.innerHTML = "";
  frames().forEach((fr, i) => {
    const b = document.createElement("button");
    b.className = "thumb";
    b.title = fr.name + " · " + fr.hold + "ms";
    b.innerHTML = `<img src="${fr.src}" alt=""><span>${fr.index}</span>`;
    b.onclick = () => { idx = i; acc = 0; render(); };
    timeline.appendChild(b);
  });
}

function switchAction(key){
  action = key; idx = 0; acc = 0; playing = true;
  buildTimeline(); render(); syncPlayBtn();
}

function render(){
  const list = frames(), fr = list[idx];
  char.src = fr.src;
  $("badgeAction").textContent = action;
  $("badgeIndex").textContent = fr.index;
  $("badgeHold").textContent = fr.hold;
  [...timeline.children].forEach((el, i) => el.classList.toggle("sel", i === idx));
  [...$("actions").children].forEach(el => el.classList.toggle("active", el.dataset.action === action));
  bar.style.width = (acc / fr.hold * 100).toFixed(1) + "%";
}

function syncPlayBtn(){
  $("play").textContent = playing ? "⏸ 暂停" : "▶ 播放";
}

function tick(ts){
  if(!last) last = ts;
  const dt = Math.min(ts - last, 120);
  last = ts;
  if(playing){
    acc += dt * speed;
    let guard = 0;
    while(acc >= frames()[idx].hold && guard++ < 8){
      acc -= frames()[idx].hold;
      if(idx + 1 < frames().length) idx++;
      else if(loop) idx = 0;
      else { playing = false; acc = frames()[idx].hold; syncPlayBtn(); break; }
    }
    render();
  }
  requestAnimationFrame(tick);
}

$("play").onclick = () => { playing = !playing; acc = 0; syncPlayBtn(); };
$("prev").onclick = () => { idx = (idx - 1 + frames().length) % frames().length; acc = 0; render(); };
$("next").onclick = () => { idx = (idx + 1) % frames().length; acc = 0; render(); };
$("speed").oninput = e => {
  speed = parseFloat(e.target.value);
  $("speedVal").textContent = speed.toFixed(2) + "×";
  e.target.style.background = `linear-gradient(90deg,var(--accent) 0%,var(--accent) ${(speed - .25) / 1.75 * 100}%,#2a333f ${(speed - .25) / 1.75 * 100}%)`;
};
$("loop").onchange = e => { loop = e.target.checked; };

document.addEventListener("keydown", e => {
  if(e.code === "Space"){ e.preventDefault(); $("play").click(); }
  if(e.code === "ArrowLeft"){ e.preventDefault(); $("prev").click(); }
  if(e.code === "ArrowRight"){ e.preventDefault(); $("next").click(); }
});

buildActions();
buildTimeline();
$("speed").dispatchEvent(new Event("input"));
render();
syncPlayBtn();
requestAnimationFrame(tick);
</script>
</body>
</html>
"""

html = HTML.replace("__FRAMES__", frames_json)
with open(os.path.join(HERE, "viewer.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("viewer.html:", round(os.path.getsize(os.path.join(HERE, "viewer.html")) / 1024), "KB")
