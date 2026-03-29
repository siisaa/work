// ---- 覚醒データ ----
// AWK[level] = [cost_to_reach, I%, III%, VI%]
// level 1 = starting state (0 books)
const AWK = [
  null,
  [0,15.0,45.0,45.0],
  [1,15.96,48.0,47.8],
  [2,16.92,51.0,50.6],
  [3,17.88,54.0,53.4],
  [5,18.84,57.0,56.2],
  [7,19.8,60.0,59.0],
  [9,20.76,63.0,61.8],
  [12,21.72,66.0,64.6],
  [16,22.68,69.0,67.4],
  [20,23.64,72.0,70.2],
  [20,24.68,75.25,73.2],
  [20,25.72,78.5,76.2],
  [20,26.76,81.75,79.2],
  [20,27.8,85.0,82.2],
  [20,28.84,88.25,85.2],
  [20,29.88,91.5,88.2],
  [20,30.92,94.75,91.2],
  [20,31.96,98.0,94.2],
  [20,33.0,101.25,97.2],
  [25,34.04,104.5,100.2],
  [25,35.24,108.25,103.7],
  [25,36.44,112.0,107.2],
  [25,37.64,115.75,110.7],
  [25,38.84,119.5,114.2],
  [25,40.04,123.25,117.7],
  [25,41.24,127.0,121.2],
  [25,42.44,130.75,124.7],
  [25,43.64,134.5,128.2],
  [25,44.84,138.25,131.7],
  [25,46.04,142.0,135.2],
  [30,47.4,146.25,139.2],
  [30,48.76,150.5,143.2],
  [30,50.12,154.75,147.2],
  [30,51.48,159.0,151.2],
  [30,52.84,163.25,155.2],
  [30,54.2,167.5,159.2],
  [30,55.56,171.75,163.2],
  [30,56.92,176.0,167.2],
  [30,58.28,180.25,171.2],
  [30,59.64,184.5,175.2],
  [35,61.16,189.25,179.7],
  [35,62.68,194.0,184.2],
  [35,64.2,198.75,188.7],
  [35,65.72,203.5,193.2],
  [35,67.24,208.25,197.7],
  [35,68.76,213.0,202.2],
  [35,70.28,217.75,206.7],
  [35,71.8,222.5,211.2],
  [35,73.32,227.25,215.7],
  [35,74.84,232.0,220.2],
  [40,76.52,237.25,225.2],
  [40,78.2,242.5,230.2],
  [40,79.88,247.75,235.2],
  [40,81.56,253.0,240.2],
  [40,83.24,258.25,245.2],
  [40,84.92,263.5,250.2],
  [40,86.6,268.75,255.2],
  [40,88.28,274.0,260.2],
  [40,89.96,279.25,265.2],
  [40,91.64,284.5,270.2],
  [45,93.48,290.25,275.7],
  [45,95.32,296.0,281.2],
  [45,97.16,301.75,286.7],
  [45,99.0,307.5,292.2],
  [45,100.84,313.25,297.7],
  [45,102.68,319.0,303.2],
  [45,104.52,324.75,308.7],
  [45,106.36,330.5,314.2],
  [45,108.2,336.25,319.7],
  [45,110.04,342.0,325.2],
  [50,112.04,348.25,331.2],
  [50,114.04,354.5,337.2],
  [50,116.04,360.75,343.2],
  [50,118.04,367.0,349.2],
  [50,120.04,373.25,355.2],
  [50,122.04,379.5,361.2],
  [50,124.04,385.75,367.2],
  [50,126.04,392.0,373.2],
  [50,128.04,398.25,379.2],
  [50,130.04,404.5,385.2],
  [55,132.2,411.25,391.7],
  [55,134.36,418.0,398.2],
  [55,136.52,424.75,404.7],
  [55,138.68,431.5,411.2],
  [55,140.84,438.25,417.7],
  [55,143.0,445.0,424.2],
  [55,145.16,451.75,430.7],
  [55,147.32,458.5,437.2],
  [55,149.48,465.25,443.7],
  [55,151.64,472.0,450.2],
  [60,153.88,479.0,457.2],
  [60,156.12,486.0,464.2],
  [60,158.36,493.0,471.2],
  [60,160.6,500.0,478.2],
  [60,162.84,507.0,485.2],
  [60,165.08,514.0,492.2],
  [60,167.32,521.0,499.2],
  [60,169.56,528.0,506.2],
  [60,171.8,535.0,513.2],
  [60,174.04,542.0,520.2],
  [65,176.44,549.5,527.7],
  [65,178.84,557.0,535.2],
  [65,181.24,564.5,542.7],
  [65,183.64,572.0,550.2],
  [65,186.04,579.5,557.7],
  [65,188.44,587.0,565.2],
  [65,190.84,594.5,572.7],
  [65,193.24,602.0,580.2],
  [65,195.64,609.5,587.7],
  [65,198.04,617.0,595.2],
  [70,200.6,625.0,603.2],
  [70,203.16,633.0,611.2],
  [70,205.72,641.0,619.2],
  [70,208.28,649.0,627.2],
  [70,210.84,657.0,635.2],
  [70,213.4,665.0,643.2],
  [70,215.96,673.0,651.2],
  [70,218.52,681.0,659.2],
  [70,221.08,689.0,667.2],
  [70,223.64,697.0,675.2],
  [75,226.36,705.5,683.7],
  [75,229.08,714.0,692.2],
  [75,231.8,722.5,700.7],
  [75,234.52,731.0,709.2],
  [75,237.24,739.5,717.7],
  [75,239.96,748.0,726.2],
  [75,242.68,756.5,734.7],
  [75,245.4,765.0,743.2],
  [75,248.12,773.5,751.7],
  [75,250.84,782.0,760.2],
  [80,253.72,791.0,769.2],
  [80,256.6,800.0,778.2],
  [80,259.48,809.0,787.2],
  [80,262.36,818.0,796.2],
  [80,265.24,827.0,805.2],
  [80,268.12,836.0,814.2],
  [80,271.0,845.0,823.2],
  [80,273.88,854.0,832.2],
  [80,276.76,863.0,841.2],
  [80,279.64,872.0,850.2],
  [85,282.68,881.5,859.7],
  [85,285.72,891.0,869.2],
  [85,288.76,900.5,878.7],
  [85,291.8,910.0,888.2],
  [85,294.84,919.5,897.7],
  [85,297.88,929.0,907.2],
  [85,300.92,938.5,916.7],
  [85,303.96,948.0,926.2],
  [85,307.0,957.5,935.7],
  [85,310.04,967.0,945.2],
  [90,313.24,977.0,955.2],
  [90,316.44,987.0,965.2],
  [90,319.64,997.0,975.2],
  [90,322.84,1007.0,985.2],
  [90,326.04,1017.0,995.2],
  [90,329.24,1027.0,1005.2],
  [90,332.44,1037.0,1015.2],
  [90,335.64,1047.0,1025.2],
  [90,338.84,1057.0,1035.2],
  [90,342.04,1067.0,1045.2],
  [95,345.4,1077.5,1055.7],
  [95,348.76,1088.0,1066.2],
  [95,352.12,1098.5,1076.7],
  [95,355.48,1109.0,1087.2],
  [95,358.84,1119.5,1097.7],
  [95,362.2,1130.0,1108.2],
  [95,365.56,1140.5,1118.7],
  [95,368.92,1151.0,1129.2],
  [95,372.28,1161.5,1139.7],
  [95,375.64,1172.0,1150.2],
  [100,379.16,1183.0,1161.2],
  [100,382.68,1194.0,1172.2],
  [100,386.2,1205.0,1183.2],
  [100,389.72,1216.0,1194.2],
  [100,393.24,1227.0,1205.2],
  [100,396.76,1238.0,1216.2],
  [100,400.28,1249.0,1227.2],
  [100,403.8,1260.0,1238.2],
  [100,407.32,1271.0,1249.2],
  [100,410.84,1282.0,1260.2],
  [105,414.52,1293.5,1271.7],
  [105,418.2,1305.0,1283.2],
  [105,421.88,1316.5,1294.7],
  [105,425.56,1328.0,1306.2],
  [105,429.24,1339.5,1317.7],
  [105,432.92,1351.0,1329.2],
  [105,436.6,1362.5,1340.7],
  [105,440.28,1374.0,1352.2],
  [105,443.96,1385.5,1363.7],
  [105,447.64,1397.0,1375.2],
  [110,451.48,1409.0,1387.2],
  [110,455.32,1421.0,1399.2],
  [110,459.16,1433.0,1411.2],
  [110,463.0,1445.0,1423.2],
  [110,466.84,1457.0,1435.2],
  [110,470.68,1469.0,1447.2],
  [110,474.52,1481.0,1459.2],
  [110,478.36,1493.0,1471.2],
  [110,482.2,1505.0,1483.2],
  [110,486.04,1517.0,1495.2],
];

// ---- ダメージ計算（index.htmlと同じロジック）----

function computeExpected(v) {
  if (v.atk === null || v.def === null || v.allyDamage === null) return null;

  const atkMinusDef = Math.max(0, v.atk - v.def);
  const inspireEff = v.inspire / 100;
  const resistEff  = v.resist  / 100;
  const P_INS = 0.3, P_RES = 0.3;

  const scenarios = [
    { p: (1 - P_INS) * (1 - P_RES), ins: false, res: false },
    { p:       P_INS * (1 - P_RES), ins: true,  res: false },
    { p: (1 - P_INS) *       P_RES, ins: false, res: true  },
    { p:       P_INS *       P_RES, ins: true,  res: true  },
  ];

  let effReduction = 0;
  for (const s of scenarios) {
    const adj = v.damageReduction
      - (s.ins ? inspireEff : 0)
      + (s.res ? resistEff  : 0);
    effReduction += s.p * Math.min(80, Math.max(0, adj));
  }

  const baseDamage = atkMinusDef * (v.allyDamage / 100) * (1 - effReduction / 100);

  const effectiveMultiRate = Math.min(1.0, Math.max(0, v.multiRate - v.multiIgnore) / 100);
  const multiMult = 1 + effectiveMultiRate;

  const effectiveCritRate = Math.max(0, v.critRate - v.critIgnore) / 100;
  const critResistVal = (v.critResist !== null && v.critResist > 0) ? v.critResist : 100;
  const critEff = Math.max(1.5, v.critDamage / critResistVal);
  const critMult = 1 + effectiveCritRate * (critEff - 1);

  const evadeCoeff = v.evadePattern === "B" ? 0.6 : 0.4;
  const finalEvadeIgnore = v.allyEvadeIgnore + v.evadeIgnore * evadeCoeff;
  const rawEvade = Math.max(0, v.evadeRate - finalEvadeIgnore);
  const effEvade = Math.min(80, Math.pow(rawEvade, 0.9));
  const hitRate = 1 - effEvade / 100;

  return baseDamage * multiMult * critMult * hitRate;
}

// ---- 覚醒状態からダメージ計算 ----

function computeDmgAtLevels(base, enemy, lvI, lvIII, lvVI) {
  const I_pct  = AWK[lvI][1];
  const III_pct = AWK[lvIII][2];
  const VI_pct  = AWK[lvVI][3];

  const v = {
    atk:             base.baseAtk * (1 + I_pct / 100),
    def:             enemy.def,
    allyDamage:      base.baseAllyDmg + III_pct,
    damageReduction: enemy.damageReduction,
    multiRate:       base.multiRate,
    multiIgnore:     enemy.multiIgnore,
    critRate:        base.critRate,
    critIgnore:      enemy.critIgnore,
    critDamage:      base.baseCritDmg + VI_pct,
    critResist:      enemy.critResist,
    inspire:         base.inspire,
    resist:          enemy.resist,
    evadeRate:       enemy.evadeRate,
    allyEvadeIgnore: base.allyEvadeIgnore,
    evadeIgnore:     base.evadeIgnore,
    evadePattern:    base.evadePattern,
  };
  return computeExpected(v) ?? 0;
}

// ---- 全振り ----

function allocateAllTo(cat, lvI, lvIII, lvVI, books) {
  let cI = lvI, cIII = lvIII, cVI = lvVI;
  let rem = books;
  while (rem > 0) {
    const cur = cat === "I" ? cI : cat === "III" ? cIII : cVI;
    if (cur >= 200) break;
    const cost = AWK[cur + 1][0];
    if (cost > rem) break;
    rem -= cost;
    if (cat === "I") cI++;
    else if (cat === "III") cIII++;
    else cVI++;
  }
  return { lvI: cI, lvIII: cIII, lvVI: cVI, booksUsed: books - rem };
}

// ---- 貪欲法（限界利益/コスト最大化）----

function greedyOptimize(base, enemy, lvI, lvIII, lvVI, books) {
  let cI = lvI, cIII = lvIII, cVI = lvVI;
  let rem = books;

  while (rem > 0) {
    const curDmg = computeDmgAtLevels(base, enemy, cI, cIII, cVI);
    let best = 0, bestCat = null;

    if (cI < 200 && AWK[cI + 1][0] <= rem) {
      const g = (computeDmgAtLevels(base, enemy, cI + 1, cIII, cVI) - curDmg) / AWK[cI + 1][0];
      if (g > best) { best = g; bestCat = "I"; }
    }
    if (cIII < 200 && AWK[cIII + 1][0] <= rem) {
      const g = (computeDmgAtLevels(base, enemy, cI, cIII + 1, cVI) - curDmg) / AWK[cIII + 1][0];
      if (g > best) { best = g; bestCat = "III"; }
    }
    if (cVI < 200 && AWK[cVI + 1][0] <= rem) {
      const g = (computeDmgAtLevels(base, enemy, cI, cIII, cVI + 1) - curDmg) / AWK[cVI + 1][0];
      if (g > best) { best = g; bestCat = "VI"; }
    }

    if (!bestCat) break;

    if (bestCat === "I") { rem -= AWK[cI + 1][0]; cI++; }
    else if (bestCat === "III") { rem -= AWK[cIII + 1][0]; cIII++; }
    else { rem -= AWK[cVI + 1][0]; cVI++; }
  }

  return { lvI: cI, lvIII: cIII, lvVI: cVI, booksUsed: books - rem };
}

// ---- 入力取得 ----

function gv(id) {
  const v = parseFloat(document.getElementById(id).value);
  return isNaN(v) ? null : v;
}

function getLvInput(id) {
  const v = parseInt(document.getElementById(id).value, 10);
  if (isNaN(v) || v < 1) return 1;
  if (v > 200) return 200;
  return v;
}

function getEvadePattern() {
  const el = document.querySelector('input[name="evadePattern2"]:checked');
  return el ? el.value : "A";
}

// ---- 計算・描画 ----

let chart = null;

function fmt(n) {
  if (!Number.isFinite(n) || n <= 0) return "-";
  return n.toLocaleString("ja-JP", { maximumFractionDigits: 0 });
}

function fmtPct(n) {
  return Number.isFinite(n) ? n.toFixed(1) + "%" : "-";
}

function runOptimize() {
  const errorEl = document.getElementById("optError");
  errorEl.textContent = "";

  // 現在ステータス（ゲーム内表示値）
  const curAtk     = gv("curAtk");
  const curAllyDmg = gv("curAllyDmg");
  const curCritDmg = gv("curCritDmg");
  if (curAtk === null || curAllyDmg === null || curCritDmg === null) {
    errorEl.textContent = "攻撃力・仲間ダメージ・会心ダメージを入力してください。";
    return;
  }

  const lvI   = getLvInput("lvI");
  const lvIII = getLvInput("lvIII");
  const lvVI  = getLvInput("lvVI");
  const books = gv("books") ?? 0;

  // 覚醒ボーナスを除いた素の値を算出
  const baseAtk    = curAtk / (1 + AWK[lvI][1] / 100);
  const baseAllyDmg = curAllyDmg - AWK[lvIII][2];
  const baseCritDmg = curCritDmg - AWK[lvVI][3];

  if (baseAllyDmg < 0 || baseCritDmg < 0) {
    errorEl.textContent = "入力値と覚醒レベルが整合しません。現在値または覚醒レベルを確認してください。";
    return;
  }

  const base = {
    baseAtk, baseAllyDmg, baseCritDmg,
    critRate:        gv("critRate2")       ?? 0,
    multiRate:       gv("multiRate2")      ?? 0,
    inspire:         gv("inspire2")        ?? 0,
    allyEvadeIgnore: gv("allyEvadeIgnore2") ?? 0,
    evadeIgnore:     gv("evadeIgnore2")    ?? 0,
    evadePattern:    getEvadePattern(),
  };

  const def = gv("def2") ?? 0;
  if (gv("def2") === null) { errorEl.textContent = "防御力を入力してください。"; return; }

  const enemy = {
    def,
    damageReduction: gv("damageReduction2") ?? 0,
    multiIgnore:     gv("multiIgnore2")     ?? 0,
    critIgnore:      gv("critIgnore2")      ?? 0,
    critResist:      gv("critResist2"),
    resist:          gv("resist2")          ?? 0,
    evadeRate:       gv("evadeRate2")       ?? 0,
  };

  // ---- 各シナリオのダメージ計算 ----
  const dmgCurrent = computeDmgAtLevels(base, enemy, lvI, lvIII, lvVI);

  const opt       = greedyOptimize(base, enemy, lvI, lvIII, lvVI, books);
  const dmgOpt    = computeDmgAtLevels(base, enemy, opt.lvI, opt.lvIII, opt.lvVI);

  const allI      = allocateAllTo("I",   lvI, lvIII, lvVI, books);
  const dmgAllI   = computeDmgAtLevels(base, enemy, allI.lvI, allI.lvIII, allI.lvVI);

  const allIII    = allocateAllTo("III", lvI, lvIII, lvVI, books);
  const dmgAllIII = computeDmgAtLevels(base, enemy, allIII.lvI, allIII.lvIII, allIII.lvVI);

  const allVI     = allocateAllTo("VI",  lvI, lvIII, lvVI, books);
  const dmgAllVI  = computeDmgAtLevels(base, enemy, allVI.lvI, allVI.lvIII, allVI.lvVI);

  // ---- 最適結果の表示 ----
  const addI   = opt.lvI   - lvI;
  const addIII = opt.lvIII - lvIII;
  const addVI  = opt.lvVI  - lvVI;
  const usedBooks = opt.booksUsed;

  document.getElementById("optResult").classList.add("has-result");

  document.getElementById("resCurrentDmg").textContent = fmt(dmgCurrent);
  document.getElementById("resOptDmg").textContent     = fmt(dmgOpt);
  document.getElementById("resIncrease").textContent   =
    dmgCurrent > 0 ? fmtPct((dmgOpt / dmgCurrent - 1) * 100) : "-";

  document.getElementById("resLvI").textContent   = `Lv${lvI} → Lv${opt.lvI}（+${addI}）`;
  document.getElementById("resLvIII").textContent = `Lv${lvIII} → Lv${opt.lvIII}（+${addIII}）`;
  document.getElementById("resLvVI").textContent  = `Lv${lvVI} → Lv${opt.lvVI}（+${addVI}）`;
  document.getElementById("resBooks").textContent = `${usedBooks} / ${books} 枚`;

  // ---- グラフ描画 ----
  const labels = [
    "現在",
    `最適配分\n(Ⅰ+${addI}/Ⅲ+${addIII}/Ⅵ+${addVI})`,
    `Ⅰ全振り\n(Lv${allI.lvI})`,
    `Ⅲ全振り\n(Lv${allIII.lvIII})`,
    `Ⅵ全振り\n(Lv${allVI.lvVI})`,
  ];
  const values = [dmgCurrent, dmgOpt, dmgAllI, dmgAllIII, dmgAllVI];
  const maxVal = Math.max(...values);

  const colors = values.map((v, i) =>
    i === 0 ? "rgba(107,114,128,0.8)" :
    v === maxVal ? "rgba(34,197,94,0.85)" :
    "rgba(56,189,248,0.7)"
  );
  const borderColors = colors.map(c => c.replace("0.8","1").replace("0.85","1").replace("0.7","1"));

  const ctx = document.getElementById("optChart").getContext("2d");
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "期待ダメージ",
        data: values,
        backgroundColor: colors,
        borderColor: borderColors,
        borderWidth: 1,
        borderRadius: 4,
      }],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => fmt(ctx.parsed.x),
          },
        },
      },
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            color: "#9ca3af",
            callback: v => v.toLocaleString("ja-JP"),
          },
          grid: { color: "rgba(148,163,184,0.1)" },
        },
        y: {
          ticks: { color: "#d1d5db", font: { size: 11 } },
          grid: { display: false },
        },
      },
    },
  });
}

function handleChange() {
  const curAtk     = gv("curAtk");
  const curAllyDmg = gv("curAllyDmg");
  const curCritDmg = gv("curCritDmg");
  const def2       = gv("def2");
  if (curAtk !== null && curAllyDmg !== null && curCritDmg !== null && def2 !== null) {
    runOptimize();
  }
}

function handleReset() {
  document.querySelectorAll("input[type='number']").forEach(el => { el.value = ""; });
  document.getElementById("lvI").value   = "1";
  document.getElementById("lvIII").value = "1";
  document.getElementById("lvVI").value  = "1";
  document.getElementById("optError").textContent = "";
  document.getElementById("optResult").classList.remove("has-result");
  if (chart) { chart.destroy(); chart = null; }
}

function init() {
  document.querySelectorAll("input[type='number'], input[type='range']").forEach(el => {
    el.addEventListener("input", handleChange);
  });
  document.querySelectorAll('input[name="evadePattern2"]').forEach(el => {
    el.addEventListener("change", handleChange);
  });
  document.getElementById("resetBtn").addEventListener("click", handleReset);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
