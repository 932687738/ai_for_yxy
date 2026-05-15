const canvas = document.getElementById("sky");
    const ctx = canvas.getContext("2d");
    const sceneBuffer = document.createElement("canvas");
    const sceneCtx = sceneBuffer.getContext("2d");
    const controls = document.getElementById("controls");
    const timeSpeedControl = document.getElementById("timeSpeedControl");
    const pauseControl = document.getElementById("pauseControl");
    const resetTimeControl = document.getElementById("resetTimeControl");
    const scaleModeControl = document.getElementById("scaleModeControl");
    const targetSelect = document.getElementById("targetSelect");
    const locateControl = document.getElementById("locateControl");
    const focusControl = document.getElementById("focusControl");
    const measureControl = document.getElementById("measureControl");
    const clearMeasureControl = document.getElementById("clearMeasureControl");
    const showTrailsControl = document.getElementById("showTrailsControl");
    const showOrbitsControl = document.getElementById("showOrbitsControl");
    const showLabelsControl = document.getElementById("showLabelsControl");
    const showAsteroidsControl = document.getElementById("showAsteroidsControl");
    const showCometsControl = document.getElementById("showCometsControl");
    const showMeteorsControl = document.getElementById("showMeteorsControl");
    const showStarsControl = document.getElementById("showStarsControl");
    const sizeControl = document.getElementById("sizeControl");
    const speedControl = document.getElementById("speedControl");
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
    const measurement = {
      points: []
    };

    let width = 0;
    let height = 0;
    let pixelRatio = 1;
    let simulationTime = 0;
    let selectedInfoTarget = null;
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
    const AU_IN_KM = 149597870.7;
    const MOON_ORBIT_AU = 384400 / AU_IN_KM;
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
      木星: { moons: "已知卫星超过 90 颗", atmosphere: "氢、氦为主", missions: "伽利略号、朱诺号、欧罗巴快船", fact: "大红斑是持续数百年的巨型风暴。" },
      土星: { moons: "已知卫星超过 140 颗", atmosphere: "氢、氦为主", missions: "先锋11号、旅行者、卡西尼", fact: "土星环主要由冰粒和岩屑组成。" },
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

    function updateSetting(control, output, key) {
      settings[key] = Number(control.value);
      output.value = `${settings[key].toFixed(key === "speed" ? 2 : 1)}x`;
    }

    function updateTimeSetting() {
      settings.timeSpeed = Number(timeSpeedControl.value);
      timeSpeedValue.value = `${settings.timeSpeed.toFixed(1)}x`;
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
      measureBanner.hidden = !settings.measureMode || measurement.points.length >= 2;
    }

    function updateMagnifierSetting() {
      settings.magnifierEnabled = magnifierControl.checked;
      settings.magnifierZoom = Number(magnifierZoomControl.value);
      settings.magnifierRadius = Number(magnifierRadiusControl.value);
      magnifierZoomValue.value = `${settings.magnifierZoom.toFixed(1)}x`;
      magnifierRadiusValue.value = `${Math.round(settings.magnifierRadius)}px`;
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
      const count = Math.floor((width * height) / 4200);

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
      const count = Math.max(90, Math.floor((width * height) / 9000));

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
      const hue = Math.floor(random(0, 360));
      const angle = random(0, Math.PI * 2);
      const size = random(0.95, 2.45) * settings.size;
      const speed = random(520, 900) * settings.speed;
      const tail = random(170, 340) * Math.sqrt(size);
      const tailShape = settings.tailShapes[Math.floor(Math.random() * settings.tailShapes.length)] || "trail";
      const bodyShape = settings.bodyShapes[Math.floor(Math.random() * settings.bodyShapes.length)] || "oval";

      meteors.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        age: 0,
        life: random(0.65, 1.05),
        size,
        tail,
        tailShape,
        bodyShape,
        hue,
        color: `hsl(${hue} 95% 68%)`,
        glow: `hsla(${hue}, 100%, 72%, 0.55)`
      });
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

    function drawSolarSystem(time) {
      const minSize = Math.min(width, height);
      const scale = Math.max(0.64, Math.min(minSize / 820, 1.15));
      const centerX = width * 0.5;
      const centerY = height * 0.54;
      const yScale = 0.56;
      const minOrbit = settings.scaleMode === "relative" ? Math.max(34, minSize * 0.06) : Math.max(40, minSize * 0.09);
      const maxOrbit = Math.max(minOrbit + 180 * scale, minSize * 0.43);
      const earthDays = time * 8;
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

        if (settings.showLabels) {
          ctx.fillStyle = "rgba(226, 236, 255, 0.72)";
          ctx.fillText(planet.name, x, y - visualRadius - 10 * scale);
        }
      });

      focusTarget = solarTargets.find((target) => target.data.name === settings.focusTarget);
      drawFocusMarker(focusTarget);
      drawMeasurementLine();

      ctx.restore();
    }

    function drawMeteorTail(meteor, opacity, length, angle, widthScale = 1, offset = 0) {
      const normalX = -Math.sin(angle) * offset;
      const normalY = Math.cos(angle) * offset;
      const headX = meteor.x + normalX;
      const headY = meteor.y + normalY;
      const tailX = headX - Math.cos(angle) * length;
      const tailY = headY - Math.sin(angle) * length;
      const gradient = ctx.createLinearGradient(tailX, tailY, headX, headY);

      gradient.addColorStop(0, `hsla(${meteor.hue}, 100%, 68%, 0)`);
      gradient.addColorStop(0.32, `hsla(${meteor.hue}, 100%, 68%, ${0.16 * opacity})`);
      gradient.addColorStop(1, `hsla(${meteor.hue}, 100%, 76%, ${0.95 * opacity})`);

      ctx.strokeStyle = gradient;
      ctx.lineWidth = 3.4 * meteor.size * widthScale;
      ctx.beginPath();
      ctx.moveTo(tailX, tailY);
      ctx.lineTo(headX, headY);
      ctx.stroke();
    }

    function drawOvalBody(meteor, opacity, angle, radiusScale = 1, stretch = 1.35) {
      const radius = 3.8 * meteor.size * radiusScale;

      ctx.save();
      ctx.translate(meteor.x, meteor.y);
      ctx.rotate(angle);
      ctx.fillStyle = `hsla(${meteor.hue}, 100%, 90%, ${opacity})`;
      ctx.beginPath();
      ctx.ellipse(0, 0, radius * stretch, radius, 0, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = `rgba(255, 255, 255, ${0.84 * opacity})`;
      ctx.beginPath();
      ctx.ellipse(radius * 0.42, -radius * 0.18, radius * 0.42, radius * 0.28, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    function drawCometBody(meteor, opacity, angle) {
      const radius = 7.5 * meteor.size;

      ctx.save();
      ctx.translate(meteor.x, meteor.y);
      ctx.rotate(angle);

      const glow = ctx.createRadialGradient(0, 0, 0, 0, 0, radius * 1.4);
      glow.addColorStop(0, `hsla(${meteor.hue}, 100%, 94%, ${0.95 * opacity})`);
      glow.addColorStop(0.42, `hsla(${meteor.hue}, 100%, 72%, ${0.55 * opacity})`);
      glow.addColorStop(1, `hsla(${meteor.hue}, 100%, 68%, 0)`);

      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.ellipse(0, 0, radius * 1.15, radius * 0.92, 0, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = `rgba(255, 255, 255, ${0.9 * opacity})`;
      ctx.beginPath();
      ctx.ellipse(radius * 0.2, -radius * 0.12, radius * 0.38, radius * 0.24, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    function drawDoubleBody(meteor, opacity, angle) {
      const offset = 5.3 * meteor.size;
      const radius = 3.1 * meteor.size;
      const normalX = -Math.sin(angle) * offset;
      const normalY = Math.cos(angle) * offset;

      ctx.strokeStyle = `hsla(${meteor.hue}, 100%, 80%, ${0.5 * opacity})`;
      ctx.lineWidth = Math.max(1.2, 1.1 * meteor.size);
      ctx.beginPath();
      ctx.moveTo(meteor.x - normalX, meteor.y - normalY);
      ctx.lineTo(meteor.x + normalX, meteor.y + normalY);
      ctx.stroke();

      for (const side of [-1, 1]) {
        ctx.fillStyle = `hsla(${meteor.hue}, 100%, ${side === 1 ? 92 : 82}%, ${opacity})`;
        ctx.beginPath();
        ctx.arc(meteor.x + normalX * side, meteor.y + normalY * side, radius, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    function drawStarBody(meteor, opacity, angle) {
      const points = 8;
      const outer = 8.2 * meteor.size;
      const inner = 3.1 * meteor.size;

      ctx.save();
      ctx.translate(meteor.x, meteor.y);
      ctx.rotate(angle + Math.PI / 8);
      ctx.fillStyle = `hsla(${meteor.hue}, 100%, 88%, ${0.9 * opacity})`;
      ctx.beginPath();

      for (let i = 0; i < points * 2; i += 1) {
        const radius = i % 2 === 0 ? outer : inner;
        const pointAngle = (Math.PI * i) / points;
        const x = Math.cos(pointAngle) * radius;
        const y = Math.sin(pointAngle) * radius;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }

      ctx.closePath();
      ctx.fill();

      ctx.fillStyle = `rgba(255, 255, 255, ${0.88 * opacity})`;
      ctx.beginPath();
      ctx.arc(0, 0, 2.2 * meteor.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    function drawBladeBody(meteor, opacity, angle) {
      const length = 11 * meteor.size;
      const width = 4.8 * meteor.size;

      ctx.save();
      ctx.translate(meteor.x, meteor.y);
      ctx.rotate(angle);
      ctx.fillStyle = `hsla(${meteor.hue}, 100%, 88%, ${0.92 * opacity})`;
      ctx.beginPath();
      ctx.moveTo(length, 0);
      ctx.lineTo(0, width);
      ctx.lineTo(-length * 0.62, 0);
      ctx.lineTo(0, -width);
      ctx.closePath();
      ctx.fill();

      ctx.fillStyle = `rgba(255, 255, 255, ${0.72 * opacity})`;
      ctx.beginPath();
      ctx.moveTo(length * 0.58, 0);
      ctx.lineTo(0, width * 0.36);
      ctx.lineTo(-length * 0.18, 0);
      ctx.lineTo(0, -width * 0.36);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }

    function drawFlareTail(meteor, opacity, angle) {
      const rayLength = 14 * meteor.size;

      ctx.strokeStyle = `hsla(${meteor.hue}, 100%, 82%, ${0.72 * opacity})`;
      ctx.lineWidth = Math.max(1.2, 1.3 * meteor.size);

      for (let i = 0; i < 4; i += 1) {
        const rayAngle = angle + (Math.PI / 4) + i * (Math.PI / 2);
        ctx.beginPath();
        ctx.moveTo(meteor.x - Math.cos(rayAngle) * rayLength * 0.35, meteor.y - Math.sin(rayAngle) * rayLength * 0.35);
        ctx.lineTo(meteor.x + Math.cos(rayAngle) * rayLength, meteor.y + Math.sin(rayAngle) * rayLength);
        ctx.stroke();
      }
    }

    function drawBlade(meteor, opacity, length, angle) {
      const widthScale = 6 * meteor.size;
      const normalX = -Math.sin(angle) * widthScale;
      const normalY = Math.cos(angle) * widthScale;
      const tailX = meteor.x - Math.cos(angle) * length * 0.76;
      const tailY = meteor.y - Math.sin(angle) * length * 0.76;

      const gradient = ctx.createLinearGradient(tailX, tailY, meteor.x, meteor.y);
      gradient.addColorStop(0, `hsla(${meteor.hue}, 100%, 68%, 0)`);
      gradient.addColorStop(0.7, `hsla(${meteor.hue}, 100%, 72%, ${0.2 * opacity})`);
      gradient.addColorStop(1, `hsla(${meteor.hue}, 100%, 88%, ${0.9 * opacity})`);

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.moveTo(meteor.x + normalX, meteor.y + normalY);
      ctx.lineTo(tailX, tailY);
      ctx.lineTo(meteor.x - normalX, meteor.y - normalY);
      ctx.closePath();
      ctx.fill();
    }

    function drawMeteorBody(meteor, opacity, angle) {
      ctx.shadowBlur = 34 * meteor.size;

      if (meteor.bodyShape === "comet") {
        ctx.shadowBlur = 42 * meteor.size;
        drawCometBody(meteor, opacity, angle);
      } else if (meteor.bodyShape === "double") {
        drawDoubleBody(meteor, opacity, angle);
      } else if (meteor.bodyShape === "star") {
        ctx.shadowBlur = 38 * meteor.size;
        drawStarBody(meteor, opacity, angle);
      } else if (meteor.bodyShape === "blade") {
        drawBladeBody(meteor, opacity, angle);
      } else {
        drawOvalBody(meteor, opacity, angle);
      }
    }

    function drawMeteorTailByShape(meteor, opacity, length, angle) {
      if (meteor.tailShape === "comet") {
        drawMeteorTail(meteor, opacity, length * 0.88, angle, 1.8);
      } else if (meteor.tailShape === "double") {
        drawMeteorTail(meteor, opacity, length, angle, 0.72, 5.2 * meteor.size);
        drawMeteorTail(meteor, opacity, length * 0.86, angle, 0.72, -5.2 * meteor.size);
      } else if (meteor.tailShape === "flare") {
        drawMeteorTail(meteor, opacity, length * 0.72, angle, 0.9);
        drawFlareTail(meteor, opacity, angle);
      } else if (meteor.tailShape === "blade") {
        drawBlade(meteor, opacity, length, angle);
      } else {
        drawMeteorTail(meteor, opacity, length, angle);
      }
    }

    function drawMeteor(meteor, delta) {
      meteor.age += delta;
      meteor.x += meteor.vx * delta;
      meteor.y += meteor.vy * delta;

      const progress = meteor.age / meteor.life;
      const opacity = Math.sin(Math.min(progress, 1) * Math.PI);
      const length = meteor.tail * (0.72 + opacity * 0.28);
      const angle = Math.atan2(meteor.vy, meteor.vx);

      ctx.save();
      ctx.lineCap = "round";
      ctx.shadowColor = meteor.glow;
      ctx.shadowBlur = 22 * meteor.size;

      drawMeteorTailByShape(meteor, opacity, length, angle);
      drawMeteorBody(meteor, opacity, angle);

      ctx.restore();
    }

    let lastTime = performance.now();

    function animate(now) {
      const delta = Math.min((now - lastTime) / 1000, 0.033);
      lastTime = now;

      if (!settings.paused) {
        simulationTime += delta * settings.timeSpeed;
      }

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
    pauseControl.addEventListener("click", () => {
      settings.paused = !settings.paused;
      pauseControl.textContent = settings.paused ? "继续" : "暂停";
    });
    resetTimeControl.addEventListener("click", () => {
      simulationTime = 0;
      planetTrails.clear();
      measurement.points = [];
      clearMeasurement();
    });
    scaleModeControl.addEventListener("change", () => {
      planetTrails.clear();
      updateDisplaySettings();
    });
    locateControl.addEventListener("click", () => {
      locateTarget(targetSelect.value, false);
    });
    focusControl.addEventListener("click", () => {
      if (settings.focusTarget === targetSelect.value) {
        setFocusTarget("");
      } else {
        locateTarget(targetSelect.value, true);
      }
    });
    targetSelect.addEventListener("change", () => {
      locateTarget(targetSelect.value, false);
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
      showStarsControl
    ].forEach((control) => {
      control.addEventListener("change", updateDisplaySettings);
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

    updateSetting(sizeControl, sizeValue, "size");
    updateSetting(speedControl, speedValue, "speed");
    updateTimeSetting();
    updateDisplaySettings();
    updateMagnifierSetting();
    updateShapeSetting(tailShapeInputs, tailShapeValue, tailShapeSummary, tailShapeNames, "tailShapes", "随机全部拖尾");
    updateShapeSetting(bodyShapeInputs, bodyShapeValue, bodyShapeSummary, bodyShapeNames, "bodyShapes", "随机全部本体");
    resize();
    requestAnimationFrame(animate);

