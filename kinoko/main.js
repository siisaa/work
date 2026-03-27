function toNumber(value) {
  if (value === "" || value === null || value === undefined) return NaN;
  return Number(value);
}

function formatNumber(value) {
  if (!Number.isFinite(value)) return "-";
  return value.toFixed(2);
}

function getInputValues() {
  const allyAtk = toNumber(document.getElementById("allyAtk").value);
  const allyDamage = toNumber(document.getElementById("allyDamage").value);
  const allyMultiRate = toNumber(
    document.getElementById("allyMultiRate").value
  );
  const allyCritRate = toNumber(document.getElementById("allyCritRate").value);
  const enemyDef = toNumber(document.getElementById("enemyDef").value);
  const allyDamageReduction = toNumber(
    document.getElementById("allyDamageReduction").value
  );
  const multiIgnore = toNumber(
    document.getElementById("multiIgnore").value
  );
  const critIgnore = toNumber(document.getElementById("critIgnore").value);
  const multiCoeff = toNumber(
    document.getElementById("multiCoeff").value
  );
  const critCoeff = toNumber(document.getElementById("critCoeff").value);
  const critDamage = toNumber(
    document.getElementById("critDamage").value
  );
  const critResist = toNumber(
    document.getElementById("critResist").value
  );

  return {
    allyAtk,
    allyDamage,
    allyMultiRate,
    allyCritRate,
    enemyDef,
    allyDamageReduction,
    multiIgnore,
    critIgnore,
    multiCoeff,
    critCoeff,
    critDamage,
    critResist,
  };
}

function validateInputs(values) {
  const requiredFields = [
    "allyAtk",
    "allyDamage",
    "enemyDef",
    "allyDamageReduction",
    "allyMultiRate",
    "allyCritRate",
    "multiIgnore",
    "critIgnore",
    "multiCoeff",
    "critCoeff",
    "critDamage",
    "critResist",
  ];

  for (const key of requiredFields) {
    if (!Number.isFinite(values[key])) {
      return `入力が不足しているか数値として解釈できません: ${key}`;
    }
    if (values[key] < 0) {
      return `0未満の値は想定していません: ${key}`;
    }
  }

  return null;
}

function computeDamage(values) {
  const atkMinusDef = Math.max(0, values.allyAtk - values.enemyDef);

  // %入力の値を 0〜1 に変換
  const allyDamageRatio = values.allyDamage / 100;
  const allyDamageReductionRatio = values.allyDamageReduction / 100;
  const allyMultiRateRatio = values.allyMultiRate / 100;
  const allyCritRateRatio = values.allyCritRate / 100;
  const multiIgnoreRatio = values.multiIgnore / 100;
  const critIgnoreRatio = values.critIgnore / 100;
  const critResistRatio = values.critResist / 100;

  const damageFactor = Math.max(
    0,
    allyDamageRatio - allyDamageReductionRatio
  );

  let critBaseFactor;
  if (critResistRatio <= 0) {
    // 分母が0以下の場合は割り算を避け、会心ダメージそのものを係数として扱う
    critBaseFactor = Math.max(0, values.critDamage);
  } else {
    critBaseFactor = Math.max(0, values.critDamage / critResistRatio);
  }

  const baseDamage = atkMinusDef * damageFactor * critBaseFactor;

  let pMulti = allyMultiRateRatio - multiIgnoreRatio;
  let pCrit = allyCritRateRatio - critIgnoreRatio;

  // 0未満は0に切り上げるが、上限は設けず 100% 超もそのまま使用する
  pMulti = Math.max(0, pMulti);
  pCrit = Math.max(0, pCrit);

  const expectedMultiplier =
    (1 + pMulti * values.multiCoeff) * (1 + pCrit * values.critCoeff);

  const expectedDamage = baseDamage * expectedMultiplier;

  return {
    baseDamage,
    expectedDamage,
    pMulti,
    pCrit,
  };
}

function formatPercent(value) {
  if (!Number.isFinite(value)) return "-";
  return (value * 100).toFixed(2) + "%";
}

function updateResults(result, errorMessage) {
  const errorEl = document.getElementById("resultError");
  const baseDamageEl = document.getElementById("baseDamageOutput");
  const expectedDamageEl = document.getElementById("expectedDamageOutput");
  const pMultiEl = document.getElementById("pMultiOutput");
  const pCritEl = document.getElementById("pCritOutput");

  if (errorMessage) {
    errorEl.textContent = errorMessage;
    baseDamageEl.textContent = "-";
    expectedDamageEl.textContent = "-";
    pMultiEl.textContent = "-";
    pCritEl.textContent = "-";
    return;
  }

  errorEl.textContent = "";
  baseDamageEl.textContent = formatNumber(result.baseDamage);
  expectedDamageEl.textContent = formatNumber(result.expectedDamage);
  pMultiEl.textContent = formatPercent(result.pMulti);
  pCritEl.textContent = formatPercent(result.pCrit);
}

function handleCalculate() {
  const values = getInputValues();
  const error = validateInputs(values);
  if (error) {
    updateResults(null, error);
    return;
  }

  const result = computeDamage(values);
  updateResults(result, null);
}

function handleReset() {
  const inputs = document.querySelectorAll("input[type='number']");
  inputs.forEach((input) => {
    input.value = "";
  });

  updateResults(
    {
      baseDamage: NaN,
      expectedDamage: NaN,
      pMulti: NaN,
      pCrit: NaN,
    },
    ""
  );
}

function init() {
  const calcButton = document.getElementById("calcButton");
  const resetButton = document.getElementById("resetButton");

  if (calcButton) {
    calcButton.addEventListener("click", handleCalculate);
  }
  if (resetButton) {
    resetButton.addEventListener("click", handleReset);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function toNumber(value) {
  if (value === "" || value === null || value === undefined) return NaN;
  return Number(value);
}

function formatNumber(value) {
  if (!Number.isFinite(value)) return "-";
  return value.toFixed(2);
}

function getInputValues() {
  const allyAtk = toNumber(document.getElementById("allyAtk").value);
  const allyDamage = toNumber(document.getElementById("allyDamage").value);
  const allyMultiRate = toNumber(
    document.getElementById("allyMultiRate").value
  );
  const allyCritRate = toNumber(document.getElementById("allyCritRate").value);
  const enemyDef = toNumber(document.getElementById("enemyDef").value);
  const allyDamageReduction = toNumber(
    document.getElementById("allyDamageReduction").value
  );
  const multiIgnore = toNumber(
    document.getElementById("multiIgnore").value
  );
  const critIgnore = toNumber(document.getElementById("critIgnore").value);
  const multiCoeff = toNumber(
    document.getElementById("multiCoeff").value
  );
  const critCoeff = toNumber(document.getElementById("critCoeff").value);
  const critDamage = toNumber(
    document.getElementById("critDamage").value
  );
  const critResist = toNumber(
    document.getElementById("critResist").value
  );

  return {
    allyAtk,
    allyDamage,
    allyMultiRate,
    allyCritRate,
    enemyDef,
    allyDamageReduction,
    multiIgnore,
    critIgnore,
    multiCoeff,
    critCoeff,
    critDamage,
    critResist,
  };
}

function validateInputs(values) {
  const requiredFields = [
    "allyAtk",
    "allyDamage",
    "enemyDef",
    "allyDamageReduction",
    "allyMultiRate",
    "allyCritRate",
    "multiIgnore",
    "critIgnore",
    "multiCoeff",
    "critCoeff",
    "critDamage",
    "critResist",
  ];

  for (const key of requiredFields) {
    if (!Number.isFinite(values[key])) {
      return `入力が不足しているか数値として解釈できません: ${key}`;
    }
    if (values[key] < 0) {
      return `0未満の値は想定していません: ${key}`;
    }
  }

  return null;
}

function computeDamage(values) {
  const atkMinusDef = Math.max(0, values.allyAtk - values.enemyDef);
  const damageFactor = Math.max(
    0,
    values.allyDamage - values.allyDamageReduction
  );
  const critBaseFactor = Math.max(
    0,
    values.critDamage - values.critResist
  );

  const baseDamage = atkMinusDef * damageFactor * critBaseFactor;

  let pMulti = values.allyMultiRate - values.multiIgnore;
  let pCrit = values.allyCritRate - values.critIgnore;

  // 0未満は0に切り上げるが、上限は設けず 100% 超もそのまま使用する
  pMulti = Math.max(0, pMulti);
  pCrit = Math.max(0, pCrit);

  const expectedMultiplier =
    (1 + pMulti * values.multiCoeff) * (1 + pCrit * values.critCoeff);

  const expectedDamage = baseDamage * expectedMultiplier;

  return {
    baseDamage,
    expectedDamage,
    pMulti,
    pCrit,
  };
}

function updateResults(result, errorMessage) {
  const errorEl = document.getElementById("resultError");
  const baseDamageEl = document.getElementById("baseDamageOutput");
  const expectedDamageEl = document.getElementById("expectedDamageOutput");
  const pMultiEl = document.getElementById("pMultiOutput");
  const pCritEl = document.getElementById("pCritOutput");

  if (errorMessage) {
    errorEl.textContent = errorMessage;
    baseDamageEl.textContent = "-";
    expectedDamageEl.textContent = "-";
    pMultiEl.textContent = "-";
    pCritEl.textContent = "-";
    return;
  }

  errorEl.textContent = "";
  baseDamageEl.textContent = formatNumber(result.baseDamage);
  expectedDamageEl.textContent = formatNumber(result.expectedDamage);
  pMultiEl.textContent = formatNumber(result.pMulti);
  pCritEl.textContent = formatNumber(result.pCrit);
}

function handleCalculate() {
  const values = getInputValues();
  const error = validateInputs(values);
  if (error) {
    updateResults(null, error);
    return;
  }

  const result = computeDamage(values);
  updateResults(result, null);
}

function handleReset() {
  const inputs = document.querySelectorAll("input[type='number']");
  inputs.forEach((input) => {
    input.value = "";
  });

  updateResults(
    {
      baseDamage: NaN,
      expectedDamage: NaN,
      pMulti: NaN,
      pCrit: NaN,
    },
    ""
  );
}

function init() {
  const calcButton = document.getElementById("calcButton");
  const resetButton = document.getElementById("resetButton");

  if (calcButton) {
    calcButton.addEventListener("click", handleCalculate);
  }
  if (resetButton) {
    resetButton.addEventListener("click", handleReset);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function toNumber(value) {
  if (value === "" || value === null || value === undefined) return NaN;
  return Number(value);
}

function formatNumber(value) {
  if (!Number.isFinite(value)) return "-";
  return value.toFixed(2);
}

function getInputValues() {
  const allyAtk = toNumber(document.getElementById("allyAtk").value);
  const allyDamage = toNumber(document.getElementById("allyDamage").value);
  const allyMultiRate = toNumber(
    document.getElementById("allyMultiRate").value
  );
  const allyCritRate = toNumber(document.getElementById("allyCritRate").value);
  const enemyDef = toNumber(document.getElementById("enemyDef").value);
  const allyDamageReduction = toNumber(
    document.getElementById("allyDamageReduction").value
  );
  const multiIgnore = toNumber(
    document.getElementById("multiIgnore").value
  );
  const critIgnore = toNumber(document.getElementById("critIgnore").value);
  const multiCoeff = toNumber(
    document.getElementById("multiCoeff").value
  );
  const critCoeff = toNumber(document.getElementById("critCoeff").value);
  const critDamage = toNumber(
    document.getElementById("critDamage").value
  );
  const critResist = toNumber(
    document.getElementById("critResist").value
  );

  return {
    allyAtk,
    allyDamage,
    allyMultiRate,
    allyCritRate,
    enemyDef,
    allyDamageReduction,
    multiIgnore,
    critIgnore,
    multiCoeff,
    critCoeff,
    critDamage,
    critResist,
  };
}

function validateInputs(values) {
  const requiredFields = [
    "allyAtk",
    "allyDamage",
    "enemyDef",
    "allyDamageReduction",
    "allyMultiRate",
    "allyCritRate",
    "multiIgnore",
    "critIgnore",
    "multiCoeff",
    "critCoeff",
    "critDamage",
    "critResist",
  ];

  for (const key of requiredFields) {
    if (!Number.isFinite(values[key])) {
      return `入力が不足しているか数値として解釈できません: ${key}`;
    }
    if (values[key] < 0) {
      return `0未満の値は想定していません: ${key}`;
    }
  }

  return null;
}

function computeDamage(values) {
  const atkMinusDef = Math.max(0, values.allyAtk - values.enemyDef);
  const damageFactor = Math.max(
    0,
    values.allyDamage - values.allyDamageReduction
  );
  const critBaseFactor = Math.max(
    0,
    values.critDamage - values.critResist
  );

  const baseDamage = atkMinusDef * damageFactor * critBaseFactor;

  let pMulti = values.allyMultiRate - values.multiIgnore;
  let pCrit = values.allyCritRate - values.critIgnore;

  pMulti = clamp(pMulti, 0, 1);
  pCrit = clamp(pCrit, 0, 1);

  const expectedMultiplier =
    (1 + pMulti * values.multiCoeff) * (1 + pCrit * values.critCoeff);

  const expectedDamage = baseDamage * expectedMultiplier;

  return {
    baseDamage,
    expectedDamage,
    pMulti,
    pCrit,
  };
}

function updateResults(result, errorMessage) {
  const errorEl = document.getElementById("resultError");
  const baseDamageEl = document.getElementById("baseDamageOutput");
  const expectedDamageEl = document.getElementById("expectedDamageOutput");
  const pMultiEl = document.getElementById("pMultiOutput");
  const pCritEl = document.getElementById("pCritOutput");

  if (errorMessage) {
    errorEl.textContent = errorMessage;
    baseDamageEl.textContent = "-";
    expectedDamageEl.textContent = "-";
    pMultiEl.textContent = "-";
    pCritEl.textContent = "-";
    return;
  }

  errorEl.textContent = "";
  baseDamageEl.textContent = formatNumber(result.baseDamage);
  expectedDamageEl.textContent = formatNumber(result.expectedDamage);
  pMultiEl.textContent = formatNumber(result.pMulti);
  pCritEl.textContent = formatNumber(result.pCrit);
}

function handleCalculate() {
  const values = getInputValues();
  const error = validateInputs(values);
  if (error) {
    updateResults(null, error);
    return;
  }

  const result = computeDamage(values);
  updateResults(result, null);
}

function handleReset() {
  const inputs = document.querySelectorAll("input[type='number']");
  inputs.forEach((input) => {
    input.value = "";
  });

  updateResults(
    {
      baseDamage: NaN,
      expectedDamage: NaN,
      pMulti: NaN,
      pCrit: NaN,
    },
    ""
  );
}

function init() {
  const calcButton = document.getElementById("calcButton");
  const resetButton = document.getElementById("resetButton");

  if (calcButton) {
    calcButton.addEventListener("click", handleCalculate);
  }
  if (resetButton) {
    resetButton.addEventListener("click", handleReset);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}

