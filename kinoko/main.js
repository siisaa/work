// ---- 入力取得 ----

function getVal(id) {
  const v = parseFloat(document.getElementById(id).value);
  return isNaN(v) ? null : v;
}

function getInputs() {
  return {
    atk:             getVal("atk"),
    def:             getVal("def"),
    allyDamage:      getVal("allyDamage"),
    damageReduction: getVal("damageReduction") ?? 0,
    multiRate:       getVal("multiRate")       ?? 0,
    multiIgnore:     getVal("multiIgnore")     ?? 0,
    critRate:        getVal("critRate")        ?? 0,
    critIgnore:      getVal("critIgnore")      ?? 0,
    critDamage:      getVal("critDamage")      ?? 0,
    critResist:      getVal("critResist"),      // null = 未入力 → 100 扱い
    inspire:         getVal("inspire")         ?? 0,
    resist:          getVal("resist")          ?? 0,
  };
}

// ---- 計算 ----

function computeDamage(v) {
  // 攻撃力・防御力・仲間ダメは必須
  if (v.atk === null || v.def === null || v.allyDamage === null) return null;

  const atkMinusDef = Math.max(0, v.atk - v.def);

  // --- 期待有効ダメ軽減（鼓舞・抵抗の4パターン加重平均）---
  const inspireEff = v.inspire / 100; // 数値/100 = %
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

  // --- 基本ダメージ ---
  const baseDamage = atkMinusDef
    * (v.allyDamage / 100)
    * (1 - effReduction / 100);

  // --- 連撃乗数（有効連撃率は100%上限）---
  const effectiveMultiRate = Math.min(1.0, Math.max(0, v.multiRate - v.multiIgnore) / 100);
  const multiMult = 1 + effectiveMultiRate; // 連撃は+100%、最大2.0x

  // --- 会心乗数 ---
  const effectiveCritRate = Math.max(0, v.critRate - v.critIgnore) / 100;
  const critResistVal = (v.critResist !== null && v.critResist > 0) ? v.critResist : 100;
  const critEff = Math.max(1.5, v.critDamage / critResistVal);
  const critMult = 1 + effectiveCritRate * (critEff - 1);

  // --- 期待ダメージ ---
  const expectedDamage = baseDamage * multiMult * critMult;

  return { baseDamage, expectedDamage, effReduction, multiMult, critMult };
}

// ---- 表示 ----

function fmt(n, digits = 0) {
  if (!Number.isFinite(n)) return "-";
  return n.toLocaleString("ja-JP", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function fmtMult(n) {
  if (!Number.isFinite(n)) return "-";
  return n.toFixed(3) + "x";
}

function fmtPct(n) {
  if (!Number.isFinite(n)) return "-";
  return n.toFixed(1) + "%";
}

function render(result) {
  const errorEl  = document.getElementById("resultError");
  const expEl    = document.getElementById("expectedDamage");
  const baseEl   = document.getElementById("baseDamage");
  const redEl    = document.getElementById("effReduction");
  const multiEl  = document.getElementById("multiMult");
  const critEl   = document.getElementById("critMult");
  const cardEl   = document.getElementById("resultCard");

  if (!result) {
    errorEl.textContent = "攻撃力・防御力・仲間ダメージを入力してください。";
    expEl.textContent  = "-";
    baseEl.textContent = "-";
    redEl.textContent  = "-";
    multiEl.textContent = "-";
    critEl.textContent  = "-";
    cardEl.classList.remove("has-result");
    return;
  }

  errorEl.textContent = "";
  expEl.textContent   = fmt(result.expectedDamage);
  baseEl.textContent  = fmt(result.baseDamage);
  redEl.textContent   = fmtPct(result.effReduction);
  multiEl.textContent = fmtMult(result.multiMult);
  critEl.textContent  = fmtMult(result.critMult);
  cardEl.classList.add("has-result");
}

// ---- イベント ----

function handleInput() {
  const values = getInputs();
  const result = computeDamage(values);
  render(result);
}

function handleReset() {
  document.querySelectorAll("input[type='number']").forEach(el => {
    el.value = "";
  });
  render(null);
  document.getElementById("resultError").textContent = "";
  document.getElementById("resultCard").classList.remove("has-result");
}

function init() {
  document.querySelectorAll("input[type='number']").forEach(el => {
    el.addEventListener("input", handleInput);
  });
  document.getElementById("resetButton").addEventListener("click", handleReset);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
