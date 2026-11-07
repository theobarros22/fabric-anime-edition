// Personagens 2D oficiais (vetor plano) - Tito, Bozo, Gengivao, Cabeca de Ovo, Nove Dedos
// busto(nome, {expr:'neutro'|'bravo'|'surpreso'|'rindo', m:0..1 (boca), blink:bool, dedo:graus|null, martelo:graus|null})
// Origem = centro da cabeca; raio da cabeca ~100.
(function(G){
const C={tito:{skin:'#D19D72',skinS:'#B98457',hair:'#2A1A14',shirt:'#315570',under:'#E8E3D8'},
 bozo:{skin:'#E5BE98',skinS:'#CFA27C',hair:'#6B4A30',grey:'#9A9A9A',shirt:'#7E9847',shirtS:'#6A8240'},
 ggv:{skin:'#D6A27C',skinS:'#BE8B66',beard:'#9A9A9A',suit:'#1F1C25',shirt:'#EDEAE2'},
 ovo:{skin:'#D9A56A',skinS:'#B98A54',suit:'#1B1B24',tie:'#B01E32',shirt:'#F1EEE6',wood:'#B98B3A',woodD:'#6B3F23'},
 nove:{skin:'#D9A07A',skinS:'#C98E68',hair:'#F3F1EA',hairS:'#D9D6CC',shirt:'#D8432F',star:'#F2C230',nose:'#E0907A',mouth:'#7A1F1A'}};
const MOUTH='#7A1F1A', MOUTHL='#C1584A';
function olhosPontos(ex,y,blink,r){return [-1,1].map(s=>blink?`<path d="M${s*ex-r} ${y} L${s*ex+r} ${y}" stroke="#1B0E09" stroke-width="5" stroke-linecap="round"/>`:`<circle cx="${s*ex}" cy="${y}" r="${r}" fill="#1B0E09"/>`).join('')}
function boca(y,m,w,col,sm){ if(sm) return `<path d="M${-w-6} ${y-2} Q0 ${y+44} ${w+6} ${y-2} Z" fill="${col}"/><path d="M${-w+8} ${y+12} Q0 ${y+34} ${w-8} ${y+12} Q0 ${y+20} ${-w+8} ${y+12}Z" fill="#C1584A"/>`; if(m<0.08) return `<path d="M${-w} ${y} Q0 ${y+4} ${w} ${y}" fill="none" stroke="${col}" stroke-width="7" stroke-linecap="round"/>`; return `<ellipse cx="0" cy="${y+m*8}" rx="${w*(0.55+0.45*m)}" ry="${6+m*22}" fill="${col}"/>`}
function star(cx,cy,R,r,fill){let p=[];for(let i=0;i<10;i++){const q=i%2?r:R,a=-Math.PI/2+i*Math.PI/5;p.push((cx+q*Math.cos(a)).toFixed(1)+','+(cy+q*Math.sin(a)).toFixed(1))}return `<polygon points="${p.join(' ')}" fill="${fill}"/>`}
const B={
tito(o){const c=C.tito,e=o.expr||'neutro',m=o.m||0;let g='';
 g+=`<path d="M-160 300 C-160 160 -90 120 -40 112 L40 112 C90 120 160 160 160 300 Z" fill="${c.shirt}"/><polygon points="-26,112 0,160 26,112" fill="${c.under}"/><rect x="-24" y="80" width="48" height="44" rx="10" fill="${c.skinS}"/>`;
 g+=`<circle cx="-100" cy="8" r="14" fill="${c.skinS}"/><circle cx="100" cy="8" r="14" fill="${c.skinS}"/><circle r="100" fill="${c.skin}"/>`;
 g+=`<path d="M-102 -2 C-110 -88 -48 -112 0 -112 C52 -112 110 -88 102 -2 C84 -52 44 -64 0 -60 C-46 -64 -86 -52 -102 -2 Z" fill="${c.hair}"/>`;
 g+=olhosPontos(36,-6,o.blink,8);
 const br=e==='bravo'?[[-62,-34,-14,-20],[62,-34,14,-20]]:e==='surpreso'?[[-56,-44,-16,-48],[56,-44,16,-48]]:[[-60,-30,-14,-36],[60,-30,14,-36]];
 g+=`<path d="M${br[0][0]} ${br[0][1]} L${br[0][2]} ${br[0][3]}" stroke="#241410" stroke-width="9" stroke-linecap="round"/><path d="M${br[1][0]} ${br[1][1]} L${br[1][2]} ${br[1][3]}" stroke="#241410" stroke-width="9" stroke-linecap="round"/>`;
 if(o.dedo!=null) g+=`<path d="M112 170 L196 52" stroke="${c.shirt}" stroke-width="34" stroke-linecap="round"/><path d="M196 52 L214 20" stroke="${c.skin}" stroke-width="22" stroke-linecap="round"/>`;
 g+=boca(52,m,24,'#8B3A2E',e==='rindo'); return g},
bozo(o){const c=C.bozo,e=o.expr||'bravo',m=o.m||0;let g='';
 g+=`<path d="M-170 300 C-170 170 -90 124 -42 116 L42 116 C90 124 170 170 170 300 Z" fill="${c.shirt}"/><path d="M-42 116 L0 170 L42 116 Q0 128 -42 116 Z" fill="${c.shirtS}"/><rect x="-24" y="80" width="48" height="44" rx="10" fill="${c.skinS}"/>`;
 g+=`<ellipse cx="-102" cy="4" rx="14" ry="26" fill="${c.grey}"/><ellipse cx="102" cy="4" rx="14" ry="26" fill="${c.grey}"/><circle r="100" fill="${c.skin}"/>`;
 g+=`<path d="M-100 -12 C-110 -92 -40 -118 10 -112 C70 -110 110 -80 100 -12 C86 -56 50 -70 0 -68 C-48 -66 -84 -52 -100 -12 Z" fill="${c.hair}"/>`;
 const ey=-6; [-1,1].forEach(s=>{ if(o.blink) g+=`<path d="M${s*40-20} ${ey} L${s*40+20} ${ey}" stroke="#1B0E09" stroke-width="5"/>`; else g+=`<ellipse cx="${s*40}" cy="${ey}" rx="20" ry="${e==='surpreso'?17:12}" fill="#fff"/><circle cx="${s*40}" cy="${ey}" r="7" fill="#4F6F9A"/><circle cx="${s*40}" cy="${ey}" r="3.2" fill="#10151f"/>`});
 const k=e==='rindo'?0:1;
 g+= k?`<path d="M-72 -30 L-16 -16" stroke="#14100e" stroke-width="11" stroke-linecap="round"/><path d="M72 -30 L16 -16" stroke="#14100e" stroke-width="11" stroke-linecap="round"/>`:`<path d="M-72 -22 L-16 -30" stroke="#14100e" stroke-width="11" stroke-linecap="round"/><path d="M72 -22 L16 -30" stroke="#14100e" stroke-width="11" stroke-linecap="round"/>`;
 g+=`<path d="M-4 6 Q12 26 -2 34" fill="none" stroke="#B98457" stroke-width="5" stroke-linecap="round"/>`;
 g+=boca(56,m,24,MOUTH,e==='rindo'); return g},
gengivao(o){const c=C.ggv,e=o.expr||'neutro',m=o.m||0;let g='';
 g+=`<path d="M-170 300 C-170 170 -90 124 -42 116 L42 116 C90 124 170 170 170 300 Z" fill="${c.suit}"/><polygon points="-30,116 0,176 30,116" fill="${c.shirt}"/><polygon points="-6,140 6,140 3,200 -3,200" fill="#7B1E2B"/><rect x="-24" y="86" width="48" height="40" rx="10" fill="${c.skinS}"/>`;
 g+=`<ellipse cx="-98" cy="8" rx="12" ry="24" fill="${c.beard}"/><ellipse cx="98" cy="8" rx="12" ry="24" fill="${c.beard}"/><circle r="100" fill="${c.skin}"/><ellipse cx="-34" cy="-66" rx="26" ry="14" fill="#fff" opacity=".18"/>`;
 g+=`<path d="M-98 14 C-96 80 -48 128 0 130 C48 128 96 80 98 14 C80 50 50 62 0 62 C-50 62 -80 50 -98 14 Z" fill="${c.beard}"/>`;
 g+=`<path d="M-34 66 Q0 52 34 66 Q0 74 -34 66 Z" fill="#B3B3B3"/>`;
 g+=olhosPontos(34,-6,o.blink,6);
 g+=`<rect x="-66" y="-30" width="54" height="42" rx="12" fill="none" stroke="#0E0E10" stroke-width="9"/><rect x="12" y="-30" width="54" height="42" rx="12" fill="none" stroke="#0E0E10" stroke-width="9"/><path d="M-12 -14 L12 -14" stroke="#0E0E10" stroke-width="8"/>`;
 const up=e==='surpreso'?-10:0; g+=`<path d="M-68 ${-42+up} L-12 ${-40+up}" stroke="#3a3a3a" stroke-width="10" stroke-linecap="round"/><path d="M68 ${-42+up} L12 ${-40+up}" stroke="#3a3a3a" stroke-width="10" stroke-linecap="round"/>`;
 g+=e==='rindo'?`<path d="M-22 82 Q0 104 22 82 Z" fill="${MOUTH}"/>`:m<0.08?`<path d="M-16 84 L16 84" stroke="#6b3a35" stroke-width="7" stroke-linecap="round"/>`:`<ellipse cx="0" cy="${84+m*4}" rx="${14+m*6}" ry="${4+m*12}" fill="${MOUTH}"/>`; return g},
ovo(o){const c=C.ovo,e=o.expr||'bravo',m=o.m||0;let g='';
 g+=`<path d="M-200 340 C-200 190 -120 130 -62 122 L62 122 C120 130 200 190 200 340 Z" fill="${c.suit}"/><polygon points="-36,122 0,190 36,122" fill="${c.shirt}"/><polygon points="-10,140 10,140 14,250 0,262 -14,250" fill="${c.tie}"/>`;
 g+=`<ellipse cx="0" cy="-26" rx="108" ry="148" fill="${c.skin}"/><ellipse cx="-46" cy="-84" rx="20" ry="46" fill="#fff" opacity=".2"/>`;
 g+=olhosPontos(42,-28,o.blink,8);
 const up=e==='surpreso'?-14:0; g+=`<path d="M-84 ${-60+up} L-18 ${-44+up}" stroke="#14100e" stroke-width="11" stroke-linecap="round"/><path d="M84 ${-60+up} L18 ${-44+up}" stroke="#14100e" stroke-width="11" stroke-linecap="round"/>`;
 g+=e==='rindo'?`<path d="M-34 44 Q0 92 34 44 Z" fill="#5a1410"/>`:m<0.08?`<path d="M-30 52 Q0 38 30 52" fill="none" stroke="#5a1410" stroke-width="9" stroke-linecap="round"/>`:`<ellipse cx="0" cy="${46+m*6}" rx="${24+m*8}" ry="${8+m*26}" fill="#5a1410"/>`; if(o.martelo!=null) g+=`<g transform="translate(128 190) rotate(${-o.martelo})"><rect x="-10" y="-10" width="20" height="120" rx="8" fill="${c.woodD}"/><rect x="-48" y="-60" width="96" height="56" rx="10" fill="${c.wood}"/></g>`;
 return g},
nove(o){const c=C.nove,e=o.expr||'neutro',m=o.m||0;let g='<g transform="scale(.667)">';
 g+=`<path d="M-250 480 C-250 300 -150 250 -88 240 L88 240 C150 250 250 300 250 480 Z" fill="${c.shirt}"/><path d="M-44 240 L0 292 L44 240 Z" fill="#B53422"/>${star(-120,390,48,20,c.star)}<rect x="-40" y="120" width="80" height="62" rx="12" fill="${c.skinS}"/>`;
 [[-150,-40,52],[-165,10,46],[-140,60,42],[-110,-105,56],[-60,-150,58],[0,-165,60],[60,-150,58],[110,-105,56],[140,-40,52],[165,10,46],[140,60,42]].forEach(a=>g+=`<circle cx="${a[0]}" cy="${a[1]}" r="${a[2]}" fill="${c.hair}"/>`);
 [[-150,-90,-40],[-110,-150,-20],[-50,-185,-8],[20,-190,5],[85,-170,18],[135,-120,35],[165,-40,60],[-170,-30,-60]].forEach(a=>g+=`<path d="M-26 40 L0 -62 L26 40 Z" fill="${c.hair}" transform="translate(${a[0]},${a[1]}) rotate(${a[2]})"/>`);
 g+=`<circle r="150" fill="${c.skin}"/><path d="M-135 -60 C-120 -150 -40 -170 0 -165 C60 -170 125 -140 135 -60 C100 -110 60 -100 20 -118 C-20 -100 -80 -110 -135 -60 Z" fill="${c.hair}"/>`;
 g+=`<path d="M-148 20 C-150 120 -90 190 0 195 C90 190 150 120 148 20 C120 70 70 85 0 85 C-70 85 -120 70 -148 20 Z" fill="${c.hair}"/><path d="M-148 20 C-120 70 -70 85 0 85 C70 85 120 70 148 20 C150 40 150 60 140 80 C100 110 50 118 0 118 C-50 118 -100 110 -140 80 C-150 60 -150 40 -148 20 Z" fill="${c.hairS}" opacity=".55"/>`;
 g+=`<path d="M-70 70 Q-30 40 0 62 Q30 40 70 70 Q40 96 0 84 Q-40 96 -70 70 Z" fill="${c.hair}"/>`;
 [-1,1].forEach(s=>g+=`<ellipse cx="${s*152}" cy="10" rx="16" ry="26" fill="${c.skinS}"/>`);
 g+=`<ellipse cx="0" cy="28" rx="40" ry="36" fill="${c.nose}"/><ellipse cx="-12" cy="16" rx="12" ry="9" fill="#EDA894" opacity=".8"/>`;
 if(e==='rindo'||o.blink){[-1,1].forEach(s=>g+=`<path d="M${s*68-26} -22 Q${s*68} -50 ${s*68+26} -22" fill="none" stroke="#1B0E09" stroke-width="9" stroke-linecap="round"/>`)}
 else [-1,1].forEach(s=>{g+=`<ellipse cx="${s*68}" cy="-28" rx="30" ry="${e==='bravo'?34:28}" fill="#fff"/><circle cx="${s*68-s*4}" cy="-26" r="11" fill="#1B0E09"/>`});
 g+= e==='bravo'?`<path d="M-104 -78 L-34 -52" stroke="#fff" stroke-width="16" stroke-linecap="round"/><path d="M104 -78 L34 -52" stroke="#fff" stroke-width="16" stroke-linecap="round"/>`:`<path d="M-100 -74 L-38 -66" stroke="#fff" stroke-width="15" stroke-linecap="round"/><path d="M100 -74 L38 -66" stroke="#fff" stroke-width="15" stroke-linecap="round"/>`;
 g+= m<0.08?`<path d="M-34 112 Q0 120 34 112" fill="none" stroke="${c.mouth}" stroke-width="11" stroke-linecap="round"/>`:`<ellipse cx="0" cy="${110+m*6}" rx="${28+m*18}" ry="${10+m*34}" fill="${c.mouth}"/>`;
 return g+'</g>'}
};
G.busto=function(nome,o,x,y,s){o=o||{};return `<g transform="translate(${x||0},${y||0}) scale(${s||1})">${B[nome](o)}</g>`};
G.CORES=C;
})(typeof window!=='undefined'?window:globalThis);
