from flask import Flask, Response

app = Flask(__name__)

GAME_HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>표류일지 — 무인도 생존기</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;700;900&family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<style>
  :root{
    --ink:#EDE7D8;
    --ink-dim:#A9A392;
    --bg-deep:#040709;
    --bg-mid:#0A1119;
    --bg-panel:#101820;
    --line: rgba(237,231,216,0.10);
    --line-strong: rgba(237,231,216,0.20);
    --gold:#D6A94C;
    --gold-dim: rgba(214,169,76,0.16);
    --coral:#DE6A50;
    --coral-dim: rgba(222,106,80,0.16);
    --teal:#4FA79E;
    --teal-dim: rgba(79,167,158,0.16);
    --violet:#7C9BCB;
    --violet-dim: rgba(124,155,203,0.16);
  }
  *{box-sizing:border-box;}
  body{
    margin:0;
    min-height:100vh;
    font-family:'Noto Sans KR', sans-serif;
    color:var(--ink);
    background:
      radial-gradient(ellipse 900px 500px at 15% -10%, rgba(79,167,158,0.10), transparent 60%),
      radial-gradient(ellipse 700px 500px at 100% 110%, rgba(214,169,76,0.08), transparent 60%),
      linear-gradient(180deg, var(--bg-deep) 0%, var(--bg-mid) 55%, var(--bg-deep) 100%);
    display:flex;
    flex-direction:column;
    align-items:center;
    padding:28px 16px 40px;
    position:relative;
    overflow-x:hidden;
  }
  /* subtle grain */
  body::before{
    content:"";
    position:fixed; inset:0; pointer-events:none; z-index:0; opacity:0.05;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  }
  .stars span{
    position:fixed; border-radius:50%; background:#fff; pointer-events:none; z-index:0;
    animation: tw 3.5s ease-in-out infinite;
  }
  @keyframes tw{0%,100%{opacity:.15}50%{opacity:.75}}

  .wrap{ position:relative; z-index:1; width:100%; max-width:640px; }
  .eyebrow{
    font-size:12px; letter-spacing:0.14em; color:var(--gold); font-weight:600;
  }
  h1,h2{ font-family:'Noto Serif KR', serif; margin:0; }

  /* ---------- panel shell : journal page, not a saas card ---------- */
  .page{
    background: linear-gradient(180deg, rgba(16,24,32,0.9), rgba(9,14,19,0.92));
    border:1px solid var(--line);
    border-top:2px solid var(--line-strong);
    padding:34px 30px 28px;
    position:relative;
  }
  .page::after{
    content:"";
    position:absolute; left:0; right:0; bottom:-1px; height:10px;
    background:
      linear-gradient(135deg, transparent 50%, var(--bg-deep) 50%) 0 0/14px 10px repeat-x,
      linear-gradient(-135deg, transparent 50%, var(--bg-deep) 50%) 0 0/14px 10px repeat-x;
  }
  .hidden{display:none !important;}

  /* ---------- start screen ---------- */
  #start-screen{ text-align:center; }
  .compass{ width:56px;height:56px; margin:0 auto 18px; opacity:0.9; }
  #start-screen h1{ font-size:28px; line-height:1.35; color:var(--ink); margin:10px 0 14px; }
  #start-screen p{ color:var(--ink-dim); font-size:14.5px; line-height:1.7; font-weight:300; margin:0; }
  .lede{ max-width:440px; margin:0 auto 26px; }

  .trait-grid{ display:grid; grid-template-columns:1fr; gap:10px; text-align:left; margin:22px 0 24px; }
  @media(min-width:560px){ .trait-grid{ grid-template-columns:1fr 1fr 1fr; } }
  .trait-card{
    border:1px solid var(--line); border-left:3px solid transparent;
    padding:14px 14px 12px; cursor:pointer; background:rgba(255,255,255,0.02);
    transition:border-color .15s, background .15s;
  }
  .trait-card:hover{ background:rgba(255,255,255,0.045); }
  .trait-card.selected{ border-left-color:var(--gold); background:var(--gold-dim); }
  .trait-icon{ font-size:20px; }
  .trait-name{ font-weight:700; font-size:14.5px; margin:6px 0 4px; }
  .trait-desc{ font-size:12px; color:var(--ink-dim); line-height:1.55; font-weight:300; }

  .btn-primary{
    appearance:none; border:none; cursor:pointer;
    background:var(--gold); color:#241A05; font-weight:700; font-size:16px;
    padding:15px 40px; letter-spacing:0.02em;
    box-shadow:0 10px 30px -12px rgba(214,169,76,0.55);
    transition:transform .15s, box-shadow .15s;
  }
  .btn-primary:hover{ transform:translateY(-2px); box-shadow:0 14px 34px -12px rgba(214,169,76,0.7); }
  .btn-ghost{
    appearance:none; cursor:pointer; background:transparent; color:var(--ink);
    border:1px solid var(--line-strong); font-weight:600; font-size:14.5px; padding:12px 30px;
  }
  .btn-ghost:hover{ border-color:var(--gold); color:var(--gold); }

  /* ---------- name input ---------- */
  .name-field{
    display:flex; align-items:center; gap:10px; max-width:340px; margin:0 auto 22px;
    border-bottom:1px solid var(--line-strong); padding-bottom:8px;
  }
  .name-field label{ font-size:12px; color:var(--ink-dim); white-space:nowrap; }
  .name-field input{
    flex:1; background:transparent; border:none; outline:none; color:var(--ink);
    font-family:'Noto Serif KR', serif; font-size:16px; text-align:center;
  }
  .name-field input::placeholder{ color:var(--ink-dim); font-family:'Noto Sans KR',sans-serif; font-size:13px; }

  /* ---------- castaway portrait ---------- */
  .castaway-card{
    display:flex; align-items:center; gap:16px;
    border:1px solid var(--line); border-bottom:none; padding:14px 18px;
    background:rgba(255,255,255,0.02);
  }
  .avatar-frame{
    width:64px; height:64px; flex:none; border-radius:50%;
    background:radial-gradient(circle at 35% 30%, rgba(214,169,76,0.18), rgba(255,255,255,0.02));
    border:1px solid var(--line-strong);
    display:flex; align-items:center; justify-content:center; overflow:hidden;
  }
  .avatar-svg{ width:58px; height:58px; }
  .avatar-svg .mood{ display:none; }
  .avatar-svg[data-state="happy"] .mood-happy{ display:inline; }
  .avatar-svg[data-state="normal"] .mood-normal{ display:inline; }
  .avatar-svg[data-state="tired"] .mood-tired{ display:inline; }
  .avatar-svg[data-state="sick"] .mood-sick{ display:inline; }
  .avatar-svg .acc{ display:none; }
  .avatar-svg[data-trait="fisher"] .acc-fisher{ display:inline; }
  .avatar-svg[data-trait="outdoors"] .acc-outdoors{ display:inline; }
  .avatar-svg[data-trait="optimist"] .acc-optimist{ display:inline; }
  .castaway-meta{ flex:1; }
  .castaway-name{ font-family:'Noto Serif KR',serif; font-size:16px; color:var(--ink); }
  .castaway-mood{ font-size:12px; color:var(--ink-dim); margin-top:3px; }

  /* ---------- game screen ---------- */
  .dash{
    display:grid; grid-template-columns:auto 1fr; gap:22px; align-items:center;
    border:1px solid var(--line); padding:16px 18px; margin:0 0 18px;
    background:rgba(255,255,255,0.015);
  }
  .day-block{ text-align:center; padding-right:20px; border-right:1px solid var(--line); }
  .day-num{ font-family:'Noto Serif KR',serif; font-size:26px; color:var(--gold); line-height:1; }
  .day-label{ font-size:11px; color:var(--ink-dim); margin-top:4px; }
  .day-flavor{ font-size:10.5px; color:var(--ink-dim); margin-top:6px; max-width:70px; line-height:1.4; }

  .gauges{ display:flex; gap:18px; flex-wrap:wrap; }
  .gauge-item{ display:flex; align-items:center; gap:10px; }
  .gauge{
    width:52px; height:52px; border-radius:50%;
    background: conic-gradient(var(--gcolor) calc(var(--pct)*1%), rgba(255,255,255,0.08) 0);
    display:flex; align-items:center; justify-content:center; position:relative; flex:none;
  }
  .gauge::before{
    content:""; position:absolute; width:38px;height:38px;border-radius:50%;
    background:var(--bg-mid);
  }
  .gauge span{ position:relative; font-size:11px; font-weight:700; color:var(--ink); }
  .gauge-meta .glabel{ font-size:11px; color:var(--ink-dim); }
  .gauge-meta .gval{ font-size:12.5px; font-weight:600; }

  .inv-row{
    display:flex; align-items:center; gap:10px; flex-wrap:wrap;
    font-size:12px; color:var(--ink-dim); border:1px solid var(--line); padding:10px 14px; margin-bottom:20px;
  }
  .inv-row b{ color:var(--ink); font-weight:600; }
  .chip{
    border:1px solid var(--line-strong); padding:3px 9px; font-size:11.5px; color:var(--gold);
    background:var(--gold-dim);
  }

  .scenario{
    border:1px solid var(--line); border-left:3px solid var(--cat-color, var(--gold));
    padding:0 0 20px; margin-bottom:20px; position:relative; overflow:hidden;
    background:rgba(255,255,255,0.015);
  }
  .scene-stage{
    position:relative; width:100%; height:190px; overflow:hidden;
    background:linear-gradient(180deg, #060a10 0%, #0b141d 100%);
    border-bottom:1px solid var(--line);
  }
  .scene-stage canvas{ display:block; width:100%; height:100%; }
  .scene-vignette{
    position:absolute; inset:0; pointer-events:none;
    background:
      linear-gradient(180deg, rgba(6,10,16,0.05) 0%, rgba(6,10,16,0.55) 100%),
      radial-gradient(ellipse at 50% 100%, rgba(6,10,16,0.6), transparent 60%);
  }
  .scene-icon{
    position:absolute; top:10px; right:12px; font-size:18px; opacity:0.85;
    filter:drop-shadow(0 2px 4px rgba(0,0,0,0.6));
  }
  .scene-flash{
    position:absolute; inset:0; background:#fff; opacity:0; pointer-events:none;
  }
  .scenario-body{ padding:20px 22px 0; }
  .badge-row{ display:flex; align-items:center; gap:10px; margin-bottom:10px; }
  .cat-badge{
    font-size:11px; font-weight:700; letter-spacing:0.03em;
    color:var(--cat-color, var(--gold)); border:1px solid var(--cat-color, var(--gold));
    padding:3px 9px;
  }
  .scenario h2{ font-size:19px; color:var(--ink); }
  .scenario p{ font-size:13.5px; line-height:1.75; color:var(--ink-dim); font-weight:300; margin:10px 0 0; white-space:pre-line; }

  .choices{ display:flex; flex-direction:column; gap:9px; }
  .choice-btn{
    display:flex; align-items:center; justify-content:space-between; gap:12px;
    text-align:left; padding:14px 16px; cursor:pointer;
    background:rgba(255,255,255,0.02); border:1px solid var(--line); border-left:3px solid var(--risk-color, var(--line-strong));
    color:var(--ink); font-size:13.5px; font-weight:500; font-family:inherit;
    transition:background .15s, border-color .15s;
  }
  .choice-btn:hover{ background:rgba(255,255,255,0.055); border-color:var(--risk-color, var(--gold)); }
  .choice-btn:disabled{ opacity:0.35; cursor:not-allowed; }
  .choice-num{ color:var(--ink-dim); font-size:12px; margin-right:8px; }
  .choice-arrow{ color:var(--ink-dim); flex:none; }

  /* ---------- gameover screen ---------- */
  #gameover-screen{ text-align:center; }
  .go-emoji{ font-size:52px; margin-bottom:6px; }
  #gameover-title{ font-size:26px; margin-bottom:10px; }
  #gameover-reason{ color:var(--ink-dim); font-size:13.5px; line-height:1.7; max-width:440px; margin:0 auto 22px; font-weight:300;}
  .final-panel{
    border:1px solid var(--line); padding:20px; max-width:340px; margin:0 auto 18px; background:rgba(255,255,255,0.02);
  }
  .final-days{ font-family:'Noto Serif KR',serif; font-size:30px; color:var(--gold); }
  .badges{ display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin:14px 0 24px; }
  .ach{ font-size:11.5px; border:1px solid var(--line-strong); padding:5px 10px; color:var(--ink-dim); }

  footer{ position:relative; z-index:1; color:var(--ink-dim); font-size:11px; margin-top:26px; text-align:center; }
</style>
</head>
<body>

<div class="stars">
  <span style="width:2px;height:2px;top:8%;left:20%;animation-delay:.2s;"></span>
  <span style="width:1.5px;height:1.5px;top:14%;left:75%;animation-delay:1.1s;"></span>
  <span style="width:2px;height:2px;top:22%;left:52%;animation-delay:.6s;"></span>
  <span style="width:1.5px;height:1.5px;top:5%;left:88%;animation-delay:1.8s;"></span>
</div>

<div class="wrap">

  <!-- ================= START ================= -->
  <div id="start-screen" class="page">
    <svg class="compass" viewBox="0 0 64 64" fill="none">
      <circle cx="32" cy="32" r="28" stroke="#D6A94C" stroke-width="1.4" opacity="0.7"/>
      <circle cx="32" cy="32" r="2.4" fill="#D6A94C"/>
      <path d="M32 8 L36 30 L32 34 L28 30 Z" fill="#D6A94C"/>
      <path d="M32 56 L28 34 L32 30 L36 34 Z" fill="#EDE7D8" opacity="0.5"/>
      <text x="32" y="6" font-size="5" fill="#A9A392" text-anchor="middle">N</text>
    </svg>
    <div class="eyebrow">표류 D-1 · 좌표 불명</div>
    <h1>내가 만약 무인도에 떨어진다면?</h1>
    <div class="lede">
      <p>배가 침몰한 밤, 당신은 이름 없는 섬 해변에서 눈을 떴습니다.<br>
      가진 것은 젖은 옷과 낡은 성냥 한 갑뿐입니다.<br>
      구조선이 당신을 찾아낼 때까지, 하루하루를 버텨내야 합니다.</p>
    </div>

    <div class="name-field">
      <label for="name-input">이름</label>
      <input type="text" id="name-input" placeholder="표류자의 이름 (선택)" maxlength="12">
    </div>

    <div class="eyebrow" style="margin-bottom:10px;">당신은 어떤 사람이었나요?</div>
    <div class="trait-grid" id="trait-grid"></div>

    <button class="btn-primary" onclick="startGame()">항해 일지 시작하기</button>
  </div>

  <!-- ================= GAME ================= -->
  <div id="game-screen" class="page hidden">

    <div class="castaway-card">
      <div class="avatar-frame">
        <svg class="avatar-svg" id="avatar-svg" viewBox="0 0 100 100" data-state="normal" data-trait="fisher">
          <!-- shoulders / torn shirt -->
          <path d="M14 100 C14 76 30 66 50 66 C70 66 86 76 86 100 Z" fill="#E7E0CE"/>
          <path d="M14 100 C14 82 24 72 34 68 L30 100 Z" fill="#D8CFB6"/>
          <path d="M86 100 C86 82 76 72 66 68 L70 100 Z" fill="#D8CFB6"/>
          <!-- neck -->
          <rect x="42" y="58" width="16" height="14" fill="#C98C5D"/>
          <!-- head -->
          <circle cx="50" cy="42" r="26" fill="#D79A66"/>
          <!-- hair -->
          <path d="M24 38 C22 20 36 12 50 12 C64 12 78 20 76 38 C72 30 64 24 50 24 C36 24 28 30 24 38 Z" fill="#3B2A1F"/>
          <!-- bandana -->
          <path d="M22 30 C30 22 70 22 78 30 L76 36 C64 30 36 30 24 36 Z" fill="#D6A94C"/>
          <path d="M76 32 L86 40 L78 42 Z" fill="#D6A94C"/>

          <!-- mood: happy -->
          <g class="mood mood-happy">
            <path d="M38 40 Q41 35 44 40" stroke="#3B2A1F" stroke-width="2.2" fill="none" stroke-linecap="round"/>
            <path d="M56 40 Q59 35 62 40" stroke="#3B2A1F" stroke-width="2.2" fill="none" stroke-linecap="round"/>
            <path d="M39 50 Q50 60 61 50" stroke="#5C3A22" stroke-width="2.6" fill="none" stroke-linecap="round"/>
          </g>
          <!-- mood: normal -->
          <g class="mood mood-normal">
            <circle cx="41" cy="41" r="2" fill="#3B2A1F"/>
            <circle cx="59" cy="41" r="2" fill="#3B2A1F"/>
            <path d="M41 52 Q50 56 59 52" stroke="#5C3A22" stroke-width="2.2" fill="none" stroke-linecap="round"/>
          </g>
          <!-- mood: tired -->
          <g class="mood mood-tired">
            <path d="M37 41 L45 41" stroke="#3B2A1F" stroke-width="2.2" stroke-linecap="round"/>
            <path d="M55 41 L63 41" stroke="#3B2A1F" stroke-width="2.2" stroke-linecap="round"/>
            <path d="M42 54 Q50 51 58 54" stroke="#5C3A22" stroke-width="2.2" fill="none" stroke-linecap="round"/>
            <path d="M66 34 C68 38 68 42 65 45" stroke="#7FBFD8" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.8"/>
          </g>
          <!-- mood: sick -->
          <g class="mood mood-sick">
            <path d="M38 38 L44 44 M44 38 L38 44" stroke="#3B2A1F" stroke-width="2" stroke-linecap="round"/>
            <path d="M56 38 L62 44 M62 38 L56 44" stroke="#3B2A1F" stroke-width="2" stroke-linecap="round"/>
            <path d="M41 55 Q50 49 59 55" stroke="#7A3B2E" stroke-width="2.4" fill="none" stroke-linecap="round"/>
            <rect x="60" y="48" width="12" height="6" rx="2" fill="#EDE7D8" stroke="#C98C5D" stroke-width="0.6"/>
          </g>

          <!-- trait accessories -->
          <text class="acc acc-fisher" x="66" y="88" font-size="16">🎣</text>
          <text class="acc acc-outdoors" x="66" y="88" font-size="16">🧭</text>
          <text class="acc acc-optimist" x="66" y="88" font-size="16">🍀</text>
        </svg>
      </div>
      <div class="castaway-meta">
        <div class="castaway-name" id="castaway-name">이름 없는 표류자</div>
        <div class="castaway-mood" id="castaway-mood">컨디션: 양호함</div>
      </div>
    </div>

    <div class="dash">
      <div class="day-block">
        <div class="day-num" id="stat-day">1</div>
        <div class="day-label">DAY</div>
        <div class="day-flavor" id="day-flavor">해가 떠오르다</div>
      </div>
      <div class="gauges">
        <div class="gauge-item">
          <div class="gauge" id="gauge-health" style="--pct:100;--gcolor:var(--coral);"><span id="num-health">100</span></div>
          <div class="gauge-meta"><div class="glabel">체력</div><div class="gval" id="text-health">100/100</div></div>
        </div>
        <div class="gauge-item">
          <div class="gauge" id="gauge-hunger" style="--pct:100;--gcolor:var(--gold);"><span id="num-hunger">100</span></div>
          <div class="gauge-meta"><div class="glabel">포만감</div><div class="gval" id="text-hunger">100/100</div></div>
        </div>
        <div class="gauge-item">
          <div class="gauge" id="gauge-thirst" style="--pct:100;--gcolor:var(--teal);"><span id="num-thirst">100</span></div>
          <div class="gauge-meta"><div class="glabel">수분</div><div class="gval" id="text-thirst">100/100</div></div>
        </div>
      </div>
    </div>

    <div class="inv-row">
      <b>소지품</b>
      <div id="inventory-list" style="display:flex; gap:6px; flex-wrap:wrap;"></div>
    </div>

    <div class="scenario" id="scenario-box">
      <div class="scene-stage" id="scene-stage">
        <div class="scene-vignette"></div>
        <span class="scene-icon" id="scenario-emoji-bg">🏝️</span>
        <div class="scene-flash" id="scene-flash"></div>
      </div>
      <div class="scenario-body">
        <div class="badge-row">
          <span class="cat-badge" id="scenario-badge">상황</span>
        </div>
        <h2 id="scenario-title">상황 제목</h2>
        <p id="scenario-desc">상황 설명</p>
      </div>
    </div>

    <div id="choices-container" class="choices"></div>
  </div>

  <!-- ================= GAME OVER ================= -->
  <div id="gameover-screen" class="page hidden">
    <div class="go-emoji" id="gameover-emoji">💀</div>
    <h2 id="gameover-title">생존 실패</h2>
    <p id="gameover-reason">-</p>
    <div class="final-panel">
      <div class="day-label" style="margin-bottom:4px;">최종 생존 기록</div>
      <div class="final-days" id="final-days">Day 1</div>
    </div>
    <div class="badges" id="badges"></div>
    <button class="btn-primary" onclick="resetGame()">다시 표류하기</button>
  </div>

</div>

<footer>일지는 매번 다르게 기록됩니다 · 무인도 생존 시뮬레이터</footer>

<script>
/* ============ 설정: 특성 ============ */
const TRAITS = [
  { key:'fisher', icon:'🎣', name:'베테랑 어부', startItem:'낚싯줄',
    desc:'물과 식량을 구하는 선택에서 더 많은 것을 얻습니다.' },
  { key:'outdoors', icon:'🧭', name:'야외 전문가', startItem:'방수 재킷',
    desc:'위험한 상황에서 체력을 덜 잃습니다.' },
  { key:'optimist', icon:'🍀', name:'낙천주의자', startItem:'행운의 부적',
    desc:'매일 체력이 조금씩 회복되고, 구조 확률이 오릅니다.' }
];

const CAT_COLOR = {
  exploration:'var(--gold)',
  water:'var(--teal)',
  weather:'var(--violet)',
  animal:'var(--coral)',
  health:'var(--coral)',
  craft:'var(--gold)',
  social:'var(--violet)',
  rescue:'var(--teal)'
};
const RISK_COLOR = { safe:'var(--teal)', balanced:'var(--gold)', risky:'var(--coral)' };

/* ============ 시나리오 풀 ============ */
const scenarioPool = [
  { id:'beach_crate', category:'exploration', emoji:'📦', badge:'해변 탐색',
    title:'밀려온 상자 두 개',
    desc:'파도가 상자 두 개를 해변에 밀어 올렸습니다. 하나는 녹슨 철제, 다른 하나는 방수 플라스틱입니다.',
    choices:[
      { text:'철제 상자를 연다', risk:'balanced', effect:{addInv:'녹슨 칼'}, message:'녹슨 칼을 얻었습니다. 사냥과 손질에 쓸 수 있을 것 같습니다.' },
      { text:'방수 통을 연다', risk:'safe', effect:{hunger:14, thirst:18}, message:'통조림과 생수를 발견해 배와 목을 채웠습니다.' },
      { text:'열어보지 않고 모닥불부터 정비한다', risk:'safe', effect:{health:5, hunger:-4}, message:'안전을 택했지만 배가 고파집니다.' }
    ]},
  { id:'forest_fruit', category:'exploration', emoji:'🥭', badge:'정글 탐색',
    title:'낯선 열매나무',
    desc:'정글 깊숙한 곳에서 처음 보는 열매가 가득 열린 나무를 발견했습니다. 새들이 그 열매를 쪼아 먹고 있습니다.',
    choices:[
      { text:'새가 먹는 것을 보고 안심하며 먹는다', risk:'balanced', effect:{hunger:22, health:-4}, message:'배는 채웠지만 살짝 위가 쓰립니다. 완전히 안전하진 않았던 모양입니다.' },
      { text:'몇 개만 따서 나중에 끓여 먹기로 한다', risk:'safe', effect:{hunger:10, addInv:'낯선 열매'}, message:'무리하지 않고 조금만 챙겼습니다.' },
      { text:'위험해 보여 포기하고 다른 곳을 찾는다', risk:'safe', effect:{hunger:-6, health:2}, message:'허탕이었지만 다치지는 않았습니다.' }
    ]},
  { id:'cave_shelter', category:'exploration', emoji:'🕳️', badge:'동굴 발견',
    title:'절벽 아래의 작은 동굴',
    desc:'해안 절벽 아래로 사람 한 명이 겨우 들어갈 동굴 입구를 발견했습니다. 안쪽에서 찬 바람이 흘러나옵니다.',
    choices:[
      { text:'조심스럽게 안까지 들어가 본다', risk:'risky', effect:{health:-10, addInv:'마른 나뭇가지'}, message:'박쥐떼에 놀라 긁혔지만, 불쏘시개로 쓸 마른 나뭇가지를 챙겼습니다.' },
      { text:'입구만 정리해 은신처로 삼는다', risk:'safe', effect:{health:8}, message:'비바람을 피할 곳을 확보해 마음이 놓입니다.' },
      { text:'무너질까 불안해 포기한다', risk:'safe', effect:{hunger:-5}, message:'안전을 위해 지나쳤습니다.' }
    ]},
  { id:'reef_tidepool', category:'exploration', emoji:'🦀', badge:'물웅덩이',
    title:'썰물이 남긴 갯바위 웅덩이',
    desc:'썰물이 빠지며 갯바위 사이 작은 웅덩이에 게와 작은 물고기들이 갇혔습니다.',
    choices:[
      { text:'맨손으로 잡아본다', risk:'risky', effect:{health:-8, hunger:18}, message:'게 집게에 손을 물렸지만 식량은 확보했습니다.' },
      { text:'낚싯줄이 있다면 침착히 낚아 올린다', risk:'safe', requireItem:'낚싯줄', effect:{hunger:26}, message:'낚싯줄로 손쉽게 여러 마리를 낚았습니다!' },
      { text:'조수가 다시 밀려오기 전에 물러난다', risk:'safe', effect:{health:3}, message:'안전하게 자리를 비켰습니다.' }
    ]},
  { id:'jungle_pool', category:'water', emoji:'💧', badge:'수원 탐색',
    title:'정글 속 고인 웅덩이',
    desc:'목이 타들어 갈 즈음, 정글 깊은 곳에서 맑아 보이는 물웅덩이를 발견했습니다.',
    choices:[
      { text:'그냥 벌컥벌컥 마신다', risk:'risky', effect:{thirst:40, health:-18}, message:'갈증은 풀렸지만 배탈이 났습니다. 물은 늘 끓여야 했는데...' },
      { text:'나뭇잎으로 거르고 불에 끓여 마신다', risk:'safe', effect:{thirst:28, health:6}, message:'번거로웠지만 안전하게 수분을 채웠습니다.' },
      { text:'대신 코코넛을 찾아본다', risk:'balanced', effect:{thirst:14, hunger:6, health:-4}, message:'코코넛 몇 개를 구해 목과 배를 동시에 달랬습니다.' }
    ]},
  { id:'rain_catch', category:'water', emoji:'🌧️', badge:'빗물 수집',
    title:'조용히 내리는 비',
    desc:'거세지 않은 비가 하루 종일 내립니다. 큰 잎사귀들을 엮으면 제법 물을 받을 수 있을 것 같습니다.',
    choices:[
      { text:'하루 종일 빗물을 받는다', risk:'balanced', effect:{thirst:24, hunger:-8, addInv:'빗물통'}, message:'배는 조금 고프지만 넉넉한 빗물통을 확보했습니다.' },
      { text:'비를 피해 몸을 말리는 데 집중한다', risk:'safe', effect:{health:10, thirst:-6}, message:'체온을 지키는 데 집중했습니다.' },
      { text:'비를 맞으며 주변을 정찰한다', risk:'risky', effect:{health:-12, addInv:'표류물 지도조각'}, message:'감기 기운이 돌지만 흥미로운 지도 조각을 주웠습니다.' }
    ]},
  { id:'storm', category:'weather', emoji:'⛈️', badge:'폭풍우',
    title:'수평선을 뒤덮는 먹구름',
    desc:'하늘이 급격히 어두워지고 거센 폭풍우가 몰아칩니다. 얼기설기 세운 은신처가 흔들립니다.',
    choices:[
      { text:'몸으로 기둥을 붙잡고 버틴다', risk:'risky', effect:{health:-22, thirst:14}, message:'은신처는 지켰지만 온몸이 흠뻑 젖고 멍이 들었습니다.' },
      { text:'근처 동굴이나 바위 틈으로 대피한다', risk:'safe', effect:{health:6, hunger:-12}, message:'무사히 피했지만 먹을 것을 챙기지 못했습니다.' },
      { text:'빗물통(있다면)을 내걸고 함께 대피한다', risk:'balanced', requireItem:'빗물통', effect:{thirst:20, health:-4}, message:'폭풍 속에서도 빗물통 덕분에 수분을 넉넉히 모았습니다.' }
    ]},
  { id:'heatwave', category:'weather', emoji:'☀️', badge:'폭염',
    title:'그늘 한 점 없는 더위',
    desc:'구름 한 점 없이 해가 내리쬐고, 모래사장은 발을 델 만큼 뜨겁습니다.',
    choices:[
      { text:'그늘에서 낮잠을 자며 버틴다', risk:'safe', effect:{health:8, thirst:-14}, message:'체력은 지켰지만 갈증이 심해집니다.' },
      { text:'젖은 옷을 두르고 활동을 이어간다', risk:'balanced', effect:{hunger:8, thirst:-10, health:-4}, message:'더위 속에서도 그럭저럭 하루를 보냈습니다.' },
      { text:'바닷물에 몸을 담가 체온을 낮춘다', risk:'risky', effect:{health:10, thirst:-18}, message:'시원했지만 짠물 탓에 갈증이 더 심해졌습니다.' }
    ]},
  { id:'cold_night', category:'weather', emoji:'🌙', badge:'추운 밤',
    title:'유난히 차가운 밤바람',
    desc:'기온이 뚝 떨어진 밤입니다. 모닥불이 꺼지면 밤새 떨어야 할 것 같습니다.',
    choices:[
      { text:'마른 나뭇가지(있다면)로 불을 지킨다', risk:'safe', requireItem:'마른 나뭇가지', effect:{health:10, hunger:-4}, message:'불씨를 지켜 따뜻하게 밤을 넘겼습니다.' },
      { text:'옷가지를 겹겹이 두르고 웅크린다', risk:'balanced', effect:{health:-6}, message:'춥고 뻐근한 밤이었지만 버텨냈습니다.' },
      { text:'움직이며 체온을 유지한다', risk:'risky', effect:{health:-4, hunger:-10, thirst:-8}, message:'체온은 지켰지만 기력을 많이 소모했습니다.' }
    ]},
  { id:'predator', category:'animal', emoji:'🐾', badge:'맹수 조우',
    title:'수풀 너머의 날카로운 눈빛',
    desc:'먹을 것을 찾아 헤매던 중, 덤불 사이로 정체 모를 짐승과 눈이 마주쳤습니다.',
    choices:[
      { text:'소리를 지르며 위협해 쫓아낸다', risk:'risky', effect:{health:-16}, message:'짐승은 물러갔지만 몸싸움에 긁혔습니다.' },
      { text:'녹슨 칼(있다면)을 겨누고 맞선다', risk:'balanced', requireItem:'녹슨 칼', effect:{health:6, hunger:24, addInv:'짐승 가죽'}, message:'칼 덕분에 되려 사냥에 성공했습니다! 가죽까지 얻었습니다.' },
      { text:'천천히 뒷걸음질 치며 자리를 피한다', risk:'safe', effect:{hunger:-10, thirst:-10}, message:'무사히 피했지만 진을 많이 뺐습니다.' }
    ]},
  { id:'small_game', category:'animal', emoji:'🐇', badge:'작은 사냥감',
    title:'덫에 걸릴 듯한 작은 동물',
    desc:'나무뿌리 사이에서 작은 동물 한 마리가 경계 없이 풀을 뜯고 있습니다.',
    choices:[
      { text:'조용히 다가가 맨손으로 잡는다', risk:'risky', effect:{hunger:16, health:-6}, message:'놓칠 뻔했지만 결국 잡아냈습니다.' },
      { text:'간이 덫을 놓고 기다린다', risk:'safe', effect:{hunger:10, health:2}, message:'조급해하지 않고 안전하게 성과를 거뒀습니다.' },
      { text:'놀라게 하지 않고 지나간다', risk:'safe', effect:{health:4}, message:'괜한 위험을 피했습니다.' }
    ]},
  { id:'fever', category:'health', emoji:'🤒', badge:'몸살',
    title:'으슬으슬한 몸살 기운',
    desc:'아침부터 몸이 무겁고 열이 오릅니다. 무리하면 상태가 악화될 것 같습니다.',
    choices:[
      { text:'하루 종일 쉬며 회복에 집중한다', risk:'safe', effect:{health:16, hunger:-10, thirst:-8}, message:'무리하지 않고 쉬어 몸이 한결 나아졌습니다.' },
      { text:'약초를 찾아 헤맨다', risk:'balanced', effect:{health:10, hunger:-6, addInv:'약초'}, message:'다행히 열을 내려줄 것 같은 약초를 발견했습니다.' },
      { text:'아픈 몸을 이끌고 평소처럼 활동한다', risk:'risky', effect:{health:-14, hunger:8}, message:'억지로 버텼지만 몸 상태가 더 나빠졌습니다.' }
    ]},
  { id:'wound', category:'health', emoji:'🩹', badge:'부상',
    title:'날카로운 산호에 베인 상처',
    desc:'물속을 걷다 발바닥을 산호에 깊게 베였습니다. 피가 제법 흐릅니다.',
    choices:[
      { text:'약초(있다면)로 상처를 감싼다', risk:'safe', requireItem:'약초', effect:{health:14}, message:'약초 덕분에 상처가 빠르게 아물기 시작했습니다.' },
      { text:'천 조각으로 지혈만 하고 계속 움직인다', risk:'risky', effect:{health:-10, hunger:6}, message:'상처가 욱신거리지만 하루를 버텼습니다.' },
      { text:'바닷물로 씻어내고 충분히 쉰다', risk:'balanced', effect:{health:4, thirst:-6}, message:'따끔했지만 그럭저럭 상처를 관리했습니다.' }
    ]},
  { id:'raft_wood', category:'craft', emoji:'🪵', badge:'표류목 수거',
    title:'해변에 쌓인 표류목',
    desc:'튼튼해 보이는 표류목 여러 개가 해변 한쪽에 쌓여 있습니다. 뗏목을 만들 수 있을지도 모릅니다.',
    choices:[
      { text:'하루 종일 나무를 옮겨 뗏목 기초를 짠다', risk:'risky', effect:{health:-14, hunger:-14, addInv:'뗏목 뼈대'}, message:'몹시 지쳤지만 뗏목의 뼈대를 완성했습니다.' },
      { text:'일부만 챙겨 은신처를 보강한다', risk:'safe', effect:{health:8, hunger:-6}, message:'무리하지 않고 은신처를 단단히 했습니다.' },
      { text:'거울처럼 빛나는 금속 조각도 함께 챙긴다', risk:'balanced', effect:{hunger:-6, addInv:'신호용 금속판'}, message:'나중에 신호를 보낼 때 쓸 만한 금속판을 발견했습니다.' }
    ]},
  { id:'signal_fire', category:'craft', emoji:'🔥', badge:'봉화대 준비',
    title:'언덕 위의 봉화 자리',
    desc:'섬에서 가장 높은 언덕을 발견했습니다. 이곳에 봉화를 준비해두면 언젠가 쓸모가 있을 것 같습니다.',
    choices:[
      { text:'땔감을 모아 봉화대를 미리 쌓아둔다', risk:'balanced', effect:{hunger:-10, thirst:-8, addInv:'봉화 땔감'}, message:'힘들었지만 언제든 불을 피울 준비를 마쳤습니다.' },
      { text:'대신 전망 좋은 곳에서 바다를 살핀다', risk:'safe', effect:{health:4}, message:'별다른 소득은 없었지만 지형을 익혔습니다.' },
      { text:'무리해서 정상까지 올라 표식을 남긴다', risk:'risky', effect:{health:-10, hunger:-10, addInv:'표식 깃발'}, message:'지쳤지만 멀리서도 보일 표식을 세웠습니다.' }
    ]},
  { id:'bottle_msg', category:'social', emoji:'🍾', badge:'표류병',
    title:'모래에 반쯤 파묻힌 유리병',
    desc:'파도에 밀려온 낡은 유리병 안에 누렇게 바랜 종이가 들어 있습니다. 이 섬에 먼저 다녀간 사람이 있었던 걸까요.',
    choices:[
      { text:'종이를 꺼내 조심스럽게 읽는다', risk:'safe', effect:{health:6, addInv:'낡은 지도'}, message:'섬의 수원지가 표시된 낡은 지도를 얻었습니다.' },
      { text:'병만 챙기고 신경 쓰지 않는다', risk:'safe', effect:{hunger:2}, message:'빈 병은 나중에 쓸모가 있을지도 모릅니다.' },
      { text:'같은 자리를 더 파헤쳐 본다', risk:'risky', effect:{health:-6, addInv:'녹슨 지갑'}, message:'손을 다쳤지만 오래된 지갑 하나를 더 찾았습니다.' }
    ]},
  { id:'old_camp', category:'social', emoji:'⛺', badge:'옛 야영지',
    title:'누군가 머물렀던 흔적',
    desc:'수풀 사이로 무너진 천막과 다 타버린 모닥불 자리를 발견했습니다. 이 섬에도 생존자가 있었던 모양입니다.',
    choices:[
      { text:'잔해를 뒤져 쓸 만한 것을 찾는다', risk:'balanced', effect:{hunger:8, addInv:'낡은 배낭'}, message:'낡았지만 튼튼한 배낭을 발견했습니다.' },
      { text:'조용히 애도하고 자리를 정리해준다', risk:'safe', effect:{health:8}, message:'마음이 복잡했지만 위안을 얻었습니다.' },
      { text:'혹시 몰라 근처를 더 수색한다', risk:'risky', effect:{health:-8, hunger:6, thirst:6}, message:'조금 다쳤지만 남겨진 식수와 식량을 찾아냈습니다.' }
    ]},
  { id:'distant_light', category:'rescue', emoji:'🚢', badge:'수평선의 불빛',
    title:'밤바다 저 너머의 빛',
    desc:'깊은 밤, 수평선 저편에서 배의 불빛으로 보이는 무언가가 반짝입니다.',
    choices:[
      { text:'생나무를 던져 짙은 연기를 피운다', risk:'balanced', effect:{health:-8, hunger:-10}, rescueChance:0.32, message:'짙은 연기가 하늘로 치솟았습니다. 저들이 봐줄까요?' },
      { text:'신호용 금속판(있다면)으로 빛을 반사시킨다', risk:'safe', requireItem:'신호용 금속판', effect:{hunger:-6}, rescueChance:0.55, message:'정확한 빛 신호를 밤바다로 쏘아 보냈습니다.' },
      { text:'무리하지 않고 체력을 비축해 둔다', risk:'safe', effect:{health:12}, rescueChance:0.0, message:'기회를 흘려보냈지만 푹 쉬어 체력을 회복했습니다.' }
    ]},
  { id:'plane_flyby', category:'rescue', emoji:'✈️', badge:'항공기 포착',
    title:'하늘을 가로지르는 비행운',
    desc:'까마득히 높은 하늘에서 비행기 한 대가 섬 위를 지나가고 있습니다.',
    choices:[
      { text:'봉화 땔감(있다면)에 불을 붙인다', risk:'safe', requireItem:'봉화 땔감', effect:{hunger:-4}, rescueChance:0.5, message:'미리 준비해둔 봉화가 순식간에 타올랐습니다!' },
      { text:'표식 깃발(있다면)을 힘껏 흔든다', risk:'safe', requireItem:'표식 깃발', effect:{health:-4}, rescueChance:0.4, message:'있는 힘껏 깃발을 흔들었습니다.' },
      { text:'맨몸으로 해변에 SOS 글자를 새긴다', risk:'risky', effect:{health:-10, hunger:-8}, rescueChance:0.2, message:'급히 모래에 커다란 SOS를 새겼습니다.' }
    ]},
  { id:'night_noise', category:'weather', emoji:'🌑', badge:'정체 모를 소리',
    title:'어둠 속에서 들리는 발소리',
    desc:'잠들려는 순간, 은신처 밖에서 무언가 부스럭거리는 소리가 들립니다.',
    choices:[
      { text:'용기를 내 횃불을 들고 확인한다', risk:'risky', effect:{health:-8, hunger:6}, message:'놀란 짐승이 먹이를 두고 달아났습니다. 뜻밖의 소득입니다.' },
      { text:'숨죽이고 아침이 오길 기다린다', risk:'safe', effect:{health:-4, thirst:-4}, message:'뜬눈으로 밤을 지새웠지만 별일은 없었습니다.' },
      { text:'모닥불을 키워 짐승을 쫓는다', risk:'balanced', effect:{hunger:-6, health:4}, message:'불빛 덕분에 안심하고 잠들 수 있었습니다.' }
    ]}
];

/* ============ 상태 ============ */
let gameState = null;
let deck = [];
let lastScenarioId = null;

/* ============ 특성 카드 렌더 ============ */
let selectedTrait = TRAITS[0].key;
function renderTraits(){
  const grid = document.getElementById('trait-grid');
  grid.innerHTML = '';
  TRAITS.forEach(t=>{
    const el = document.createElement('div');
    el.className = 'trait-card' + (t.key===selectedTrait ? ' selected' : '');
    el.onclick = ()=>{ selectedTrait = t.key; renderTraits(); };
    el.innerHTML = `
      <div class="trait-icon">${t.icon}</div>
      <div class="trait-name">${t.name}</div>
      <div class="trait-desc">${t.desc}</div>`;
    grid.appendChild(el);
  });
}
renderTraits();

/* ============ 유틸 ============ */
function clamp(v){ return Math.max(0, Math.min(100, v)); }
function hasItem(name){ return gameState.inventory.includes(name); }
function currentTrait(){ return TRAITS.find(t=>t.key===gameState.traitKey); }

function modify(effectVal, statKey){
  if (effectVal === undefined) return 0;
  const trait = currentTrait();
  let v = effectVal;
  if (trait.key==='fisher' && (statKey==='hunger'||statKey==='thirst') && v>0) v = Math.round(v*1.25);
  if (trait.key==='outdoors' && statKey==='health' && v<0) v = Math.round(v*0.7);
  return v;
}

function buildDeck(){
  deck = [...scenarioPool].sort(()=>Math.random()-0.5);
}

function nextScenario(){
  if (deck.length===0) buildDeck();
  let idx = 0;
  if (deck[0].id === lastScenarioId && deck.length>1) idx = 1;
  const s = deck.splice(idx,1)[0];
  lastScenarioId = s.id;
  return s;
}

/* ============ 시작 ============ */
function startGame(){
  document.getElementById('start-screen').classList.add('hidden');
  document.getElementById('gameover-screen').classList.add('hidden');
  document.getElementById('game-screen').classList.remove('hidden');

  const trait = TRAITS.find(t=>t.key===selectedTrait);
  const nameInput = document.getElementById('name-input').value.trim();
  gameState = {
    day:1, health:100, hunger:100, thirst:100,
    inventory:['기본 성냥', trait.startItem],
    traitKey: trait.key,
    name: nameInput || '이름 없는 표류자'
  };
  deck = [];
  lastScenarioId = null;

  document.getElementById('castaway-name').innerText = gameState.name;
  document.getElementById('avatar-svg').setAttribute('data-trait', trait.key);

  initScene();
  updateUI();
  loadNextScenario();
}

/* ============ UI 갱신 ============ */
const DAY_FLAVORS = ['해가 떠오르다','바람이 잔잔하다','파도가 높다','안개가 짙다','볕이 따갑다','구름이 낮다'];

function updateUI(){
  document.getElementById('stat-day').innerText = gameState.day;
  document.getElementById('day-flavor').innerText = DAY_FLAVORS[gameState.day % DAY_FLAVORS.length];

  setGauge('health', gameState.health);
  setGauge('hunger', gameState.hunger);
  setGauge('thirst', gameState.thirst);
  updateAvatar();

  const inv = document.getElementById('inventory-list');
  inv.innerHTML = '';
  gameState.inventory.forEach(item=>{
    const chip = document.createElement('span');
    chip.className = 'chip';
    chip.innerText = item;
    inv.appendChild(chip);
  });
}

const MOOD_LABEL = {
  happy:'컨디션: 활기참',
  normal:'컨디션: 양호함',
  tired:'컨디션: 지쳐 있음',
  sick:'컨디션: 위태로움'
};
function getMoodState(){
  if (gameState.health<20) return 'sick';
  const avg = (gameState.health+gameState.hunger+gameState.thirst)/3;
  if (avg>=70) return 'happy';
  if (avg>=40) return 'normal';
  if (avg>=15) return 'tired';
  return 'sick';
}
function updateAvatar(){
  const state = getMoodState();
  document.getElementById('avatar-svg').setAttribute('data-state', state);
  document.getElementById('castaway-mood').innerText = MOOD_LABEL[state];
}

function setGauge(key, val){
  val = clamp(val);
  document.getElementById('gauge-'+key).style.setProperty('--pct', val);
  document.getElementById('num-'+key).innerText = val;
  document.getElementById('text-'+key).innerText = `${val}/100`;
}

/* ============ 시나리오 로드 ============ */
function loadNextScenario(){
  if (gameState.health<=0 || gameState.hunger<=0 || gameState.thirst<=0){
    endByStat();
    return;
  }

  const s = nextScenario();
  gameState.current = s;

  document.getElementById('scenario-box').style.setProperty('--cat-color', CAT_COLOR[s.category] || 'var(--gold)');
  document.getElementById('scenario-emoji-bg').innerText = s.emoji;
  document.getElementById('scenario-badge').innerText = s.badge;
  document.getElementById('scenario-title').innerText = s.title;
  document.getElementById('scenario-desc').innerText = s.desc;
  applyCategoryTheme(s.category, NIGHT_IDS.includes(s.id));

  const box = document.getElementById('choices-container');
  box.innerHTML = '';

  s.choices.forEach((choice, i)=>{
    const enabled = !choice.requireItem || hasItem(choice.requireItem);
    const btn = document.createElement('button');
    btn.className = 'choice-btn';
    btn.style.setProperty('--risk-color', RISK_COLOR[choice.risk] || 'var(--line-strong)');
    btn.disabled = !enabled;
    btn.innerHTML = `
      <span><span class="choice-num">${i+1}</span>${choice.text}${choice.requireItem ? ` <span style="color:var(--ink-dim);font-size:11.5px;">(${choice.requireItem} 필요)</span>` : ''}</span>
      <span class="choice-arrow">➔</span>`;
    if (enabled) btn.onclick = ()=>selectChoice(choice);
    box.appendChild(btn);
  });
}

/* ============ 선택 처리 ============ */
function selectChoice(choice){
  const e = choice.effect || {};
  const dHealth = modify(e.health,'health');
  const dHunger = modify(e.hunger,'hunger');
  const dThirst = modify(e.thirst,'thirst');
  gameState.health = clamp(gameState.health + dHealth);
  gameState.hunger = clamp(gameState.hunger + dHunger);
  gameState.thirst = clamp(gameState.thirst + dThirst);

  if (e.addInv && !gameState.inventory.includes(e.addInv)) gameState.inventory.push(e.addInv);
  if (e.removeInv) gameState.inventory = gameState.inventory.filter(x=>x!==e.removeInv);

  playAction(pickActionType(dHealth, dHunger, dThirst, gameState.current && gameState.current.category));

  let rescueChance = choice.rescueChance || 0;
  if (rescueChance>0){
    const trait = currentTrait();
    if (trait.key==='optimist') rescueChance += 0.08;
    rescueChance += Math.min(0.15, gameState.day*0.006);
    if (Math.random() < rescueChance){
      updateUI();
      triggerVictory();
      return;
    }
  }

  if (gameState.health<=0 || gameState.hunger<=0 || gameState.thirst<=0){
    updateUI();
    endByStat();
    return;
  }

  advanceDay();
}

function advanceDay(){
  gameState.day += 1;
  const trait = currentTrait();

  const hardMode = gameState.day>10 ? 1 : 0;
  gameState.hunger = clamp(gameState.hunger - (10+hardMode));
  gameState.thirst = clamp(gameState.thirst - (12+hardMode));

  if (trait.key==='optimist' && gameState.health<100) gameState.health = clamp(gameState.health+3);
  if (gameState.hunger>60 && gameState.thirst>60) gameState.health = clamp(gameState.health+2);

  updateUI();

  if (gameState.health<=0 || gameState.hunger<=0 || gameState.thirst<=0){
    endByStat();
    return;
  }
  loadNextScenario();
}

/* ============ 종료 처리 ============ */
const DEATH_MESSAGES = {
  health:['거듭된 부상과 탈진을 끝내 이겨내지 못했습니다.','몸이 더는 버텨주지 않았습니다.'],
  hunger:['오랜 굶주림 끝에 기력을 잃고 말았습니다.','먹을 것을 구하지 못해 쓰러졌습니다.'],
  thirst:['갈증을 이기지 못하고 정신을 잃었습니다.','물을 구하지 못한 날들이 결국 발목을 잡았습니다.']
};
function endByStat(){
  let key = 'health';
  if (gameState.hunger<=0) key='hunger';
  if (gameState.thirst<=0) key='thirst';
  const msgs = DEATH_MESSAGES[key];
  triggerGameOver(msgs[Math.floor(Math.random()*msgs.length)]);
}

function triggerGameOver(reason){
  document.getElementById('game-screen').classList.add('hidden');
  document.getElementById('gameover-screen').classList.remove('hidden');
  document.getElementById('gameover-emoji').innerText = '💀';
  const title = document.getElementById('gameover-title');
  title.innerText = '표류, 여기서 끝나다';
  title.style.color = 'var(--coral)';
  document.getElementById('gameover-reason').innerText = `${gameState.name}. ${reason}`;
  document.getElementById('final-days').innerText = `Day ${gameState.day}`;
  renderBadges(false);
}

function triggerVictory(){
  playAction('rescue');
  document.getElementById('game-screen').classList.add('hidden');
  document.getElementById('gameover-screen').classList.remove('hidden');
  document.getElementById('gameover-emoji').innerText = '🚁';
  const title = document.getElementById('gameover-title');
  let msg;
  if (gameState.day<=6) msg='구조되다 — 짧지만 강렬한 표류였습니다.';
  else if (gameState.day<=14) msg='구조되다 — 섬을 완전히 내 것으로 만들었습니다.';
  else msg='구조되다 — 전설적인 생존기가 되었습니다.';
  title.innerText = msg;
  title.style.color = 'var(--teal)';
  document.getElementById('gameover-reason').innerText = `${gameState.name}은(는) 총 ${gameState.day}일간의 표류 끝에 마침내 구조선에 발견되었습니다.`;
  document.getElementById('final-days').innerText = `Day ${gameState.day}`;
  renderBadges(true);
}

function renderBadges(survived){
  const wrap = document.getElementById('badges');
  wrap.innerHTML = '';
  const list = [];
  if (survived) list.push('구조 성공');
  if (gameState.day>=15) list.push('장기 생존자');
  if (gameState.inventory.length>=6) list.push('만물 수집가');
  if (gameState.health>=80 && gameState.hunger>=60 && gameState.thirst>=60) list.push('완벽한 컨디션');
  list.forEach(b=>{
    const s = document.createElement('span');
    s.className = 'ach';
    s.innerText = b;
    wrap.appendChild(s);
  });
}

function resetGame(){
  document.getElementById('gameover-screen').classList.add('hidden');
  document.getElementById('start-screen').classList.remove('hidden');
  renderTraits();
}

/* ============================================================
   3D 배경 — 섬 다이오라마 (Three.js)
   ============================================================ */
const NIGHT_IDS = ['cold_night','night_noise','distant_light'];
const CAT_THEME = {
  exploration:{sky:[0x35506a,0x0a121a], fog:0x0a141c, light:0xffe3b0, lightI:1.0,  ocean:0x1c4f57, particle:'fireflies'},
  water:      {sky:[0x1c3f52,0x081119], fog:0x081119, light:0xbfe8ff, lightI:0.9,  ocean:0x1a6b78, particle:'bubbles'},
  weather:    {sky:[0x1a2030,0x05070b], fog:0x05070b, light:0x9fb3d1, lightI:0.55, ocean:0x123038, particle:'rain'},
  animal:     {sky:[0x243a24,0x070a06], fog:0x070a06, light:0xffdca0, lightI:0.85, ocean:0x1c4f57, particle:'fireflies'},
  health:     {sky:[0x2e2024,0x0a0608], fog:0x0a0608, light:0xffb37a, lightI:0.75, ocean:0x1c4f57, particle:'embers'},
  craft:      {sky:[0x2c2416,0x0a0805], fog:0x0a0805, light:0xffcf8a, lightI:0.85, ocean:0x1c4f57, particle:'embers'},
  social:     {sky:[0x272a40,0x080910], fog:0x080910, light:0xd8d6ff, lightI:0.7,  ocean:0x1c3f57, particle:'fireflies'},
  rescue:     {sky:[0x0f2436,0x03060a], fog:0x03060a, light:0xffffff, lightI:1.1,  ocean:0x123a4a, particle:'sparkle'}
};

let renderer=null, threeScene=null, camera=null, clock=null;
let oceanMesh=null, oceanBasePos=null;
let particleSystem=null;
let bursts=[];
let fireLight=null, sunLight=null, ambientLight=null;
let shakeT=0, shakeMag=0;

function initScene(){
  if (renderer){ resizeScene(); return; }
  if (typeof THREE === 'undefined') return;
  const stage = document.getElementById('scene-stage');
  const w = stage.clientWidth || 320, h = stage.clientHeight || 190;

  threeScene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(42, w/h, 0.1, 60);
  camera.position.set(0, 1.9, 6.2);
  camera.lookAt(0, 0.4, 0);

  renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1, 1.6));
  renderer.setSize(w, h);
  stage.insertBefore(renderer.domElement, stage.firstChild);

  clock = new THREE.Clock();

  ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
  threeScene.add(ambientLight);
  sunLight = new THREE.DirectionalLight(0xffe3b0, 1.0);
  sunLight.position.set(-3, 4, 2);
  threeScene.add(sunLight);
  fireLight = new THREE.PointLight(0xff9a4d, 0, 6);
  fireLight.position.set(0.9, 0.35, 0.6);
  threeScene.add(fireLight);

  const oceanGeo = new THREE.PlaneGeometry(18, 9, 36, 18);
  oceanGeo.rotateX(-Math.PI/2);
  oceanBasePos = oceanGeo.attributes.position.array.slice();
  const oceanMat = new THREE.MeshStandardMaterial({color:0x1c4f57, roughness:0.55, metalness:0.15, flatShading:true});
  oceanMesh = new THREE.Mesh(oceanGeo, oceanMat);
  oceanMesh.position.y = -0.55;
  threeScene.add(oceanMesh);

  const sandMat = new THREE.MeshStandardMaterial({color:0xC9A86A, roughness:0.9, flatShading:true});
  const sand = new THREE.Mesh(new THREE.CylinderGeometry(2.5, 2.8, 0.35, 20), sandMat);
  sand.position.y = -0.35;
  threeScene.add(sand);

  const palm = new THREE.Group();
  palm.name = 'palm';
  const trunkMat = new THREE.MeshStandardMaterial({color:0x6b4a30, roughness:0.9});
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.11, 1.9, 6), trunkMat);
  trunk.position.set(0.9, 0.6, -0.3);
  trunk.rotation.z = 0.18;
  palm.add(trunk);
  const frondMat = new THREE.MeshStandardMaterial({color:0x2f6b4f, roughness:0.8, side:THREE.DoubleSide, flatShading:true});
  for(let i=0;i<6;i++){
    const frond = new THREE.Mesh(new THREE.ConeGeometry(0.12, 1.1, 4), frondMat);
    frond.position.set(0.9+Math.sin(i)*0.15, 1.55, -0.3+Math.cos(i)*0.15);
    frond.rotation.z = Math.PI/2 + (i-2.5)*0.35;
    frond.rotation.y = i*1.1;
    palm.add(frond);
  }
  threeScene.add(palm);

  const fireGroup = new THREE.Group();
  fireGroup.name = 'fireGroup';
  const logMat = new THREE.MeshStandardMaterial({color:0x4a3626, roughness:1});
  for(let i=0;i<3;i++){
    const log = new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,0.6,5), logMat);
    log.rotation.z = Math.PI/2;
    log.rotation.y = i*1.1;
    log.position.set(0.9,0.05,0.6);
    fireGroup.add(log);
  }
  const flameMat = new THREE.MeshBasicMaterial({color:0xff8a3d});
  const flame = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.32, 6), flameMat);
  flame.name = 'flame';
  flame.position.set(0.9, 0.24, 0.6);
  fireGroup.add(flame);
  threeScene.add(fireGroup);

  buildCastaway();
  applyCategoryTheme('exploration', false);
  animate();
}

function buildCastaway(){
  const skin = new THREE.MeshStandardMaterial({color:0xD79A66, roughness:0.8});
  const hairMat = new THREE.MeshStandardMaterial({color:0x3B2A1F, roughness:0.9});
  const bandanaMat = new THREE.MeshStandardMaterial({color:0xD6A94C, roughness:0.7});
  const shirtMat = new THREE.MeshStandardMaterial({color:0xE7E0CE, roughness:0.85});
  const pantsMat = new THREE.MeshStandardMaterial({color:0x5a4634, roughness:0.9});

  const person = new THREE.Group();
  person.name = 'castaway';

  const hips = new THREE.Group();
  hips.name = 'hips';
  hips.position.set(-0.85, -0.12, 0.95);
  hips.rotation.y = -0.5;
  person.add(hips);

  // legs
  [-0.07, 0.07].forEach(x=>{
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.045,0.05,0.55,6), pantsMat);
    leg.position.set(x, 0.28, 0);
    hips.add(leg);
  });

  // torso
  const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.13,0.16,0.42,7), shirtMat);
  torso.position.set(0, 0.72, 0);
  torso.name = 'torso';
  hips.add(torso);

  // head + face
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.14,10,8), skin);
  head.position.set(0, 1.06, 0);
  hips.add(head);
  const hair = new THREE.Mesh(new THREE.SphereGeometry(0.145,10,8,0,Math.PI*2,0,Math.PI*0.55), hairMat);
  hair.position.set(0, 1.09, 0);
  hips.add(hair);
  const bandana = new THREE.Mesh(new THREE.TorusGeometry(0.145,0.025,6,12), bandanaMat);
  bandana.rotation.x = Math.PI/2;
  bandana.position.set(0, 1.03, 0);
  hips.add(bandana);

  // arms (shoulder pivots so they can raise/lower)
  const shoulderL = new THREE.Group(); shoulderL.position.set(-0.16,0.86,0); shoulderL.name='shoulderL';
  const shoulderR = new THREE.Group(); shoulderR.position.set(0.16,0.86,0); shoulderR.name='shoulderR';
  hips.add(shoulderL, shoulderR);
  [shoulderL, shoulderR].forEach(s=>{
    const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.035,0.04,0.36,6), skin);
    arm.position.set(0,-0.18,0);
    s.add(arm);
  });
  shoulderL.rotation.z = 0.18;
  shoulderR.rotation.z = -0.18;

  threeScene.add(person);
}

const CASTAWAY_POSES = {
  idle:  { arm:0.18 },
  crouch:{ arm:0.35, crouch:true },
  wave:  { arm:2.5, wave:true }
};
let castawayPose = 'idle';
let castawayFlinchT = 0, castawayHopT = 0;

function setCastawayPose(category){
  if (category==='rescue') castawayPose = 'wave';
  else if (category==='weather') castawayPose = 'crouch';
  else castawayPose = 'idle';
}


function resizeScene(){
  if (!renderer) return;
  const stage = document.getElementById('scene-stage');
  const w = stage.clientWidth, h = stage.clientHeight;
  if (!w || !h) return;
  camera.aspect = w/h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
}
window.addEventListener('resize', resizeScene);

function disposeParticles(){
  if (!particleSystem) return;
  if (particleSystem.points){
    threeScene.remove(particleSystem.points);
    particleSystem.points.geometry.dispose();
    particleSystem.points.material.dispose();
  }
  if (particleSystem.stars){
    threeScene.remove(particleSystem.stars.points);
    particleSystem.stars.points.geometry.dispose();
    particleSystem.stars.points.material.dispose();
  }
  particleSystem = null;
}

function makeParticles(type, count, spread){
  const geo = new THREE.BufferGeometry();
  const positions = new Float32Array(count*3);
  const velocities = new Float32Array(count*3);
  for(let i=0;i<count;i++){
    const ix=i*3;
    if (type==='rain'){
      positions[ix]=(Math.random()-0.5)*spread; positions[ix+1]=Math.random()*4; positions[ix+2]=(Math.random()-0.5)*spread*0.6;
      velocities[ix+1] = -5-Math.random()*2;
    } else if (type==='bubbles'){
      positions[ix]=(Math.random()-0.5)*2.2; positions[ix+1]=-0.5+Math.random()*0.3; positions[ix+2]=(Math.random()-0.5)*1.6;
      velocities[ix+1] = 0.25+Math.random()*0.3;
    } else if (type==='embers'){
      positions[ix]=0.9+(Math.random()-0.5)*0.5; positions[ix+1]=0.1+Math.random()*0.4; positions[ix+2]=0.6+(Math.random()-0.5)*0.5;
      velocities[ix+1] = 0.4+Math.random()*0.5;
    } else if (type==='fireflies'){
      positions[ix]=(Math.random()-0.5)*3.5; positions[ix+1]=0.4+Math.random()*1.2; positions[ix+2]=(Math.random()-0.5)*2.5;
    } else if (type==='sparkle'){
      positions[ix]=(Math.random()-0.5)*0.6; positions[ix+1]=0.3+Math.random()*2.2; positions[ix+2]=-3-Math.random()*1.5;
      velocities[ix+1] = 0.15+Math.random()*0.2;
    } else if (type==='stars'){
      positions[ix]=(Math.random()-0.5)*16; positions[ix+1]=2.5+Math.random()*3; positions[ix+2]=-4-Math.random()*4;
    }
  }
  geo.setAttribute('position', new THREE.BufferAttribute(positions,3));
  const colorMap = { rain:0x9fd3ff, bubbles:0x8fe0e8, embers:0xff9a4d, fireflies:0xffd97a, sparkle:0xffffff, stars:0xffffff };
  const sizeMap = { rain:0.05, bubbles:0.045, embers:0.055, fireflies:0.09, sparkle:0.08, stars:0.045 };
  const glow = (type==='fireflies'||type==='sparkle'||type==='embers');
  const mat = new THREE.PointsMaterial({color:colorMap[type]||0xffffff, size:sizeMap[type]||0.06, transparent:true, opacity:0.85, blending: glow?THREE.AdditiveBlending:THREE.NormalBlending, depthWrite:false});
  const points = new THREE.Points(geo, mat);
  return { points, type, velocities, count };
}

function applyCategoryTheme(category, night){
  if (!renderer) return;
  const theme = CAT_THEME[category] || CAT_THEME.exploration;
  const stage = document.getElementById('scene-stage');
  const topC = new THREE.Color(theme.sky[0]);
  const botC = new THREE.Color(theme.sky[1]);
  if (night){ topC.multiplyScalar(0.45); botC.multiplyScalar(0.5); }
  stage.style.background = `linear-gradient(180deg, #${topC.getHexString()} 0%, #${botC.getHexString()} 100%)`;
  threeScene.fog = new THREE.Fog(theme.fog, 4, 13);

  sunLight.color.setHex(theme.light);
  sunLight.intensity = night ? theme.lightI*0.35 : theme.lightI;
  ambientLight.intensity = night ? 0.22 : 0.5;
  oceanMesh.material.color.setHex(theme.ocean);

  const fireGroup = threeScene.getObjectByName('fireGroup');
  const wantsFire = ['craft','health','animal'].includes(category) || night;
  fireLight.intensity = wantsFire ? 1.1 : 0;
  fireGroup.visible = wantsFire;
  setCastawayPose(category);

  disposeParticles();
  particleSystem = makeParticles(theme.particle, theme.particle==='rain'?260:70, 8);
  threeScene.add(particleSystem.points);
  if (night){
    const stars = makeParticles('stars', 90, 0);
    threeScene.add(stars.points);
    particleSystem.stars = stars;
  }
}

function pickActionType(dh, dHu, dTh, category){
  if (dh <= -10) return 'damage';
  if (category==='water' && dTh>0) return 'water';
  if (dh>0 || dHu>0 || dTh>0) return 'heal';
  if (dh<0) return 'damage';
  return 'neutral';
}

function shakeCamera(mag){ shakeMag = mag; shakeT = 0.35; }

function playAction(type){
  if (!renderer || type==='neutral') return;
  const flash = document.getElementById('scene-flash');
  let color=0xffffff, count=40, spread=1.4, upward=1.2, flashColor='255,255,255', flashOpacity=0.2, maxLife=0.6;

  if (type==='damage'){ color=0xe0694f; flashColor='222,90,70'; flashOpacity=0.28; upward=0.6; shakeCamera(0.14); castawayFlinchT=0.4; }
  else if (type==='heal'){ color=0xd6a94c; flashColor='214,169,76'; flashOpacity=0.18; upward=1.4; castawayHopT=0.35; }
  else if (type==='water'){ color=0x6fc7d0; flashColor='111,199,208'; flashOpacity=0.16; upward=0.9; }
  else if (type==='rescue'){ color=0xffffff; count=90; flashColor='255,255,255'; flashOpacity=0.55; upward=2.0; maxLife=1.1; castawayHopT=0.9; }
  else return;

  const geo = new THREE.BufferGeometry();
  const positions = new Float32Array(count*3);
  const vel = new Float32Array(count*3);
  const originX = type==='water' ? 0 : 0.4, originY = type==='water' ? -0.4 : 0.6, originZ = type==='water' ? 0 : 0.3;
  for(let i=0;i<count;i++){
    const ix=i*3;
    positions[ix]=originX+(Math.random()-0.5)*spread;
    positions[ix+1]=originY+(Math.random()-0.5)*0.4;
    positions[ix+2]=originZ+(Math.random()-0.5)*spread*0.6;
    vel[ix]=(Math.random()-0.5)*1.2;
    vel[ix+1]=upward*(0.6+Math.random()*0.8);
    vel[ix+2]=(Math.random()-0.5)*1.2;
  }
  geo.setAttribute('position', new THREE.BufferAttribute(positions,3));
  const mat = new THREE.PointsMaterial({color, size:0.08, transparent:true, opacity:0.95, blending:THREE.AdditiveBlending, depthWrite:false});
  const points = new THREE.Points(geo, mat);
  threeScene.add(points);
  bursts.push({ life:0, maxLife, points, vel, mat });

  flash.style.transition = 'opacity 0.08s ease-out';
  flash.style.background = `rgb(${flashColor})`;
  flash.style.opacity = flashOpacity;
  setTimeout(()=>{ flash.style.transition='opacity 0.5s ease-out'; flash.style.opacity=0; }, 90);
}

function animate(){
  requestAnimationFrame(animate);
  const gameScreen = document.getElementById('game-screen');
  if (!renderer || gameScreen.classList.contains('hidden')) return;

  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  const pos = oceanMesh.geometry.attributes.position;
  for(let i=0;i<pos.count;i++){
    const bx=oceanBasePos[i*3], bz=oceanBasePos[i*3+2], by=oceanBasePos[i*3+1];
    pos.setY(i, by + Math.sin(bx*0.6+t*1.2)*0.08 + Math.cos(bz*0.5+t*0.9)*0.06);
  }
  pos.needsUpdate = true;

  const palm = threeScene.getObjectByName('palm');
  if (palm) palm.rotation.z = Math.sin(t*0.7)*0.04;

  const hips = threeScene.getObjectByName('hips');
  if (hips){
    const pose = CASTAWAY_POSES[castawayPose] || CASTAWAY_POSES.idle;
    let bob = Math.sin(t*1.6)*0.015;
    let baseY = -0.12;
    if (pose.crouch) baseY -= 0.08;
    if (castawayHopT>0){ castawayHopT -= dt; bob += Math.max(0,Math.sin((0.35-castawayHopT)/0.35*Math.PI))*0.12; }
    hips.position.y = baseY + bob;

    let armTarget = pose.arm;
    if (pose.wave) armTarget = 2.3 + Math.sin(t*6)*0.35;
    const shoulderL = hips.getObjectByName('shoulderL');
    const shoulderR = hips.getObjectByName('shoulderR');
    if (shoulderL) shoulderL.rotation.z += (armTarget - shoulderL.rotation.z)*Math.min(1,dt*6);
    if (shoulderR) shoulderR.rotation.z += (-armTarget - shoulderR.rotation.z)*Math.min(1,dt*6);

    if (castawayFlinchT>0){
      castawayFlinchT -= dt;
      hips.rotation.x = Math.sin(castawayFlinchT*30)*0.12*(castawayFlinchT/0.4);
    } else {
      hips.rotation.x = 0;
    }
  }

  const fireGroup = threeScene.getObjectByName('fireGroup');
  if (fireGroup && fireGroup.visible){
    const flame = fireGroup.getObjectByName('flame');
    if (flame){ flame.scale.y = 1+Math.sin(t*14)*0.15; flame.scale.x = 1+Math.cos(t*11)*0.1; }
    fireLight.intensity = 1.0 + Math.sin(t*16)*0.2;
  }

  if (particleSystem && particleSystem.points){
    const p = particleSystem.points.geometry.attributes.position;
    const type = particleSystem.type;
    for(let i=0;i<particleSystem.count;i++){
      const ix=i*3;
      if (type==='rain'){
        p.array[ix+1] += particleSystem.velocities[ix+1]*dt;
        if (p.array[ix+1] < -0.5) p.array[ix+1] = 3+Math.random()*1.5;
      } else if (type==='bubbles'){
        p.array[ix+1] += particleSystem.velocities[ix+1]*dt;
        if (p.array[ix+1] > 0.6) p.array[ix+1] = -0.5;
      } else if (type==='embers'){
        p.array[ix+1] += particleSystem.velocities[ix+1]*dt;
        p.array[ix] += Math.sin(t*2+i)*0.002;
        if (p.array[ix+1] > 1.8) p.array[ix+1] = 0.1;
      } else if (type==='fireflies'){
        p.array[ix]   += Math.sin(t*0.8+i)*0.004;
        p.array[ix+1] += Math.cos(t*1.1+i)*0.003;
        p.array[ix+2] += Math.sin(t*0.6+i*1.3)*0.004;
      } else if (type==='sparkle'){
        p.array[ix+1] += particleSystem.velocities[ix+1]*dt;
        if (p.array[ix+1] > 2.6) p.array[ix+1] = 0.3;
      }
    }
    p.needsUpdate = true;
    if (type==='fireflies' || type==='sparkle') particleSystem.points.material.opacity = 0.6+Math.sin(t*3)*0.3;
  }
  if (particleSystem && particleSystem.stars){
    particleSystem.stars.points.material.opacity = 0.5+Math.sin(t*1.5)*0.2;
  }

  for(let i=bursts.length-1;i>=0;i--){
    const b = bursts[i];
    b.life += dt;
    const arr = b.points.geometry.attributes.position.array;
    for(let j=0;j<arr.length/3;j++){
      const jx=j*3;
      arr[jx]   += b.vel[jx]*dt;
      arr[jx+1] += b.vel[jx+1]*dt;
      arr[jx+2] += b.vel[jx+2]*dt;
      b.vel[jx+1] -= dt*1.6;
    }
    b.points.geometry.attributes.position.needsUpdate = true;
    b.mat.opacity = Math.max(0, 1-b.life/b.maxLife);
    if (b.life >= b.maxLife){
      threeScene.remove(b.points);
      b.points.geometry.dispose();
      b.mat.dispose();
      bursts.splice(i,1);
    }
  }

  let camX = Math.sin(t*0.15)*0.35;
  let camY = 1.9 + Math.sin(t*0.5)*0.04;
  if (shakeT>0){
    shakeT -= dt;
    camX += (Math.random()-0.5)*shakeMag;
    camY += (Math.random()-0.5)*shakeMag;
  }
  camera.position.x = camX;
  camera.position.y = camY;
  camera.lookAt(0, 0.4, 0);

  renderer.render(threeScene, camera);
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return Response(GAME_HTML, mimetype="text/html")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
