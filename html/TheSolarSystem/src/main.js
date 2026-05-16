const canvas = document.getElementById("sky");
    const ctx = canvas.getContext("2d");
    const sceneBuffer = document.createElement("canvas");
    const sceneCtx = sceneBuffer.getContext("2d");
    const controls = document.getElementById("controls");
    const consoleToggle = document.getElementById("consoleToggle");
    const timeSpeedControl = document.getElementById("timeSpeedControl");
    const pauseControl = document.getElementById("pauseControl");
    const scaleModeControl = document.getElementById("scaleModeControl");
    const targetSelect = document.getElementById("targetSelect");
    const measureControl = document.getElementById("measureControl");
    const clearMeasureControl = document.getElementById("clearMeasureControl");
    const screenshotControl = document.getElementById("screenshotControl");
    const showTrailsControl = document.getElementById("showTrailsControl");
    const showOrbitsControl = document.getElementById("showOrbitsControl");
    const showLabelsControl = document.getElementById("showLabelsControl");
    const showAsteroidsControl = document.getElementById("showAsteroidsControl");
    const showCometsControl = document.getElementById("showCometsControl");
    const showMeteorsControl = document.getElementById("showMeteorsControl");
    const showStarsControl = document.getElementById("showStarsControl");
    const showTeachingControl = document.getElementById("showTeachingControl");
    const showSolarActivityControl = document.getElementById("showSolarActivityControl");
    const solarActivityIntensityControl = document.getElementById("solarActivityIntensityControl");
    const triggerSolarBurstControl = document.getElementById("triggerSolarBurstControl");
    const sizeControl = document.getElementById("sizeControl");
    const speedControl = document.getElementById("speedControl");
    const performanceModeControl = document.getElementById("performanceModeControl");
    const magnifierControl = document.getElementById("magnifierControl");
    const magnifierZoomControl = document.getElementById("magnifierZoomControl");
    const magnifierRadiusControl = document.getElementById("magnifierRadiusControl");
    const infoPanel = document.getElementById("infoPanel");
    const infoTitle = document.getElementById("infoTitle");
    const infoGrid = document.getElementById("infoGrid");
    const infoClose = document.getElementById("infoClose");
    const infoFocusControl = document.getElementById("infoFocusControl");
    const infoMeasureControl = document.getElementById("infoMeasureControl");
    const measureBanner = document.getElementById("measureBanner");
    const timeSpeedValue = document.getElementById("timeSpeedValue");
    const pageOpenedValue = document.getElementById("pageOpenedValue");
    const simulationDateValue = document.getElementById("simulationDateValue");
    const simulationElapsedValue = document.getElementById("simulationElapsedValue");
    const timeScaleValue = document.getElementById("timeScaleValue");
    const solarActivityIntensityValue = document.getElementById("solarActivityIntensityValue");
    const sizeValue = document.getElementById("sizeValue");
    const speedValue = document.getElementById("speedValue");
    const magnifierZoomValue = document.getElementById("magnifierZoomValue");
    const magnifierRadiusValue = document.getElementById("magnifierRadiusValue");
    const tailShapeValue = document.getElementById("tailShapeValue");
    const tailShapeSummary = document.getElementById("tailShapeSummary");
    const bodyShapeValue = document.getElementById("bodyShapeValue");
    const bodyShapeSummary = document.getElementById("bodyShapeSummary");
    const tailShapeInputs = [...document.querySelectorAll("input[name='meteorTailShape']")];
    const bodyShapeInputs = [...document.querySelectorAll("input[name='meteorBodyShape']")];
    const stars = [];
    const meteors = [];
    const solarTargets = [];
    const planetTrails = new Map();
    const asteroids = [];
    const solarActivityEvents = [];
    const solarWindParticles = [];
    const satelliteTrails = new Map();
    const measurement = {
      points: []
    };

    let width = 0;
    let height = 0;
    let pixelRatio = 1;
    let simulationTime = 0;
    let lastClockUpdate = 0;
    let selectedInfoTarget = null;
    let teachingTargetName = "";
    const pointer = {
      x: 0,
      y: 0,
      active: false
    };
    const settings = {
      size: Number(sizeControl.value),
      speed: Number(speedControl.value),
      timeSpeed: Number(timeSpeedControl.value),
      paused: false,
      scaleMode: scaleModeControl.value,
      focusTarget: "",
      measureMode: false,
      showTrails: showTrailsControl.checked,
      showOrbits: showOrbitsControl.checked,
      showLabels: showLabelsControl.checked,
      showAsteroids: showAsteroidsControl.checked,
      showComets: showCometsControl.checked,
      showMeteors: showMeteorsControl.checked,
      showStars: showStarsControl.checked,
      showTeaching: showTeachingControl.checked,
      showSolarActivity: showSolarActivityControl.checked,
      solarActivityIntensity: Number(solarActivityIntensityControl.value),
      performanceMode: performanceModeControl.value,
      magnifierEnabled: magnifierControl.checked,
      magnifierZoom: Number(magnifierZoomControl.value),
      magnifierRadius: Number(magnifierRadiusControl.value),
      tailShapes: [],
      bodyShapes: []
    };
    const tailShapeNames = {
      trail: "经典拖尾",
      comet: "粗亮彗尾",
      double: "双尾流光",
      flare: "爆闪短尾",
      blade: "光刃切线"
    };
    const bodyShapeNames = {
      oval: "椭圆光核",
      comet: "彗星光团",
      double: "双光点",
      star: "星芒核心",
      blade: "菱形光刃"
    };

    const random = (min, max) => Math.random() * (max - min) + min;
    const pageOpenedAt = new Date();
    const SIMULATED_DAYS_PER_SECOND = 8;
    const AU_IN_KM = 149597870.7;
    const MOON_ORBIT_AU = 384400 / AU_IN_KM;
    const meteorLimits = {
      low: 14,
      medium: 24,
      high: 34
    };
    const performanceProfiles = {
      low: { stars: 7600, asteroids: 15000, solarParticles: 0.55 },
      medium: { stars: 4200, asteroids: 9000, solarParticles: 1 },
      high: { stars: 2600, asteroids: 5600, solarParticles: 1.65 }
    };
    const planets = [
      { name: "水星", color: "#b8aa98", au: 0.387, orbitYears: 0.2408, rotationHours: 1407.6, radius: 3.1, start: 0.7, diameter: "4,879 km", mass: "3.30 × 10^23 kg", gravity: "3.70 m/s²", orbitSpeed: "47.4 km/s", day: "58.6 个地球日", year: "88 个地球日", note: "太阳系中最小且离太阳最近的行星。" },
      { name: "金星", color: "#e1b66f", au: 0.723, orbitYears: 0.6152, rotationHours: -5832.5, radius: 4.5, start: 2.2, diameter: "12,104 km", mass: "4.87 × 10^24 kg", gravity: "8.87 m/s²", orbitSpeed: "35.0 km/s", day: "243 个地球日，逆向自转", year: "225 个地球日", note: "厚重大气带来强烈温室效应。" },
      { name: "地球", color: "#4f9cff", au: 1, orbitYears: 1, rotationHours: 23.9, radius: 4.8, start: 3.7, diameter: "12,742 km", mass: "5.97 × 10^24 kg", gravity: "9.81 m/s²", orbitSpeed: "29.8 km/s", day: "23.9 小时", year: "365.25 天", note: "拥有液态水海洋和一颗天然卫星月亮。" },
      { name: "火星", color: "#d06b45", au: 1.524, orbitYears: 1.8808, rotationHours: 24.6, radius: 3.8, start: 5.1, diameter: "6,779 km", mass: "6.42 × 10^23 kg", gravity: "3.71 m/s²", orbitSpeed: "24.1 km/s", day: "24.6 小时", year: "687 个地球日", note: "表面富含氧化铁，呈红色外观。" },
      { name: "木星", color: "#d2aa77", au: 5.203, orbitYears: 11.862, rotationHours: 9.9, radius: 8.6, start: 1.4, diameter: "139,820 km", mass: "1.90 × 10^27 kg", gravity: "24.79 m/s²", orbitSpeed: "13.1 km/s", day: "9.9 小时", year: "11.86 个地球年", note: "太阳系最大行星，拥有明显云带和大红斑。" },
      { name: "土星", color: "#dcc58f", au: 9.537, orbitYears: 29.457, rotationHours: 10.7, radius: 7.6, start: 4.4, ring: true, diameter: "116,460 km", mass: "5.68 × 10^26 kg", gravity: "10.44 m/s²", orbitSpeed: "9.7 km/s", day: "10.7 小时", year: "29.46 个地球年", note: "以宽阔明亮的行星环著称。" },
      { name: "天王星", color: "#8de2e6", au: 19.191, orbitYears: 84.011, rotationHours: -17.2, radius: 6.2, start: 0.1, ring: true, diameter: "50,724 km", mass: "8.68 × 10^25 kg", gravity: "8.69 m/s²", orbitSpeed: "6.8 km/s", day: "17.2 小时，逆向自转", year: "84 个地球年", note: "自转轴高度倾斜，几乎像躺着公转。" },
      { name: "海王星", color: "#4d73e7", au: 30.07, orbitYears: 164.8, rotationHours: 16.1, radius: 6.1, start: 2.9, diameter: "49,244 km", mass: "1.02 × 10^26 kg", gravity: "11.15 m/s²", orbitSpeed: "5.4 km/s", day: "16.1 小时", year: "164.8 个地球年", note: "太阳系最外侧的已知大行星，风速极高。" }
    ];
    const sunInfo = {
      name: "太阳",
      type: "恒星",
      diameter: "约 1,392,700 km",
      mass: "1.989 × 10^30 kg",
      gravity: "约 274 m/s²",
      orbitSpeed: "太阳系中心天体",
      day: "赤道约 25 天自转一周",
      year: "太阳系行星围绕它公转",
      note: "通过核聚变释放能量，是太阳系主要光和热来源。"
    };
    const moonInfo = {
      name: "月亮",
      type: "地球天然卫星",
      diameter: "3,474.8 km",
      mass: "7.35 × 10^22 kg",
      gravity: "1.62 m/s²",
      orbitSpeed: "约 1.02 km/s",
      day: "自转与公转同步，约 27.3 天",
      year: "绕地球约 27.3 天一圈",
      note: "月球引力是地球潮汐的重要来源。"
    };
    const satelliteInfos = {
      木卫一: { name: "木卫一", type: "木星卫星", diameter: "3,643 km", mass: "8.93 × 10^22 kg", gravity: "1.80 m/s²", orbitSpeed: "约 17.3 km/s", day: "与公转同步，约 1.77 天", year: "绕木星约 1.77 天", note: "太阳系火山活动最强烈的天体之一。" },
      木卫二: { name: "木卫二", type: "木星卫星", diameter: "3,122 km", mass: "4.80 × 10^22 kg", gravity: "1.31 m/s²", orbitSpeed: "约 13.7 km/s", day: "与公转同步，约 3.55 天", year: "绕木星约 3.55 天", note: "冰壳下可能存在全球性地下海洋。" },
      木卫三: { name: "木卫三", type: "木星卫星", diameter: "5,268 km", mass: "1.48 × 10^23 kg", gravity: "1.43 m/s²", orbitSpeed: "约 10.9 km/s", day: "与公转同步，约 7.15 天", year: "绕木星约 7.15 天", note: "太阳系中最大的卫星，甚至大于水星。" },
      木卫四: { name: "木卫四", type: "木星卫星", diameter: "4,821 km", mass: "1.08 × 10^23 kg", gravity: "1.24 m/s²", orbitSpeed: "约 8.2 km/s", day: "与公转同步，约 16.69 天", year: "绕木星约 16.69 天", note: "表面布满古老撞击坑。" },
      泰坦: { name: "泰坦", type: "土星卫星", diameter: "5,149 km", mass: "1.35 × 10^23 kg", gravity: "1.35 m/s²", orbitSpeed: "约 5.6 km/s", day: "与公转同步，约 15.95 天", year: "绕土星约 15.95 天", note: "拥有浓厚氮气大气和甲烷湖泊。" }
    };
    const cometInfo = {
      name: "哈雷彗星",
      type: "周期彗星",
      diameter: "彗核约 11 km",
      mass: "约 2.2 × 10^14 kg",
      gravity: "极弱",
      orbitSpeed: "随近日点/远日点变化",
      day: "自转约 2.2 天",
      year: "约 75-76 个地球年",
      note: "著名短周期彗星，靠近太阳时会形成明亮彗发和彗尾。"
    };
    const asteroidBeltInfo = {
      name: "小行星带",
      type: "小天体区域",
      diameter: "位于火星与木星轨道之间",
      mass: "总质量远小于月球",
      gravity: "由众多小天体各自贡献",
      orbitSpeed: "约 17-20 km/s 量级",
      day: "各小行星自转周期不同",
      year: "约 3-6 个地球年",
      note: "包含谷神星、灶神星等小天体，是太阳系重要碎片带。"
    };
    const knowledge = {
      太阳: { moons: "无卫星", atmosphere: "主要由氢、氦等离子体组成", missions: "SOHO、帕克太阳探测器、Solar Orbiter", fact: "太阳约占太阳系总质量的 99.8%。" },
      水星: { moons: "无卫星", atmosphere: "极稀薄外逸层", missions: "水手10号、信使号、贝皮科伦坡", fact: "昼夜温差极大。" },
      金星: { moons: "无卫星", atmosphere: "以二氧化碳为主，硫酸云层", missions: "金星号、麦哲伦号、Akatsuki", fact: "金星的一天比一年还长。" },
      地球: { moons: "1 颗：月亮", atmosphere: "氮气、氧气为主", missions: "大量地球观测卫星", fact: "目前已知唯一有稳定液态水海洋和生命的行星。" },
      月亮: { moons: "无卫星", atmosphere: "极稀薄外逸层", missions: "阿波罗、嫦娥、LRO", fact: "月亮始终以近似同一面朝向地球。" },
      火星: { moons: "2 颗：火卫一、火卫二", atmosphere: "稀薄二氧化碳大气", missions: "海盗号、好奇号、毅力号、天问一号", fact: "拥有太阳系最高火山奥林匹斯山。" },
      木卫一: { moons: "无卫星", atmosphere: "极稀薄二氧化硫外逸层", missions: "伽利略号、朱诺号近距离观测", fact: "潮汐加热驱动持续火山活动。" },
      木卫二: { moons: "无卫星", atmosphere: "极稀薄氧气外逸层", missions: "欧罗巴快船、JUICE", fact: "是寻找地下海洋和潜在生命的重要目标。" },
      木卫三: { moons: "无卫星", atmosphere: "极稀薄氧气外逸层", missions: "伽利略号、JUICE", fact: "太阳系唯一已知拥有自身磁场的卫星。" },
      木卫四: { moons: "无卫星", atmosphere: "极稀薄二氧化碳外逸层", missions: "伽利略号、JUICE", fact: "地质活动弱，保留了大量古老撞击记录。" },
      木星: { moons: "已知卫星超过 90 颗", atmosphere: "氢、氦为主", missions: "伽利略号、朱诺号、欧罗巴快船", fact: "大红斑是持续数百年的巨型风暴。" },
      土星: { moons: "已知卫星超过 140 颗", atmosphere: "氢、氦为主", missions: "先锋11号、旅行者、卡西尼", fact: "土星环主要由冰粒和岩屑组成。" },
      泰坦: { moons: "无卫星", atmosphere: "浓厚氮气大气，含甲烷", missions: "卡西尼-惠更斯、未来蜻蜓任务", fact: "除地球外，少数表面存在稳定液体的天体之一。" },
      天王星: { moons: "已知卫星 27 颗", atmosphere: "氢、氦、甲烷", missions: "旅行者2号", fact: "自转轴倾角约 98 度。" },
      海王星: { moons: "已知卫星 14 颗", atmosphere: "氢、氦、甲烷", missions: "旅行者2号", fact: "拥有太阳系行星中最强劲的风之一。" },
      哈雷彗星: { moons: "无卫星", atmosphere: "靠近太阳时形成彗发", missions: "乔托号、织女星探测器", fact: "下一次回归近日点预计在 2061 年。" },
      小行星带: { moons: "部分小行星有小卫星", atmosphere: "通常无大气", missions: "黎明号、隼鸟、OSIRIS-REx", fact: "小行星带并不像电影中那样拥挤。" }
    };
    const comet = {
      name: "哈雷彗星",
      color: "#b7fff2",
      semiMajorAU: 17.8,
      eccentricityReal: 0.967,
      orbitYears: 75.3,
      start: 0.45,
      eccentricity: 0.72,
      info: cometInfo
    };
    const satelliteSystems = {
      木星: [
        { name: "木卫一", color: "#e0c37b", periodDays: 1.769, distanceKm: 421700, visualOrbit: 1.85, visualRadius: 0.16, start: 0.2 },
        { name: "木卫二", color: "#d8d6c6", periodDays: 3.551, distanceKm: 671100, visualOrbit: 2.35, visualRadius: 0.14, start: 1.4 },
        { name: "木卫三", color: "#a99c8e", periodDays: 7.155, distanceKm: 1070400, visualOrbit: 2.95, visualRadius: 0.18, start: 2.6 },
        { name: "木卫四", color: "#8f8275", periodDays: 16.689, distanceKm: 1882700, visualOrbit: 3.6, visualRadius: 0.16, start: 4.1 }
      ],
      土星: [
        { name: "泰坦", color: "#d7a65c", periodDays: 15.945, distanceKm: 1221870, visualOrbit: 2.85, visualRadius: 0.18, start: 0.9 }
      ]
    };

    function updateSetting(control, output, key) {
      settings[key] = Number(control.value);
      output.value = `${settings[key].toFixed(key === "speed" ? 2 : 1)}x`;
    }

    function updateTimeSetting() {
      settings.timeSpeed = Number(timeSpeedControl.value);
      timeSpeedValue.value = `${settings.timeSpeed.toFixed(1)}x`;
      timeScaleValue.textContent = `1秒 = ${(SIMULATED_DAYS_PER_SECOND * settings.timeSpeed).toFixed(1)}天`;
    }

    function formatDateTime(date) {
      return new Intl.DateTimeFormat("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false
      }).format(date);
    }

    function formatDurationDays(totalDays) {
      if (totalDays < 1) {
        const hours = Math.floor(totalDays * 24);
        const minutes = Math.floor(totalDays * 1440) % 60;
        return hours > 0 ? `${hours}小时${minutes}分钟` : `${Math.max(0, minutes)}分钟`;
      }

      const years = Math.floor(totalDays / 365.25);
      const afterYears = totalDays - years * 365.25;
      const months = Math.floor(afterYears / 30.4375);
      const days = Math.floor(afterYears - months * 30.4375);
      const parts = [];

      if (years) parts.push(`${years}年`);
      if (months) parts.push(`${months}个月`);
      if (days || parts.length === 0) parts.push(`${days}天`);
      return parts.join("");
    }

    function getSimulatedEarthDays() {
      return simulationTime * SIMULATED_DAYS_PER_SECOND;
    }

    function updateSimulationClock(force = false) {
      const now = performance.now();
      if (!force && now - lastClockUpdate < 250) {
        return;
      }

      lastClockUpdate = now;
      const elapsedDays = getSimulatedEarthDays();
      const simulationDate = new Date(pageOpenedAt.getTime() + elapsedDays * 86400000);

      simulationDateValue.textContent = formatDateTime(simulationDate);
      simulationElapsedValue.textContent = formatDurationDays(elapsedDays);
      timeScaleValue.textContent = `1秒 = ${(SIMULATED_DAYS_PER_SECOND * settings.timeSpeed).toFixed(1)}天`;
    }

    function updateDisplaySettings() {
      settings.scaleMode = scaleModeControl.value;
      settings.measureMode = measureControl.checked;
      settings.showTrails = showTrailsControl.checked;
      settings.showOrbits = showOrbitsControl.checked;
      settings.showLabels = showLabelsControl.checked;
      settings.showAsteroids = showAsteroidsControl.checked;
      settings.showComets = showCometsControl.checked;
      settings.showMeteors = showMeteorsControl.checked;
      settings.showStars = showStarsControl.checked;
      settings.showTeaching = showTeachingControl.checked;
      settings.showSolarActivity = showSolarActivityControl.checked;
      settings.performanceMode = performanceModeControl.value;
      measureBanner.hidden = !settings.measureMode || measurement.points.length >= 2;
    }

    function updateSolarActivitySetting() {
      settings.solarActivityIntensity = Number(solarActivityIntensityControl.value);
      solarActivityIntensityValue.value = `${settings.solarActivityIntensity.toFixed(1)}x`;
    }

    function updateMagnifierSetting() {
      settings.magnifierEnabled = magnifierControl.checked;
      settings.magnifierZoom = Number(magnifierZoomControl.value);
      settings.magnifierRadius = Number(magnifierRadiusControl.value);
      magnifierZoomValue.value = `${settings.magnifierZoom.toFixed(1)}x`;
      magnifierRadiusValue.value = `${Math.round(settings.magnifierRadius)}px`;
    }

    function saveScreenshot() {
      const link = document.createElement("a");
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      link.download = `solar-system-${timestamp}.png`;
      link.href = canvas.toDataURL("image/png");
      link.click();
    }

    function updateShapeSetting(inputs, output, summary, names, settingKey, allText, changedInput) {
      let selected = inputs.filter((input) => input.checked).map((input) => input.value);

      if (selected.length === 0) {
        const fallback = changedInput || inputs[0];
        fallback.checked = true;
        selected = [fallback.value];
      }

      settings[settingKey] = selected;
      output.value = `${selected.length}种`;
      summary.textContent = selected.length === inputs.length
        ? allText
        : selected.map((shape) => names[shape]).join("、");
    }

    function showInfo(target) {
      const data = target.data;
      const extra = knowledge[data.name] || {};
      const rows = [
        ["类型", data.type || "行星"],
        ["大小（直径）", data.diameter],
        ["重量/质量", data.mass],
        ["表面重力", data.gravity],
        ["公转速度", data.orbitSpeed],
        ["自转周期", data.day],
        ["公转周期", data.year],
        ["模拟速度", `${settings.timeSpeed.toFixed(1)}x，当前为${settings.scaleMode === "relative" ? "相对真实模式" : "视觉模式"}`],
        ["卫星", extra.moons],
        ["大气/组成", extra.atmosphere],
        ["探索任务", extra.missions],
        ["有趣事实", extra.fact],
        ["补充", data.note]
      ];

      selectedInfoTarget = data.name;
      infoTitle.textContent = data.name;
      infoGrid.innerHTML = rows
        .filter(([, value]) => Boolean(value))
        .map(([label, value]) => `<dt>${label}</dt><dd>${value}</dd>`)
        .join("");
      infoPanel.hidden = false;
    }

    function setFocusTarget(name) {
      settings.focusTarget = name || "";
      targetSelect.value = settings.focusTarget;
      magnifierControl.checked = Boolean(settings.focusTarget);
      updateMagnifierSetting();
    }

    function locateTarget(name, shouldFocus = false) {
      const target = solarTargets.find((item) => item.data.name === name);

      if (!target) {
        return;
      }

      pointer.x = target.x;
      pointer.y = target.y;
      pointer.active = true;
      showInfo(target);

      if (shouldFocus) {
        setFocusTarget(name);
      }
    }

    function clearMeasurement() {
      measurement.points = [];
      measureBanner.textContent = "测距工具已开启：依次点击两个天体";
      measureBanner.hidden = !settings.measureMode;
    }

    function getCurrentTarget(name) {
      return solarTargets.find((target) => target.data.name === name);
    }

    function getMeasurementTargets() {
      return measurement.points
        .map((point) => getCurrentTarget(point.data.name))
        .filter(Boolean);
    }

    function formatKm(km) {
      if (km >= 100000000) {
        return `${(km / 100000000).toFixed(2)} 亿公里`;
      }

      if (km >= 10000) {
        return `${(km / 10000).toFixed(2)} 万公里`;
      }

      return `${Math.round(km).toLocaleString("zh-CN")} 公里`;
    }

    function formatAU(au) {
      return au >= 0.01 ? `${au.toFixed(3)} AU` : `${au.toFixed(5)} AU`;
    }

    function getRealDistance(a, b) {
      if (![a.realX, a.realY, b.realX, b.realY].every(Number.isFinite)) {
        return null;
      }

      const dx = a.realX - b.realX;
      const dy = a.realY - b.realY;
      const dz = (a.realZ || 0) - (b.realZ || 0);
      const au = Math.hypot(dx, dy, dz);

      return {
        au,
        km: au * AU_IN_KM
      };
    }

    function updateMeasurementBanner() {
      const current = getMeasurementTargets();

      if (current.length === 2) {
        const [a, b] = current;
        const distance = getRealDistance(a, b);
        const screenDistance = Math.hypot(a.x - b.x, a.y - b.y).toFixed(1);

        if (distance) {
          measureBanner.textContent = `${a.data.name} ↔ ${b.data.name}：约 ${formatAU(distance.au)} / ${formatKm(distance.km)}（画面 ${screenDistance}px）`;
        } else {
          measureBanner.textContent = `${a.data.name} ↔ ${b.data.name}：当前目标缺少真实比例坐标（画面 ${screenDistance}px）`;
        }

        measureBanner.hidden = false;
      } else if (current.length === 1) {
        measureBanner.textContent = `已选择 ${current[0].data.name}，再点击第二个天体`;
        measureBanner.hidden = false;
      } else {
        measureBanner.textContent = "测距工具已开启：依次点击两个天体";
        measureBanner.hidden = !settings.measureMode;
      }
    }

    function addMeasurementTarget(target) {
      if (measurement.points.length >= 2) {
        measurement.points = [];
      }

      if (!measurement.points.some((item) => item.data.name === target.data.name)) {
        measurement.points.push(target);
      }

      updateMeasurementBanner();
    }

    function findSolarTarget(x, y) {
      for (let i = solarTargets.length - 1; i >= 0; i -= 1) {
        const target = solarTargets[i];
        const distance = Math.hypot(x - target.x, y - target.y);

        if (distance <= target.hitRadius) {
          return target;
        }
      }

      return null;
    }

    function resize() {
      pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.floor(width * pixelRatio);
      canvas.height = Math.floor(height * pixelRatio);
      sceneBuffer.width = canvas.width;
      sceneBuffer.height = canvas.height;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
      createStars();
      createAsteroids();
    }

    function createStars() {
      stars.length = 0;
      const profile = performanceProfiles[settings.performanceMode] || performanceProfiles.medium;
      const count = Math.floor((width * height) / profile.stars);

      for (let i = 0; i < count; i += 1) {
        stars.push({
          x: Math.random() * width,
          y: Math.random() * height,
          radius: random(0.35, 1.65),
          alpha: random(0.28, 0.95),
          twinkle: random(0.006, 0.024),
          phase: random(0, Math.PI * 2),
          tint: Math.random() > 0.78 ? "190, 215, 255" : "255, 255, 255"
        });
      }
    }

    function createAsteroids() {
      asteroids.length = 0;
      const profile = performanceProfiles[settings.performanceMode] || performanceProfiles.medium;
      const count = Math.max(45, Math.floor((width * height) / profile.asteroids));

      for (let i = 0; i < count; i += 1) {
        asteroids.push({
          phase: random(0, Math.PI * 2),
          drift: random(-0.18, 0.18),
          orbit: random(0.38, 0.5),
          size: random(0.45, 1.25),
          speed: random(0.45, 0.9),
          alpha: random(0.22, 0.72)
        });
      }
    }

    function recordTrail(name, x, y, limit = 140) {
      if (!planetTrails.has(name)) {
        planetTrails.set(name, []);
      }

      const trail = planetTrails.get(name);
      const last = trail[trail.length - 1];

      if (!last || Math.hypot(last.x - x, last.y - y) > 0.8) {
        trail.push({ x, y });
      }

      while (trail.length > limit) {
        trail.shift();
      }
    }

    function colorWithAlpha(hex, alpha) {
      const clean = hex.replace("#", "");
      const r = parseInt(clean.slice(0, 2), 16);
      const g = parseInt(clean.slice(2, 4), 16);
      const b = parseInt(clean.slice(4, 6), 16);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    function drawTrail(name, color) {
      const trail = planetTrails.get(name);

      if (!settings.showTrails || !trail || trail.length < 2) {
        return;
      }

      ctx.save();
      ctx.lineWidth = 1.6;

      for (let i = 1; i < trail.length; i += 1) {
        const alpha = i / trail.length;
        ctx.strokeStyle = colorWithAlpha(color, 0.28 * alpha);
        ctx.beginPath();
        ctx.moveTo(trail[i - 1].x, trail[i - 1].y);
        ctx.lineTo(trail[i].x, trail[i].y);
        ctx.stroke();
      }

      ctx.restore();
    }

    function drawRadialGlow(x, y, radius, color, strength, spread) {
      const glow = ctx.createRadialGradient(x, y, radius * 0.2, x, y, radius * spread);
      glow.addColorStop(0, colorWithAlpha(color, strength));
      glow.addColorStop(0.45, colorWithAlpha(color, strength * 0.32));
      glow.addColorStop(1, colorWithAlpha(color, 0));

      ctx.save();
      ctx.globalCompositeOperation = "lighter";
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(x, y, radius * spread, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    function spawnSolarActivity(kind = "flare") {
      const strength = settings.solarActivityIntensity;
      const event = {
        kind,
        angle: random(0, Math.PI * 2),
        age: 0,
        life: kind === "cme" ? random(3.2, 5.4) : random(1.2, 2.4),
        strength: random(0.75, 1.25) * strength,
        twist: random(-0.55, 0.55)
      };

      solarActivityEvents.push(event);

      if (kind !== "prominence") {
        const profile = performanceProfiles[settings.performanceMode] || performanceProfiles.medium;
        const particleCount = Math.floor(random(14, 26) * strength * profile.solarParticles);
        for (let i = 0; i < particleCount; i += 1) {
          solarWindParticles.push({
            angle: event.angle + random(-0.22, 0.22),
            age: 0,
            life: random(1.4, 3.1),
            speed: random(34, 72) * strength,
            offset: random(-0.12, 0.12),
            size: random(0.8, 1.8),
            alpha: random(0.38, 0.78)
          });
        }
      }
    }

    function updateSolarActivity(delta) {
      if (!settings.showSolarActivity || settings.paused) {
        return;
      }

      const chance = 0.22 * settings.solarActivityIntensity * delta;
      if (Math.random() < chance) {
        const roll = Math.random();
        spawnSolarActivity(roll > 0.72 ? "cme" : roll > 0.36 ? "prominence" : "flare");
      }
    }

    function drawSolarActivity(centerX, centerY, sunRadius, delta) {
      if (!settings.showSolarActivity) {
        return;
      }

      updateSolarActivity(delta);
      ctx.save();
      ctx.globalCompositeOperation = "lighter";

      for (let i = solarActivityEvents.length - 1; i >= 0; i -= 1) {
        const event = solarActivityEvents[i];
        event.age += settings.paused ? 0 : delta;
        const progress = Math.min(event.age / event.life, 1);
        const fade = Math.sin(progress * Math.PI);
        const baseX = centerX + Math.cos(event.angle) * sunRadius * 0.92;
        const baseY = centerY + Math.sin(event.angle) * sunRadius * 0.92;

        if (event.kind === "prominence") {
          const height = sunRadius * (0.55 + event.strength * 0.2);
          const controlAngle = event.angle + event.twist;
          const endAngle = event.angle + event.twist * 0.82;
          const endX = centerX + Math.cos(endAngle) * (sunRadius * 1.04);
          const endY = centerY + Math.sin(endAngle) * (sunRadius * 1.04);
          const ctrlX = centerX + Math.cos(controlAngle) * (sunRadius + height);
          const ctrlY = centerY + Math.sin(controlAngle) * (sunRadius + height);

          ctx.strokeStyle = `rgba(255, 106, 34, ${0.52 * fade})`;
          ctx.lineWidth = Math.max(1.2, sunRadius * 0.055 * event.strength);
          ctx.beginPath();
          ctx.moveTo(baseX, baseY);
          ctx.quadraticCurveTo(ctrlX, ctrlY, endX, endY);
          ctx.stroke();

          ctx.strokeStyle = `rgba(255, 214, 116, ${0.36 * fade})`;
          ctx.lineWidth = Math.max(0.8, sunRadius * 0.022 * event.strength);
          ctx.beginPath();
          ctx.moveTo(baseX, baseY);
          ctx.quadraticCurveTo(ctrlX, ctrlY, endX, endY);
          ctx.stroke();
        } else if (event.kind === "cme") {
          const front = sunRadius * (1.15 + progress * (2.9 + event.strength * 0.45));
          const width = 0.38 + event.strength * 0.12;
          const gradient = ctx.createRadialGradient(centerX, centerY, sunRadius, centerX, centerY, front);
          gradient.addColorStop(0, `rgba(255, 218, 126, ${0.14 * fade})`);
          gradient.addColorStop(0.66, `rgba(255, 112, 48, ${0.08 * fade})`);
          gradient.addColorStop(1, "rgba(255, 112, 48, 0)");
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.moveTo(centerX, centerY);
          ctx.arc(centerX, centerY, front, event.angle - width, event.angle + width);
          ctx.closePath();
          ctx.fill();

          ctx.strokeStyle = `rgba(255, 224, 168, ${0.24 * fade})`;
          ctx.lineWidth = Math.max(1, sunRadius * 0.018);
          ctx.beginPath();
          ctx.arc(centerX, centerY, front, event.angle - width, event.angle + width);
          ctx.stroke();
        } else {
          const length = sunRadius * (0.8 + event.strength * 0.38);
          const flareEndX = centerX + Math.cos(event.angle) * (sunRadius + length * progress);
          const flareEndY = centerY + Math.sin(event.angle) * (sunRadius + length * progress);
          const gradient = ctx.createLinearGradient(baseX, baseY, flareEndX, flareEndY);
          gradient.addColorStop(0, `rgba(255, 255, 214, ${0.72 * fade})`);
          gradient.addColorStop(0.48, `rgba(255, 156, 56, ${0.34 * fade})`);
          gradient.addColorStop(1, "rgba(255, 80, 28, 0)");
          ctx.strokeStyle = gradient;
          ctx.lineWidth = Math.max(1.6, sunRadius * 0.07 * event.strength * fade);
          ctx.lineCap = "round";
          ctx.beginPath();
          ctx.moveTo(baseX, baseY);
          ctx.lineTo(flareEndX, flareEndY);
          ctx.stroke();
        }

        if (event.age >= event.life) {
          solarActivityEvents.splice(i, 1);
        }
      }

      for (let i = solarWindParticles.length - 1; i >= 0; i -= 1) {
        const particle = solarWindParticles[i];
        particle.age += settings.paused ? 0 : delta;
        const progress = Math.min(particle.age / particle.life, 1);
        const distance = sunRadius * 1.05 + particle.speed * particle.age;
        const angle = particle.angle + particle.offset * progress;
        const x = centerX + Math.cos(angle) * distance;
        const y = centerY + Math.sin(angle) * distance;
        const alpha = particle.alpha * (1 - progress);

        ctx.fillStyle = `rgba(255, 199, 112, ${alpha})`;
        ctx.beginPath();
        ctx.arc(x, y, particle.size, 0, Math.PI * 2);
        ctx.fill();

        if (particle.age >= particle.life) {
          solarWindParticles.splice(i, 1);
        }
      }

      ctx.restore();
    }

    function drawAtmosphere(x, y, radius, color, sunAngle, strength = 0.18) {
      ctx.save();
      ctx.globalCompositeOperation = "screen";
      ctx.strokeStyle = colorWithAlpha(color, strength);
      ctx.lineWidth = Math.max(0.8, radius * 0.16);
      ctx.beginPath();
      ctx.arc(x, y, radius * 1.05, 0, Math.PI * 2);
      ctx.stroke();

      ctx.strokeStyle = colorWithAlpha(color, strength * 1.9);
      ctx.lineWidth = Math.max(0.9, radius * 0.2);
      ctx.beginPath();
      ctx.arc(x, y, radius * 1.02, sunAngle - 1.2, sunAngle + 1.2);
      ctx.stroke();
      ctx.restore();
    }

    function createMeteor(x, y) {
      const palette = [
        { hue: random(26, 46), edge: random(188, 215), name: "warm" },
        { hue: random(190, 220), edge: random(34, 50), name: "blue" },
        { hue: random(275, 320), edge: random(185, 205), name: "violet" },
        { hue: random(88, 132), edge: random(28, 42), name: "green" }
      ];
      const colorSet = palette[Math.floor(random(0, palette.length))];
      const hue = Math.floor(colorSet.hue);
      const angle = random(0, Math.PI * 2);
      const size = random(0.82, 1.95) * settings.size;
      const speed = random(420, 760) * settings.speed;
      const tail = Math.min(760, random(190, 380) * Math.sqrt(size));
      const tailShape = settings.tailShapes[Math.floor(Math.random() * settings.tailShapes.length)] || "trail";
      const bodyShape = settings.bodyShapes[Math.floor(Math.random() * settings.bodyShapes.length)] || "oval";
      const fragmentScale = settings.performanceMode === "high" ? 1 : settings.performanceMode === "medium" ? 0.68 : 0.38;
      const fragmentCount = Math.floor(random(4, 10) * Math.min(1.35, size) * fragmentScale);
      const fragments = Array.from({ length: fragmentCount }, () => ({
        along: random(0.08, 0.88),
        side: random(-1, 1),
        drift: random(-22, 22),
        size: random(0.45, 1.9) * Math.sqrt(size),
        hueShift: random(-14, 18),
        phase: random(0, Math.PI * 2),
        lifeBias: random(0.25, 1)
      }));

      const meteor = {
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        age: 0,
        life: random(0.95, 1.65),
        size,
        tail,
        tailShape,
        bodyShape,
        hue,
        edgeHue: Math.floor(colorSet.edge),
        colorTone: colorSet.name,
        flicker: random(8, 16),
        phase: random(0, Math.PI * 2),
        bend: random(-0.18, 0.18),
        fragments,
        color: `hsl(${hue} 95% 68%)`,
        glow: `hsla(${hue}, 100%, 72%, 0.55)`
      };

      meteor.sprite = createMeteorSprite(meteor);
      meteors.push(meteor);

      const limit = meteorLimits[settings.performanceMode] || meteorLimits.medium;
      while (meteors.length > limit) {
        meteors.shift();
      }
    }

    function createMeteorSprite(meteor) {
      const spriteScale = settings.performanceMode === "high" ? 1.25 : settings.performanceMode === "medium" ? 1 : 0.78;
      const length = Math.max(120, meteor.tail) * spriteScale;
      const headRadius = meteor.size * (meteor.bodyShape === "comet" ? 10 : meteor.bodyShape === "blade" ? 7.2 : 8.2) * spriteScale;
      const widthBoost = meteor.tailShape === "comet" ? 3.8 : meteor.tailShape === "double" ? 2.5 : meteor.tailShape === "flare" ? 3.2 : 2.1;
      const padding = Math.ceil(Math.max(34, headRadius * 2.8));
      const canvasWidth = Math.ceil(length + padding * 2 + headRadius * 4);
      const canvasHeight = Math.ceil(Math.max(54, headRadius * widthBoost + padding));
      const offscreen = document.createElement("canvas");
      offscreen.width = canvasWidth;
      offscreen.height = canvasHeight;

      const mctx = offscreen.getContext("2d");
      const headX = canvasWidth - padding - headRadius * 1.35;
      const headY = canvasHeight / 2;
      const tailStartX = headX - length;
      const drawCurve = (offset, curve, lineWidth, hue, alpha, lightness = 72, blur = 0) => {
        const gradient = mctx.createLinearGradient(tailStartX, headY + offset, headX, headY);
        gradient.addColorStop(0, `hsla(${hue}, 100%, ${lightness - 12}%, 0)`);
        gradient.addColorStop(0.35, `hsla(${hue}, 100%, ${lightness - 4}%, ${0.08 * alpha})`);
        gradient.addColorStop(0.78, `hsla(${hue}, 100%, ${lightness}%, ${0.42 * alpha})`);
        gradient.addColorStop(0.94, `rgba(255, 245, 220, ${0.74 * alpha})`);
        gradient.addColorStop(1, `rgba(255, 255, 255, ${0.96 * alpha})`);

        mctx.save();
        mctx.strokeStyle = gradient;
        mctx.lineWidth = Math.max(0.7, lineWidth);
        mctx.lineCap = "round";
        mctx.lineJoin = "round";
        mctx.shadowColor = `hsla(${hue}, 100%, 70%, ${0.38 * alpha})`;
        mctx.shadowBlur = blur;
        mctx.beginPath();
        mctx.moveTo(tailStartX, headY + offset);
        mctx.quadraticCurveTo(headX - length * 0.48, headY + offset * 0.45 + curve, headX, headY);
        mctx.stroke();
        mctx.restore();
      };

      mctx.globalCompositeOperation = "lighter";

      const dustWidth = meteor.size * spriteScale * (meteor.tailShape === "comet" ? 26 : meteor.tailShape === "blade" ? 9 : 16);
      const dustGradient = mctx.createLinearGradient(tailStartX, headY, headX, headY);
      dustGradient.addColorStop(0, `hsla(${meteor.hue}, 92%, 54%, 0)`);
      dustGradient.addColorStop(0.52, `hsla(${meteor.hue}, 96%, 62%, 0.08)`);
      dustGradient.addColorStop(1, `hsla(${meteor.hue}, 100%, 76%, 0.28)`);
      mctx.fillStyle = dustGradient;
      mctx.beginPath();
      mctx.moveTo(headX, headY - dustWidth);
      mctx.quadraticCurveTo(headX - length * 0.48, headY - dustWidth * 0.36 + meteor.bend * length * 0.1, tailStartX, headY);
      mctx.quadraticCurveTo(headX - length * 0.48, headY + dustWidth * 0.34 + meteor.bend * length * 0.1, headX, headY + dustWidth);
      mctx.closePath();
      mctx.fill();

      const baseWidth = meteor.size * spriteScale * (meteor.tailShape === "blade" ? 2.2 : meteor.tailShape === "comet" ? 6.2 : 4.2);
      drawCurve(0, meteor.bend * length * 0.06, baseWidth * 2.2, meteor.hue, 0.42, 64, 14 * spriteScale);
      drawCurve(0, meteor.bend * length * 0.04, baseWidth, meteor.edgeHue, 0.72, 72, 7 * spriteScale);
      drawCurve(0, 0, Math.max(0.8, baseWidth * 0.38), 42, 0.92, 94, 2 * spriteScale);

      if (meteor.tailShape === "double") {
        drawCurve(meteor.size * 5.2 * spriteScale, meteor.bend * length * 0.08, baseWidth * 0.52, meteor.edgeHue, 0.58, 72, 5 * spriteScale);
        drawCurve(-meteor.size * 5.2 * spriteScale, -meteor.bend * length * 0.05, baseWidth * 0.46, meteor.hue, 0.48, 68, 5 * spriteScale);
      }

      for (const fragment of meteor.fragments) {
        const x = headX - length * fragment.along;
        const y = headY + fragment.side * meteor.size * spriteScale * 8.2 * (0.35 + fragment.along);
        const radius = fragment.size * spriteScale * (meteor.tailShape === "flare" ? 1.35 : 0.9);
        mctx.fillStyle = `hsla(${meteor.hue + fragment.hueShift}, 100%, 78%, ${0.2 + fragment.lifeBias * 0.22})`;
        mctx.shadowColor = `hsla(${meteor.edgeHue}, 100%, 74%, 0.32)`;
        mctx.shadowBlur = radius * 5;
        mctx.beginPath();
        mctx.arc(x, y, radius, 0, Math.PI * 2);
        mctx.fill();
      }

      const stretch = meteor.bodyShape === "blade" ? 2.1 : meteor.bodyShape === "oval" ? 1.55 : 1.32;
      const halo = mctx.createRadialGradient(headX, headY, 0, headX, headY, headRadius * 2.25);
      halo.addColorStop(0, "rgba(255,255,255,0.86)");
      halo.addColorStop(0.24, `hsla(${meteor.hue}, 100%, 78%, 0.52)`);
      halo.addColorStop(0.58, `hsla(${meteor.edgeHue}, 100%, 68%, 0.16)`);
      halo.addColorStop(1, `hsla(${meteor.edgeHue}, 100%, 60%, 0)`);
      mctx.save();
      mctx.translate(headX, headY);
      mctx.fillStyle = halo;
      mctx.beginPath();
      mctx.ellipse(0, 0, headRadius * stretch, headRadius, 0, 0, Math.PI * 2);
      mctx.fill();

      const core = mctx.createRadialGradient(headRadius * 0.22, -headRadius * 0.06, 0, 0, 0, headRadius * 0.9);
      core.addColorStop(0, "rgba(255,255,255,0.98)");
      core.addColorStop(0.36, "rgba(255,249,219,0.92)");
      core.addColorStop(0.72, `hsla(${meteor.hue}, 100%, 77%, 0.48)`);
      core.addColorStop(1, `hsla(${meteor.hue}, 100%, 65%, 0)`);
      mctx.fillStyle = core;
      mctx.beginPath();
      mctx.ellipse(0, 0, headRadius * 0.62 * stretch, headRadius * 0.52, 0, 0, Math.PI * 2);
      mctx.fill();

      if (meteor.bodyShape === "double") {
        mctx.fillStyle = "rgba(255,255,255,0.56)";
        for (const side of [-1, 1]) {
          mctx.beginPath();
          mctx.arc(-headRadius * 0.08, side * headRadius * 0.38, headRadius * 0.2, 0, Math.PI * 2);
          mctx.fill();
        }
      } else if (meteor.bodyShape === "star") {
        mctx.strokeStyle = "rgba(255,255,255,0.42)";
        mctx.lineWidth = Math.max(0.8, meteor.size * spriteScale * 0.8);
        mctx.beginPath();
        mctx.moveTo(-headRadius * 1.45, 0);
        mctx.lineTo(headRadius * 1.8, 0);
        mctx.moveTo(0, -headRadius * 0.85);
        mctx.lineTo(0, headRadius * 0.85);
        mctx.stroke();
      }
      mctx.restore();

      return {
        canvas: offscreen,
        headX,
        headY,
        width: canvasWidth,
        height: canvasHeight
      };
    }

    function drawBackground() {
      ctx.clearRect(0, 0, width, height);

      const glow = ctx.createRadialGradient(
        width * 0.52,
        height * 0.52,
        0,
        width * 0.52,
        height * 0.52,
        Math.max(width, height) * 0.72
      );
      glow.addColorStop(0, "rgba(40, 63, 105, 0.18)");
      glow.addColorStop(0.48, "rgba(8, 13, 32, 0.08)");
      glow.addColorStop(1, "rgba(0, 0, 0, 0)");
      ctx.fillStyle = glow;
      ctx.fillRect(0, 0, width, height);
    }

    function drawStars(time) {
      for (const star of stars) {
        const pulse = Math.sin(time * star.twinkle + star.phase) * 0.28;
        const alpha = Math.max(0.08, Math.min(1, star.alpha + pulse));

        ctx.beginPath();
        ctx.fillStyle = `rgba(${star.tint}, ${alpha})`;
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    function captureScene() {
      sceneCtx.setTransform(1, 0, 0, 1, 0, 0);
      sceneCtx.clearRect(0, 0, sceneBuffer.width, sceneBuffer.height);
      sceneCtx.drawImage(canvas, 0, 0);
    }

    function drawMagnifier() {
      if (!settings.magnifierEnabled || !pointer.active) {
        return;
      }

      const radius = settings.magnifierRadius;
      const zoom = settings.magnifierZoom;
      const sourceSize = (radius * 2) / zoom;
      const sourcePixels = sourceSize * pixelRatio;
      const maxSourceX = Math.max(0, sceneBuffer.width - sourcePixels);
      const maxSourceY = Math.max(0, sceneBuffer.height - sourcePixels);
      const sourceX = Math.min(Math.max((pointer.x - sourceSize / 2) * pixelRatio, 0), maxSourceX);
      const sourceY = Math.min(Math.max((pointer.y - sourceSize / 2) * pixelRatio, 0), maxSourceY);

      ctx.save();
      ctx.beginPath();
      ctx.arc(pointer.x, pointer.y, radius, 0, Math.PI * 2);
      ctx.clip();
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      ctx.drawImage(
        sceneBuffer,
        sourceX,
        sourceY,
        sourcePixels,
        sourcePixels,
        pointer.x - radius,
        pointer.y - radius,
        radius * 2,
        radius * 2
      );

      const lensGlow = ctx.createRadialGradient(pointer.x, pointer.y, radius * 0.4, pointer.x, pointer.y, radius);
      lensGlow.addColorStop(0, "rgba(255, 255, 255, 0)");
      lensGlow.addColorStop(1, "rgba(119, 215, 255, 0.16)");
      ctx.fillStyle = lensGlow;
      ctx.fillRect(pointer.x - radius, pointer.y - radius, radius * 2, radius * 2);
      ctx.restore();

      ctx.save();
      ctx.strokeStyle = "rgba(171, 228, 255, 0.84)";
      ctx.lineWidth = 2;
      ctx.shadowColor = "rgba(119, 215, 255, 0.62)";
      ctx.shadowBlur = 14;
      ctx.beginPath();
      ctx.arc(pointer.x, pointer.y, radius, 0, Math.PI * 2);
      ctx.stroke();

      ctx.shadowBlur = 0;
      ctx.strokeStyle = "rgba(255, 255, 255, 0.28)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(pointer.x - radius * 0.22, pointer.y);
      ctx.lineTo(pointer.x + radius * 0.22, pointer.y);
      ctx.moveTo(pointer.x, pointer.y - radius * 0.22);
      ctx.lineTo(pointer.x, pointer.y + radius * 0.22);
      ctx.stroke();
      ctx.restore();
    }

    function drawSun(centerX, centerY, scale) {
      const sunRadius = Math.max(16, 24 * scale);
      const pulse = 0.5 + Math.sin(simulationTime * 0.85) * 0.5;
      const coronaRadius = sunRadius * (5.1 + pulse * 0.22);
      const aura = ctx.createRadialGradient(centerX, centerY, sunRadius * 0.6, centerX, centerY, coronaRadius);

      aura.addColorStop(0, "rgba(255, 241, 174, 0.62)");
      aura.addColorStop(0.18, "rgba(255, 185, 70, 0.34)");
      aura.addColorStop(0.46, "rgba(255, 115, 35, 0.12)");
      aura.addColorStop(1, "rgba(255, 95, 25, 0)");
      ctx.fillStyle = aura;
      ctx.beginPath();
      ctx.arc(centerX, centerY, coronaRadius, 0, Math.PI * 2);
      ctx.fill();

      const sun = ctx.createRadialGradient(
        centerX - sunRadius * 0.24,
        centerY - sunRadius * 0.28,
        sunRadius * 0.08,
        centerX,
        centerY,
        sunRadius * 1.05
      );
      sun.addColorStop(0, "#fff9d2");
      sun.addColorStop(0.2, "#ffe27a");
      sun.addColorStop(0.56, "#ffb02f");
      sun.addColorStop(0.86, "#e97015");
      sun.addColorStop(1, "#9f3108");
      ctx.fillStyle = sun;
      ctx.shadowColor = "rgba(255, 182, 54, 0.85)";
      ctx.shadowBlur = 34 * scale;
      ctx.beginPath();
      ctx.arc(centerX, centerY, sunRadius, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;

      ctx.save();
      ctx.beginPath();
      ctx.arc(centerX, centerY, sunRadius * 0.98, 0, Math.PI * 2);
      ctx.clip();
      ctx.globalCompositeOperation = "multiply";

      for (let i = 0; i < 46; i += 1) {
        const angle = i * 1.618 + simulationTime * 0.08;
        const distance = sunRadius * (0.12 + (((i * 37) % 82) / 100));
        const granuleRadius = sunRadius * (0.035 + ((i * 13) % 8) / 260);
        const gx = centerX + Math.cos(angle) * distance * (0.9 + ((i * 5) % 9) / 35);
        const gy = centerY + Math.sin(angle * 1.07) * distance;

        ctx.fillStyle = `rgba(118, 44, 6, ${0.06 + ((i * 11) % 9) / 220})`;
        ctx.beginPath();
        ctx.arc(gx, gy, granuleRadius * 1.08, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.globalCompositeOperation = "screen";
      for (let i = 0; i < 28; i += 1) {
        const angle = i * 2.399 + simulationTime * 0.12;
        const distance = sunRadius * (0.16 + (((i * 29) % 70) / 100));
        const gx = centerX + Math.cos(angle) * distance;
        const gy = centerY + Math.sin(angle * 0.96) * distance;
        const bright = ctx.createRadialGradient(gx, gy, 0, gx, gy, sunRadius * 0.18);
        bright.addColorStop(0, "rgba(255, 238, 135, 0.16)");
        bright.addColorStop(1, "rgba(255, 238, 135, 0)");
        ctx.fillStyle = bright;
        ctx.beginPath();
        ctx.arc(gx, gy, sunRadius * 0.18, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();

      const limb = ctx.createRadialGradient(centerX, centerY, sunRadius * 0.62, centerX, centerY, sunRadius);
      limb.addColorStop(0, "rgba(255, 255, 255, 0)");
      limb.addColorStop(0.74, "rgba(170, 62, 6, 0.12)");
      limb.addColorStop(1, "rgba(73, 18, 4, 0.42)");
      ctx.fillStyle = limb;
      ctx.beginPath();
      ctx.arc(centerX, centerY, sunRadius, 0, Math.PI * 2);
      ctx.fill();

      drawSolarActivity(centerX, centerY, sunRadius, Math.min(0.033, 1 / 60));

      if (settings.showLabels) {
        ctx.fillStyle = "rgba(255, 255, 255, 0.78)";
        ctx.font = `${Math.max(11, 12 * scale)}px "Microsoft YaHei", sans-serif`;
        ctx.textAlign = "center";
        ctx.fillText("太阳", centerX, centerY + sunRadius + 18 * scale);
      }
      return sunRadius;
    }

    function drawOrbit(centerX, centerY, radius, yScale) {
      ctx.strokeStyle = "rgba(178, 205, 255, 0.14)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.ellipse(centerX, centerY, radius, radius * yScale, 0, 0, Math.PI * 2);
      ctx.stroke();
    }

    function drawPlanetBody(planet, x, y, radius, orbitAngle, rotationAngle) {
      const sunAngle = orbitAngle + Math.PI;
      const lightX = x + Math.cos(sunAngle) * radius * 0.42;
      const lightY = y + Math.sin(sunAngle) * radius * 0.42;
      const atmosphereStrength = planet.name === "地球" ? 0.28 : planet.name === "金星" ? 0.18 : 0.12;

      drawRadialGlow(x, y, radius, planet.color, atmosphereStrength * 0.7, planet.ring ? 3.5 : 2.55);

      const gradient = ctx.createRadialGradient(
        lightX,
        lightY,
        radius * 0.16,
        x,
        y,
        radius * 1.08
      );
      gradient.addColorStop(0, "rgba(255, 255, 255, 0.9)");
      gradient.addColorStop(0.34, planet.color);
      gradient.addColorStop(0.74, colorWithAlpha(planet.color, 0.68));
      gradient.addColorStop(1, "rgba(4, 7, 18, 0.94)");

      if (planet.ring) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(orbitAngle * 0.35 + 0.55);
        ctx.shadowColor = colorWithAlpha(planet.color, 0.45);
        ctx.shadowBlur = 8;
        ctx.strokeStyle = planet.name === "土星" ? "rgba(236, 217, 165, 0.62)" : "rgba(175, 241, 246, 0.36)";
        ctx.lineWidth = Math.max(1, radius * 0.22);
        ctx.beginPath();
        ctx.ellipse(0, 0, radius * 1.85, radius * 0.52, 0, 0, Math.PI * 2);
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.restore();
      }

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
      drawAtmosphere(x, y, radius, planet.color, sunAngle, atmosphereStrength);

      ctx.save();
      ctx.beginPath();
      ctx.arc(x, y, radius * 0.98, 0, Math.PI * 2);
      ctx.clip();
      ctx.translate(x, y);
      ctx.rotate(rotationAngle);
      ctx.strokeStyle = planet.name === "地球"
        ? "rgba(191, 237, 186, 0.5)"
        : "rgba(255, 255, 255, 0.24)";
      ctx.lineWidth = Math.max(1, radius * 0.16);

      for (let i = -2; i <= 2; i += 1) {
        ctx.beginPath();
        ctx.ellipse(0, i * radius * 0.36, radius * 1.15, radius * 0.12, 0, 0, Math.PI * 2);
        ctx.stroke();
      }

      ctx.restore();

      const night = ctx.createRadialGradient(
        x - Math.cos(sunAngle) * radius * 0.72,
        y - Math.sin(sunAngle) * radius * 0.72,
        radius * 0.25,
        x - Math.cos(sunAngle) * radius * 0.34,
        y - Math.sin(sunAngle) * radius * 0.34,
        radius * 1.35
      );
      night.addColorStop(0, "rgba(0, 0, 0, 0.36)");
      night.addColorStop(0.62, "rgba(0, 0, 0, 0.1)");
      night.addColorStop(1, "rgba(0, 0, 0, 0)");
      ctx.save();
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.clip();
      ctx.fillStyle = night;
      ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2);
      ctx.restore();
    }

    function drawMoon(earthX, earthY, earthRadius, earthDays, scale, earthRealX, earthRealY) {
      const moonOrbit = Math.max(13 * scale, earthRadius * 3.2);
      const moonRadius = Math.max(1.3, earthRadius * 0.28);
      const moonAngle = (earthDays / 27.3217) * Math.PI * 2;
      const moonX = earthX + Math.cos(moonAngle) * moonOrbit;
      const moonY = earthY + Math.sin(moonAngle) * moonOrbit * 0.62;
      const moonRealX = earthRealX + Math.cos(moonAngle) * MOON_ORBIT_AU;
      const moonRealY = earthRealY + Math.sin(moonAngle) * MOON_ORBIT_AU;

      ctx.strokeStyle = "rgba(210, 220, 238, 0.18)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.ellipse(earthX, earthY, moonOrbit, moonOrbit * 0.62, 0, 0, Math.PI * 2);
      ctx.stroke();

      const moon = ctx.createRadialGradient(
        moonX - moonRadius * 0.35,
        moonY - moonRadius * 0.35,
        moonRadius * 0.15,
        moonX,
        moonY,
        moonRadius
      );
      moon.addColorStop(0, "#ffffff");
      moon.addColorStop(0.55, "#cfd5df");
      moon.addColorStop(1, "#6f7888");

      drawRadialGlow(moonX, moonY, moonRadius, "#cfd5df", 0.16, 3.2);
      ctx.fillStyle = moon;
      ctx.shadowColor = "rgba(230, 238, 255, 0.45)";
      ctx.shadowBlur = 7 * scale;
      ctx.beginPath();
      ctx.arc(moonX, moonY, moonRadius, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
      drawAtmosphere(moonX, moonY, moonRadius, "#cfd5df", moonAngle + Math.PI, 0.1);

      if (settings.showLabels) {
        ctx.fillStyle = "rgba(226, 236, 255, 0.62)";
        ctx.fillText("月亮", moonX, moonY - moonRadius - 8 * scale);
      }

      return {
        x: moonX,
        y: moonY,
        realX: moonRealX,
        realY: moonRealY,
        realZ: 0,
        radius: moonRadius,
        hitRadius: Math.max(12, moonRadius + 8),
        data: moonInfo
      };
    }

    function drawPlanetSatellite(parentX, parentY, parentRadius, parentRealX, parentRealY, earthDays, scale, satellite) {
      const orbit = Math.max(parentRadius * satellite.visualOrbit, 10 * scale);
      const radius = Math.max(1.2, parentRadius * satellite.visualRadius);
      const angle = satellite.start + (earthDays / satellite.periodDays) * Math.PI * 2;
      const x = parentX + Math.cos(angle) * orbit;
      const y = parentY + Math.sin(angle) * orbit * 0.54;
      const realOrbitAU = satellite.distanceKm / AU_IN_KM;
      const realX = parentRealX + Math.cos(angle) * realOrbitAU;
      const realY = parentRealY + Math.sin(angle) * realOrbitAU;

      if (settings.showOrbits) {
        ctx.strokeStyle = "rgba(210, 220, 238, 0.12)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.ellipse(parentX, parentY, orbit, orbit * 0.54, 0, 0, Math.PI * 2);
        ctx.stroke();
      }

      drawTrail(satellite.name, satellite.color);
      if (!settings.paused) {
        recordTrail(satellite.name, x, y, 90);
      }

      drawRadialGlow(x, y, radius, satellite.color, 0.1, 2.4);
      const body = ctx.createRadialGradient(x - radius * 0.3, y - radius * 0.35, radius * 0.1, x, y, radius);
      body.addColorStop(0, "rgba(255, 255, 255, 0.9)");
      body.addColorStop(0.45, satellite.color);
      body.addColorStop(1, "rgba(16, 18, 28, 0.9)");
      ctx.fillStyle = body;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();

      if (settings.showLabels && radius > 1.4) {
        ctx.fillStyle = "rgba(226, 236, 255, 0.58)";
        ctx.fillText(satellite.name, x, y - radius - 7 * scale);
      }

      return {
        x,
        y,
        realX,
        realY,
        realZ: 0,
        radius,
        hitRadius: Math.max(9, radius + 6),
        data: satelliteInfos[satellite.name]
      };
    }

    function drawAsteroidBelt(centerX, centerY, minOrbit, maxOrbit, yScale, earthDays) {
      if (!settings.showAsteroids) {
        return;
      }

      const inner = minOrbit + ((maxOrbit - minOrbit) * 3) / (planets.length - 1);
      const outer = minOrbit + ((maxOrbit - minOrbit) * 4) / (planets.length - 1);
      const beltCenter = (inner + outer) / 2;
      const beltWidth = Math.max(8, (outer - inner) * 0.44);

      ctx.save();
      asteroids.forEach((asteroid) => {
        const angle = asteroid.phase + earthDays * 0.004 * asteroid.speed;
        const radius = beltCenter + asteroid.drift * beltWidth;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius * yScale;

        ctx.fillStyle = `rgba(196, 184, 160, ${asteroid.alpha})`;
        ctx.beginPath();
        ctx.arc(x, y, asteroid.size, 0, Math.PI * 2);
        ctx.fill();
      });

      ctx.restore();
      const beltAngle = earthDays * 0.004;
      solarTargets.push({
        x: centerX + Math.cos(beltAngle) * beltCenter,
        y: centerY + Math.sin(beltAngle) * beltCenter * yScale,
        realX: Math.cos(beltAngle) * 2.7,
        realY: Math.sin(beltAngle) * 2.7,
        realZ: 0,
        radius: beltWidth,
        hitRadius: Math.max(18, beltWidth * 0.8),
        data: asteroidBeltInfo
      });
    }

    function drawComet(centerX, centerY, maxOrbit, yScale, earthDays, scale) {
      if (!settings.showComets) {
        return;
      }

      const semiMajor = maxOrbit * 0.92;
      const semiMinor = semiMajor * 0.36;
      const angle = comet.start + (earthDays / (comet.orbitYears * 365.25)) * Math.PI * 2;
      const focusOffset = semiMajor * comet.eccentricity * 0.52;
      const x = centerX + Math.cos(angle) * semiMajor - focusOffset;
      const y = centerY + Math.sin(angle) * semiMinor * yScale;
      const realSemiMinor = comet.semiMajorAU * Math.sqrt(1 - comet.eccentricityReal ** 2);
      const realFocusOffset = comet.semiMajorAU * comet.eccentricityReal;
      const realX = Math.cos(angle) * comet.semiMajorAU - realFocusOffset;
      const realY = Math.sin(angle) * realSemiMinor;
      const tailAngle = Math.atan2(y - centerY, x - centerX);
      const tailLength = 28 * scale;

      drawTrail(comet.name, comet.color);
      if (!settings.paused) {
        recordTrail(comet.name, x, y, 170);
      }

      ctx.save();
      ctx.strokeStyle = "rgba(183, 255, 242, 0.14)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.ellipse(centerX - focusOffset, centerY, semiMajor, semiMinor * yScale, 0, 0, Math.PI * 2);
      ctx.stroke();

      const gradient = ctx.createLinearGradient(x, y, x + Math.cos(tailAngle) * tailLength, y + Math.sin(tailAngle) * tailLength);
      gradient.addColorStop(0, "rgba(220, 255, 250, 0.92)");
      gradient.addColorStop(1, "rgba(117, 215, 255, 0)");
      ctx.strokeStyle = gradient;
      ctx.lineWidth = 3 * scale;
      ctx.lineCap = "round";
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x + Math.cos(tailAngle) * tailLength, y + Math.sin(tailAngle) * tailLength);
      ctx.stroke();

      ctx.fillStyle = "#dffffa";
      ctx.shadowColor = "rgba(183, 255, 242, 0.72)";
      ctx.shadowBlur = 12 * scale;
      ctx.beginPath();
      ctx.arc(x, y, Math.max(2.2, 3.4 * scale), 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;

      if (settings.showLabels) {
        ctx.fillStyle = "rgba(226, 255, 250, 0.72)";
        ctx.fillText(comet.name, x, y - 13 * scale);
      }

      ctx.restore();
      solarTargets.push({
        x,
        y,
        realX,
        realY,
        realZ: 0,
        radius: 4 * scale,
        hitRadius: Math.max(14, 10 * scale),
        data: comet.info
      });
    }

    function drawFocusMarker(target) {
      if (!target) {
        return;
      }

      const pulse = 0.5 + Math.sin(simulationTime * 5) * 0.5;
      const radius = target.hitRadius + 8 + pulse * 5;

      ctx.save();
      ctx.strokeStyle = "rgba(119, 215, 255, 0.88)";
      ctx.lineWidth = 2;
      ctx.shadowColor = "rgba(119, 215, 255, 0.78)";
      ctx.shadowBlur = 14;
      ctx.beginPath();
      ctx.arc(target.x, target.y, radius, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();

      if (settings.magnifierEnabled) {
        pointer.x = target.x;
        pointer.y = target.y;
        pointer.active = true;
      }
    }

    function drawMeasurementLine() {
      if (measurement.points.length === 0) {
        return;
      }

      const current = measurement.points
        .map((point) => solarTargets.find((target) => target.data.name === point.data.name))
        .filter(Boolean);

      if (current.length === 0) {
        return;
      }

      ctx.save();
      ctx.strokeStyle = "rgba(255, 232, 126, 0.82)";
      ctx.fillStyle = "rgba(255, 244, 184, 0.92)";
      ctx.lineWidth = 1.6;
      current.forEach((target) => {
        ctx.beginPath();
        ctx.arc(target.x, target.y, target.hitRadius + 4, 0, Math.PI * 2);
        ctx.stroke();
      });

      if (current.length === 2) {
        const [a, b] = current;
        const realDistance = getRealDistance(a, b);
        const label = realDistance ? `${formatAU(realDistance.au)} / ${formatKm(realDistance.km)}` : `${Math.hypot(a.x - b.x, a.y - b.y).toFixed(1)}px`;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
        ctx.fillText(label, (a.x + b.x) / 2, (a.y + b.y) / 2 - 10);
        updateMeasurementBanner();
      }

      ctx.restore();
    }

    function drawTeachingAnnotation(target, centerX, centerY) {
      if (!settings.showTeaching || !target) {
        return;
      }

      const dx = target.x - centerX;
      const dy = target.y - centerY;
      const distance = Math.hypot(dx, dy) || 1;
      const tangentX = -dy / distance;
      const tangentY = dx / distance;
      const arrowLength = Math.max(28, target.hitRadius * 2.4);
      const labelX = Math.min(width - 220, Math.max(24, target.x + 22));
      const labelY = Math.min(height - 120, Math.max(24, target.y - 54));
      const realDistance = Number.isFinite(target.realX) && Number.isFinite(target.realY)
        ? Math.hypot(target.realX, target.realY, target.realZ || 0)
        : null;
      const rows = [
        target.data.name,
        target.data.orbitSpeed ? `公转速度：${target.data.orbitSpeed}` : "",
        target.data.year ? `公转周期：${target.data.year}` : "",
        realDistance ? `距太阳：${formatAU(realDistance)}` : ""
      ].filter(Boolean);

      ctx.save();
      ctx.strokeStyle = "rgba(119, 215, 255, 0.78)";
      ctx.fillStyle = "rgba(119, 215, 255, 0.9)";
      ctx.lineWidth = 1.5;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(target.x, target.y);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.strokeStyle = "rgba(255, 232, 126, 0.9)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(target.x, target.y);
      ctx.lineTo(target.x + tangentX * arrowLength, target.y + tangentY * arrowLength);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(target.x, target.y, target.hitRadius + 5, 0, Math.PI * 2);
      ctx.stroke();

      ctx.fillStyle = "rgba(4, 9, 24, 0.76)";
      ctx.strokeStyle = "rgba(255, 255, 255, 0.16)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(labelX, labelY, 196, 24 + rows.length * 17, 8);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = "rgba(245, 248, 255, 0.92)";
      ctx.font = "12px \"Microsoft YaHei\", sans-serif";
      rows.forEach((row, index) => {
        ctx.fillText(row, labelX + 12, labelY + 20 + index * 17);
      });
      ctx.restore();
    }

    function drawSolarSystem(time) {
      const minSize = Math.min(width, height);
      const scale = Math.max(0.64, Math.min(minSize / 820, 1.15));
      const centerX = width * 0.5;
      const centerY = height * 0.54;
      const yScale = 0.56;
      const minOrbit = settings.scaleMode === "relative" ? Math.max(34, minSize * 0.06) : Math.max(40, minSize * 0.09);
      const maxOrbit = Math.max(minOrbit + 180 * scale, minSize * 0.43);
      const earthDays = time * SIMULATED_DAYS_PER_SECOND;
      let focusTarget = null;

      ctx.save();
      solarTargets.length = 0;
      const sunRadius = drawSun(centerX, centerY, scale);
      solarTargets.push({
        x: centerX,
        y: centerY,
        realX: 0,
        realY: 0,
        realZ: 0,
        radius: sunRadius,
        hitRadius: sunRadius + 10,
        data: sunInfo
      });
      ctx.font = `${Math.max(10, 11 * scale)}px "Microsoft YaHei", sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      drawAsteroidBelt(centerX, centerY, minOrbit, maxOrbit, yScale, earthDays);
      drawComet(centerX, centerY, maxOrbit, yScale, earthDays, scale);

      planets.forEach((planet, index) => {
        const orbitProgress = settings.scaleMode === "relative"
          ? Math.pow(index / (planets.length - 1), 1.45)
          : index / (planets.length - 1);
        const orbitRadius = minOrbit + (maxOrbit - minOrbit) * orbitProgress;
        const orbitAngle = planet.start + (earthDays / (planet.orbitYears * 365.25)) * Math.PI * 2;
        const rotationAngle = (earthDays * 24 / planet.rotationHours) * Math.PI * 2;
        const x = centerX + Math.cos(orbitAngle) * orbitRadius;
        const y = centerY + Math.sin(orbitAngle) * orbitRadius * yScale;
        const realX = Math.cos(orbitAngle) * planet.au;
        const realY = Math.sin(orbitAngle) * planet.au;
        const visualRadius = settings.scaleMode === "relative"
          ? Math.max(2.1, Math.sqrt(planet.radius) * 2.1 * scale)
          : Math.max(2.6, planet.radius * scale);

        if (settings.showOrbits) {
          drawOrbit(centerX, centerY, orbitRadius, yScale);
        }

        drawTrail(planet.name, planet.color);
        if (!settings.paused) {
          recordTrail(planet.name, x, y);
        }

        ctx.shadowColor = planet.color;
        ctx.shadowBlur = 10 * scale;
        drawPlanetBody(planet, x, y, visualRadius, orbitAngle, rotationAngle);
        ctx.shadowBlur = 0;
        solarTargets.push({
          x,
          y,
          realX,
          realY,
          realZ: 0,
          radius: visualRadius,
          hitRadius: Math.max(12, visualRadius + 7),
          data: planet
        });

        if (planet.name === "地球") {
          const moonTarget = drawMoon(x, y, visualRadius, earthDays, scale, realX, realY);
          solarTargets.push(moonTarget);
          drawTrail("月亮", "#cfd5df");
          if (!settings.paused) {
            recordTrail("月亮", moonTarget.x, moonTarget.y, 120);
          }
        }

        if (satelliteSystems[planet.name]) {
          satelliteSystems[planet.name].forEach((satellite) => {
            solarTargets.push(drawPlanetSatellite(x, y, visualRadius, realX, realY, earthDays, scale, satellite));
          });
        }

        if (settings.showLabels) {
          ctx.fillStyle = "rgba(226, 236, 255, 0.72)";
          ctx.fillText(planet.name, x, y - visualRadius - 10 * scale);
        }
      });

      focusTarget = solarTargets.find((target) => target.data.name === settings.focusTarget);
      drawFocusMarker(focusTarget);
      drawTeachingAnnotation(solarTargets.find((target) => target.data.name === teachingTargetName) || focusTarget, centerX, centerY);
      drawMeasurementLine();

      ctx.restore();
    }

    function clamp(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }

    function easeOutCubic(value) {
      return 1 - Math.pow(1 - clamp(value, 0, 1), 3);
    }

    function drawMeteorCurve(meteor, angle, length, offset, width, opacity, hue, saturation, lightness, blur = 0) {
      const normalX = -Math.sin(angle);
      const normalY = Math.cos(angle);
      const headX = meteor.x + normalX * offset;
      const headY = meteor.y + normalY * offset;
      const tailX = headX - Math.cos(angle) * length;
      const tailY = headY - Math.sin(angle) * length;
      const controlX = headX - Math.cos(angle) * length * 0.46 + normalX * meteor.bend * length * 0.12;
      const controlY = headY - Math.sin(angle) * length * 0.46 + normalY * meteor.bend * length * 0.12;
      const gradient = ctx.createLinearGradient(tailX, tailY, headX, headY);

      gradient.addColorStop(0, `hsla(${hue}, ${saturation}%, ${lightness}%, 0)`);
      gradient.addColorStop(0.22, `hsla(${hue}, ${saturation}%, ${lightness}%, ${0.05 * opacity})`);
      gradient.addColorStop(0.62, `hsla(${hue}, ${saturation}%, ${lightness}%, ${0.34 * opacity})`);
      gradient.addColorStop(0.9, `rgba(255, 247, 224, ${0.72 * opacity})`);
      gradient.addColorStop(1, `rgba(255, 255, 255, ${0.98 * opacity})`);

      ctx.save();
      ctx.shadowColor = `hsla(${hue}, 100%, 72%, ${0.48 * opacity})`;
      ctx.shadowBlur = blur;
      ctx.strokeStyle = gradient;
      ctx.lineWidth = Math.max(0.7, width);
      ctx.beginPath();
      ctx.moveTo(tailX, tailY);
      ctx.quadraticCurveTo(controlX, controlY, headX, headY);
      ctx.stroke();
      ctx.restore();
    }

    function drawMeteorDustWake(meteor, opacity, length, angle, widthFactor) {
      const tailWidth = meteor.size * widthFactor;
      const normalX = -Math.sin(angle);
      const normalY = Math.cos(angle);
      const tailX = meteor.x - Math.cos(angle) * length;
      const tailY = meteor.y - Math.sin(angle) * length;
      const midX = meteor.x - Math.cos(angle) * length * 0.44 + normalX * meteor.bend * length * 0.16;
      const midY = meteor.y - Math.sin(angle) * length * 0.44 + normalY * meteor.bend * length * 0.16;
      const gradient = ctx.createLinearGradient(tailX, tailY, meteor.x, meteor.y);

      gradient.addColorStop(0, `hsla(${meteor.hue}, 84%, 50%, 0)`);
      gradient.addColorStop(0.48, `hsla(${meteor.hue}, 82%, 58%, ${0.08 * opacity})`);
      gradient.addColorStop(1, `hsla(${meteor.hue}, 96%, 74%, ${0.28 * opacity})`);

      ctx.save();
      ctx.globalCompositeOperation = "screen";
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.moveTo(meteor.x + normalX * tailWidth, meteor.y + normalY * tailWidth);
      ctx.quadraticCurveTo(midX + normalX * tailWidth * 0.48, midY + normalY * tailWidth * 0.48, tailX, tailY);
      ctx.quadraticCurveTo(midX - normalX * tailWidth * 0.42, midY - normalY * tailWidth * 0.42, meteor.x - normalX * tailWidth, meteor.y - normalY * tailWidth);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }

    function drawMeteorFragments(meteor, opacity, length, angle, progress) {
      const normalX = -Math.sin(angle);
      const normalY = Math.cos(angle);
      const forwardX = Math.cos(angle);
      const forwardY = Math.sin(angle);
      const flareBoost = meteor.tailShape === "flare" ? 1.45 : 1;

      ctx.save();
      ctx.globalCompositeOperation = "lighter";
      for (const fragment of meteor.fragments) {
        const localFade = opacity * clamp((1 - progress * 0.42) * fragment.lifeBias, 0, 1);
        const drift = fragment.drift * meteor.age;
        const along = length * fragment.along + drift;
        const side = fragment.side * meteor.size * 7.8 * (0.35 + fragment.along);
        const x = meteor.x - forwardX * along + normalX * side;
        const y = meteor.y - forwardY * along + normalY * side;
        const twinkle = 0.65 + Math.sin(simulationTime * 8 + fragment.phase) * 0.35;
        const radius = fragment.size * flareBoost * twinkle;

        ctx.fillStyle = `hsla(${meteor.hue + fragment.hueShift}, 100%, 78%, ${0.34 * localFade})`;
        ctx.shadowColor = `hsla(${meteor.edgeHue}, 100%, 74%, ${0.36 * localFade})`;
        ctx.shadowBlur = radius * 5;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }

    function drawMeteorHead(meteor, opacity, angle, flash) {
      const radius = meteor.size * (meteor.bodyShape === "comet" ? 9.5 : meteor.bodyShape === "blade" ? 6.8 : 7.8);
      const stretch = meteor.bodyShape === "blade" ? 2.15 : meteor.bodyShape === "oval" ? 1.55 : 1.35;

      ctx.save();
      ctx.translate(meteor.x, meteor.y);
      ctx.rotate(angle);
      ctx.globalCompositeOperation = "lighter";

      const halo = ctx.createRadialGradient(0, 0, 0, 0, 0, radius * 2.15);
      halo.addColorStop(0, `rgba(255, 255, 255, ${0.76 * opacity * flash})`);
      halo.addColorStop(0.22, `hsla(${meteor.hue}, 100%, 78%, ${0.44 * opacity})`);
      halo.addColorStop(0.55, `hsla(${meteor.edgeHue}, 100%, 68%, ${0.14 * opacity})`);
      halo.addColorStop(1, `hsla(${meteor.edgeHue}, 100%, 60%, 0)`);
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.ellipse(0, 0, radius * stretch, radius * 1.02, 0, 0, Math.PI * 2);
      ctx.fill();

      const core = ctx.createRadialGradient(radius * 0.22, -radius * 0.06, 0, 0, 0, radius * 0.88);
      core.addColorStop(0, `rgba(255, 255, 255, ${opacity})`);
      core.addColorStop(0.36, `rgba(255, 249, 219, ${0.92 * opacity})`);
      core.addColorStop(0.72, `hsla(${meteor.hue}, 100%, 77%, ${0.48 * opacity})`);
      core.addColorStop(1, `hsla(${meteor.hue}, 100%, 65%, 0)`);
      ctx.fillStyle = core;
      ctx.beginPath();
      ctx.ellipse(0, 0, radius * 0.62 * stretch, radius * 0.52, 0, 0, Math.PI * 2);
      ctx.fill();

      if (meteor.bodyShape === "double") {
        ctx.fillStyle = `rgba(255, 255, 255, ${0.62 * opacity})`;
        for (const side of [-1, 1]) {
          ctx.beginPath();
          ctx.arc(-radius * 0.08, side * radius * 0.38, radius * 0.2, 0, Math.PI * 2);
          ctx.fill();
        }
      } else if (meteor.bodyShape === "star") {
        ctx.strokeStyle = `rgba(255, 255, 255, ${0.46 * opacity})`;
        ctx.lineWidth = Math.max(0.8, meteor.size * 0.8);
        ctx.beginPath();
        ctx.moveTo(-radius * 1.45, 0);
        ctx.lineTo(radius * 1.8, 0);
        ctx.moveTo(0, -radius * 0.85);
        ctx.lineTo(0, radius * 0.85);
        ctx.stroke();
      }

      ctx.restore();
    }

    function drawMeteorTailByShape(meteor, opacity, length, angle, flash) {
      const width = meteor.size * (meteor.tailShape === "blade" ? 1.7 : meteor.tailShape === "comet" ? 4.2 : 2.7);
      const dustWidth = meteor.tailShape === "comet" ? 18 : meteor.tailShape === "blade" ? 7 : 12;

      drawMeteorDustWake(meteor, opacity, length * (meteor.tailShape === "blade" ? 0.72 : 0.88), angle, dustWidth);
      drawMeteorCurve(meteor, angle, length, 0, width * 2.1, opacity * 0.34, meteor.hue, 96, 64, 22 * meteor.size);
      drawMeteorCurve(meteor, angle, length * 0.92, 0, width, opacity * 0.72, meteor.edgeHue, 100, 72, 11 * meteor.size);
      drawMeteorCurve(meteor, angle, length * 0.68, 0, Math.max(0.85, width * 0.46), opacity * flash, 42, 30, 94, 4 * meteor.size);

      if (meteor.tailShape === "double") {
        drawMeteorCurve(meteor, angle, length * 0.84, meteor.size * 5.2, width * 0.55, opacity * 0.58, meteor.edgeHue, 100, 72, 7 * meteor.size);
        drawMeteorCurve(meteor, angle, length * 0.78, -meteor.size * 5.2, width * 0.48, opacity * 0.48, meteor.hue, 100, 68, 7 * meteor.size);
      }

      if (meteor.tailShape === "flare") {
        drawMeteorFragments(meteor, opacity * 1.2, length * 0.86, angle, meteor.age / meteor.life);
      }
    }

    function drawMeteor(meteor, delta) {
      meteor.age += delta;
      meteor.x += meteor.vx * delta;
      meteor.y += meteor.vy * delta;

      const progress = meteor.age / meteor.life;
      const ignition = easeOutCubic(progress / 0.16);
      const decay = Math.pow(clamp(1 - progress, 0, 1), 0.58);
      const flicker = 0.86 + Math.sin(simulationTime * meteor.flicker + meteor.phase) * 0.14;
      const opacity = clamp(ignition * decay * flicker, 0, 1);
      const flash = 1 + Math.max(0, 1 - progress / 0.18) * 0.55;
      const angle = Math.atan2(meteor.vy, meteor.vx);

      ctx.save();
      ctx.translate(meteor.x, meteor.y);
      ctx.rotate(angle);
      ctx.globalCompositeOperation = "lighter";
      ctx.globalAlpha = Math.min(1, opacity * flash);
      ctx.drawImage(
        meteor.sprite.canvas,
        -meteor.sprite.headX,
        -meteor.sprite.headY,
        meteor.sprite.width,
        meteor.sprite.height
      );
      ctx.restore();
    }

    let lastTime = performance.now();

    function animate(now) {
      const delta = Math.min((now - lastTime) / 1000, 0.033);
      lastTime = now;

      if (!settings.paused) {
        simulationTime += delta * settings.timeSpeed;
      }
      updateSimulationClock();

      drawBackground();
      if (settings.showStars) {
        drawStars(now);
      }
      drawSolarSystem(simulationTime);
      captureScene();
      drawMagnifier();

      if (settings.showMeteors) {
        for (let i = meteors.length - 1; i >= 0; i -= 1) {
          drawMeteor(meteors[i], delta);
          if (meteors[i].age > meteors[i].life) {
            meteors.splice(i, 1);
          }
        }
      }

      requestAnimationFrame(animate);
    }

    window.addEventListener("resize", resize);
    window.addEventListener("click", (event) => {
      if (controls.contains(event.target) || infoPanel.contains(event.target)) {
        return;
      }

      const target = findSolarTarget(event.clientX, event.clientY);

      if (target) {
        showInfo(target);
        teachingTargetName = target.data.name;
        if (settings.measureMode) {
          addMeasurementTarget(target);
        }
        return;
      }

      if (settings.showMeteors) {
        createMeteor(event.clientX, event.clientY);
      }
    });
    window.addEventListener("contextmenu", (event) => {
      event.preventDefault();
    });
    consoleToggle.addEventListener("click", () => {
      const hidden = document.body.classList.toggle("console-hidden");
      consoleToggle.textContent = hidden ? "显示控制台" : "隐藏控制台";
      consoleToggle.setAttribute("aria-expanded", String(!hidden));
    });
    infoClose.addEventListener("click", () => {
      infoPanel.hidden = true;
    });
    infoFocusControl.addEventListener("click", () => {
      if (selectedInfoTarget) {
        setFocusTarget(selectedInfoTarget);
      }
    });
    infoMeasureControl.addEventListener("click", () => {
      if (!selectedInfoTarget) {
        return;
      }

      const target = solarTargets.find((item) => item.data.name === selectedInfoTarget);
      if (target) {
        measureControl.checked = true;
        updateDisplaySettings();
        addMeasurementTarget(target);
      }
    });
    timeSpeedControl.addEventListener("input", updateTimeSetting);
    screenshotControl.addEventListener("click", saveScreenshot);
    pauseControl.addEventListener("click", () => {
      settings.paused = !settings.paused;
      pauseControl.textContent = settings.paused ? "继续" : "暂停";
    });
    scaleModeControl.addEventListener("change", () => {
      planetTrails.clear();
      updateDisplaySettings();
    });
    targetSelect.addEventListener("change", () => {
      teachingTargetName = targetSelect.value;

      if (!targetSelect.value) {
        setFocusTarget("");
        teachingTargetName = "";
        pointer.active = false;
        return;
      }

      locateTarget(targetSelect.value, true);
    });
    measureControl.addEventListener("change", () => {
      updateDisplaySettings();
      if (!measureControl.checked) {
        clearMeasurement();
        measureBanner.hidden = true;
      }
    });
    clearMeasureControl.addEventListener("click", clearMeasurement);
    [
      showTrailsControl,
      showOrbitsControl,
      showLabelsControl,
      showAsteroidsControl,
      showCometsControl,
      showMeteorsControl,
      showStarsControl,
      showTeachingControl,
      showSolarActivityControl
    ].forEach((control) => {
      control.addEventListener("change", updateDisplaySettings);
    });
    performanceModeControl.addEventListener("change", () => {
      updateDisplaySettings();
      createStars();
      createAsteroids();
    });
    solarActivityIntensityControl.addEventListener("input", updateSolarActivitySetting);
    triggerSolarBurstControl.addEventListener("click", () => {
      spawnSolarActivity("cme");
      spawnSolarActivity("flare");
    });
    sizeControl.addEventListener("input", () => {
      updateSetting(sizeControl, sizeValue, "size");
    });
    speedControl.addEventListener("input", () => {
      updateSetting(speedControl, speedValue, "speed");
    });
    magnifierControl.addEventListener("change", updateMagnifierSetting);
    magnifierZoomControl.addEventListener("input", updateMagnifierSetting);
    magnifierRadiusControl.addEventListener("input", updateMagnifierSetting);
    tailShapeInputs.forEach((input) => {
      input.addEventListener("change", () => {
        updateShapeSetting(tailShapeInputs, tailShapeValue, tailShapeSummary, tailShapeNames, "tailShapes", "随机全部拖尾", input);
      });
    });
    bodyShapeInputs.forEach((input) => {
      input.addEventListener("change", () => {
        updateShapeSetting(bodyShapeInputs, bodyShapeValue, bodyShapeSummary, bodyShapeNames, "bodyShapes", "随机全部本体", input);
      });
    });
    window.addEventListener("pointermove", (event) => {
      pointer.x = event.clientX;
      pointer.y = event.clientY;
      pointer.active = !controls.contains(event.target) && !infoPanel.contains(event.target);
    });
    window.addEventListener("pointerleave", () => {
      pointer.active = false;
    });

    pageOpenedValue.textContent = formatDateTime(pageOpenedAt);
    updateSimulationClock(true);
    updateSetting(sizeControl, sizeValue, "size");
    updateSetting(speedControl, speedValue, "speed");
    updateTimeSetting();
    updateDisplaySettings();
    updateSolarActivitySetting();
    updateMagnifierSetting();
    updateShapeSetting(tailShapeInputs, tailShapeValue, tailShapeSummary, tailShapeNames, "tailShapes", "随机全部拖尾");
    updateShapeSetting(bodyShapeInputs, bodyShapeValue, bodyShapeSummary, bodyShapeNames, "bodyShapes", "随机全部本体");
    resize();
    requestAnimationFrame(animate);

