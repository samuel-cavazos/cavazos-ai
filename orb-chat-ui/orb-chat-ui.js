(() => {
  const container = document.getElementById("container");
  if (!container) return;

  const chatDock = document.getElementById("chatDock");
  const chatForm = document.getElementById("orbChatForm");
  const chatInput = document.getElementById("orbChatInput");
  const chatSend = document.getElementById("orbChatSend");
  const chatHint = document.getElementById("orbChatHint");
  const chatReply = document.getElementById("orbChatReply");
  const orbSpeech = document.getElementById("orbSpeech");
  const isOrbEmbedMode = new URLSearchParams(window.location.search).get("embed") === "orb";

  const SEND_ICON = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <path d="M4 12h16"></path>
  <path d="M14 7l6 5-6 5"></path>
</svg>`;

  let disposed = false;
  let three = null;
  let renderer = null;
  let scene = null;
  let camera = null;
  let mesh = null;
  let material = null;
  let clock = null;
  let animationFrameId = 0;
  let externalSubmitHandler = null;
  let lastMousePosition = { x: 0, y: 0 };
  let mouseThrottleTime = 0;

  const settings = {
    preset: "Ice White",
    animationSpeed: 1.3,
    waterStrength: 0.55,
    mouseIntensity: 1.2,
    clickIntensity: 3.0,
    rippleStrength: 0.5,
    damping: 0.913,
    impactForce: 50000,
    rippleSize: 0.1,
    swirlingMotion: 0.2,
    spiralIntensity: 0.2,
    motionDecay: 0.08,
    rippleDecay: 1.0,
    waveHeight: 0.01,
  };

  const colorPresets = {
    "Electric Blue": {
      color1: [0.0, 0.5, 1.0],
      color2: [0.0, 0.8, 1.0],
      color3: [0.2, 0.3, 1.0],
      background: [0.0, 0.05, 0.1],
    },
    "Neon Pink": {
      color1: [1.0, 0.0, 0.5],
      color2: [1.0, 0.3, 0.7],
      color3: [0.9, 0.1, 0.6],
      background: [0.1, 0.0, 0.05],
    },
    "Ice White": {
      color1: [1.0, 1.0, 1.0],
      color2: [0.9, 0.95, 1.0],
      color3: [0.8, 0.9, 1.0],
      background: [0.02, 0.02, 0.05],
    },
  };

  const waterSettings = {
    resolution: 256,
    damping: 0.913,
    tension: 0.02,
    rippleRadius: 8,
  };

  const resolution = waterSettings.resolution;
  const waterBuffers = {
    current: new Float32Array(resolution * resolution),
    previous: new Float32Array(resolution * resolution),
    velocity: new Float32Array(resolution * resolution * 2),
    vorticity: new Float32Array(resolution * resolution),
  };

  for (let i = 0; i < resolution * resolution; i += 1) {
    waterBuffers.current[i] = 0.0;
    waterBuffers.previous[i] = 0.0;
    waterBuffers.velocity[i * 2] = 0.0;
    waterBuffers.velocity[i * 2 + 1] = 0.0;
    waterBuffers.vorticity[i] = 0.0;
  }

  const vertexShader = `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `;

  const fragmentShader = `
    uniform float u_time;
    uniform vec2 u_resolution;
    uniform vec3 u_color1;
    uniform vec3 u_color2;
    uniform vec3 u_color3;
    uniform vec3 u_background;
    uniform float u_speed;
    uniform sampler2D u_waterTexture;
    uniform float u_waterStrength;
    uniform float u_ripple_time;
    uniform vec2 u_ripple_position;
    uniform float u_ripple_strength;

    varying vec2 vUv;

    void main() {
      vec2 r = u_resolution;
      vec2 FC = gl_FragCoord.xy;
      vec2 screenP = (FC.xy * 2.0 - r) / r.y;

      vec2 wCoord = vec2(FC.x / r.x, FC.y / r.y);
      float waterHeight = texture2D(u_waterTexture, wCoord).r;
      float waterInfluence = clamp(waterHeight * u_waterStrength, -0.5, 0.5);

      float circleRadius = 0.9 + waterInfluence * 0.3;
      float distFromCenter = length(screenP);
      float inCircle = smoothstep(circleRadius + 0.1, circleRadius - 0.1, distFromCenter);

      vec4 o = vec4(0.0);
      if (inCircle > 0.0) {
        vec2 p = screenP * 1.1;

        float rippleTime = u_time - u_ripple_time;
        vec2 ripplePos = u_ripple_position * r;
        float rippleDist = distance(FC.xy, ripplePos);

        float clickRipple = 0.0;
        if (rippleTime < 3.0 && rippleTime > 0.0) {
          float rippleRadius = rippleTime * 150.0;
          float rippleWidth = 30.0;
          float rippleDecay = 1.0 - rippleTime / 3.0;
          clickRipple = exp(-abs(rippleDist - rippleRadius) / rippleWidth) * rippleDecay * u_ripple_strength;
        }

        float totalWaterInfluence = clamp((waterInfluence + clickRipple * 0.1) * u_waterStrength, -0.8, 0.8);

        float angle = length(p) * 4.0;
        mat2 R = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
        p *= R;

        float l = length(p) - 0.7 + totalWaterInfluence * 0.5;
        float t = u_time * u_speed + totalWaterInfluence * 2.0;
        float enhancedY = p.y + totalWaterInfluence * 0.3;

        float pattern1 = 0.5 + 0.5 * tanh(0.1 / max(l / 0.1, -l) - sin(l + enhancedY * max(1.0, -l / 0.1) + t));
        float pattern2 = 0.5 + 0.5 * tanh(0.1 / max(l / 0.1, -l) - sin(l + enhancedY * max(1.0, -l / 0.1) + t + 1.0));
        float pattern3 = 0.5 + 0.5 * tanh(0.1 / max(l / 0.1, -l) - sin(l + enhancedY * max(1.0, -l / 0.1) + t + 2.0));

        float intensity = 1.0 + totalWaterInfluence * 0.5;
        o.r = pattern1 * u_color1.r * intensity;
        o.g = pattern2 * u_color2.g * intensity;
        o.b = pattern3 * u_color3.b * intensity;
        o.a = inCircle;
      }

      vec3 finalColor = mix(u_background, o.rgb, o.a);
      gl_FragColor = vec4(finalColor, 1.0);
    }
  `;

  if (isOrbEmbedMode) {
    if (chatDock) {
      chatDock.style.display = "none";
      chatDock.setAttribute("aria-hidden", "true");
    }
    if (chatReply) {
      chatReply.textContent = "";
      chatReply.dataset.state = "";
    }
    if (orbSpeech) {
      orbSpeech.style.display = "none";
      orbSpeech.textContent = "";
      orbSpeech.dataset.state = "";
      orbSpeech.setAttribute("aria-hidden", "true");
    }
  }

  bindEvents();
  void initialize();

  async function initialize() {
    updateComposerActionButton();
    try {
      three = await import("https://esm.sh/three@0.177.0");
      if (disposed) return;
      buildRenderer();
      applyPreset(settings.preset);
      addCenterSplash();
      animate();
      setSpeech("", false);
    } catch (error) {
      console.error(`[orb-chat-ui] Failed to initialize renderer: ${error?.message || error}`);
      setSpeech("WebGL renderer failed to load.", true);
    }
  }

  function bindEvents() {
    window.addEventListener("mousemove", onPointerMove, { passive: true });
    window.addEventListener("touchmove", onTouchMove, { passive: false });
    window.addEventListener("mousedown", onPointerDown, { passive: true });
    window.addEventListener("touchstart", onTouchStart, { passive: false });
    window.addEventListener("resize", onResize);
    window.addEventListener("orientationchange", onResize);
    if (window.visualViewport) {
      window.visualViewport.addEventListener("resize", onResize);
      window.visualViewport.addEventListener("scroll", onResize);
    }
    chatForm?.addEventListener("submit", onChatSubmit);
    window.addEventListener("beforeunload", dispose);
  }

  function buildRenderer() {
    scene = new three.Scene();
    camera = new three.OrthographicCamera(-1, 1, 1, -1, 0.1, 10);
    camera.position.z = 1;

    renderer = new three.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    const { width, height } = getViewportSize();
    renderer.setSize(width, height, false);
    container.appendChild(renderer.domElement);

    const waterTexture = new three.DataTexture(
      waterBuffers.current,
      waterSettings.resolution,
      waterSettings.resolution,
      three.RedFormat,
      three.FloatType
    );
    waterTexture.minFilter = three.LinearFilter;
    waterTexture.magFilter = three.LinearFilter;
    waterTexture.needsUpdate = true;

    material = new three.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: {
        u_time: { value: 0.0 },
        u_resolution: { value: new three.Vector2(renderer.domElement.width, renderer.domElement.height) },
        u_speed: { value: settings.animationSpeed },
        u_color1: { value: new three.Vector3(1.0, 1.0, 1.0) },
        u_color2: { value: new three.Vector3(0.9, 0.95, 1.0) },
        u_color3: { value: new three.Vector3(0.8, 0.9, 1.0) },
        u_background: { value: new three.Vector3(0.02, 0.02, 0.05) },
        u_waterTexture: { value: waterTexture },
        u_waterStrength: { value: settings.waterStrength },
        u_ripple_time: { value: -10.0 },
        u_ripple_position: { value: new three.Vector2(0.5, 0.5) },
        u_ripple_strength: { value: settings.rippleStrength },
      },
    });

    mesh = new three.Mesh(new three.PlaneGeometry(2, 2), material);
    scene.add(mesh);
    clock = new three.Clock();
    centerLastPointerPosition();
  }

  function onPointerMove(event) {
    if (!renderer) return;
    if (isEventInsideChatDock(event)) return;
    const now = performance.now();
    if (now - mouseThrottleTime < 8) return;
    mouseThrottleTime = now;

    const rect = renderer.domElement.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    addMouseTrail(x, y);
  }

  function onTouchMove(event) {
    if (!renderer) return;
    if (isEventInsideChatDock(event)) return;
    event.preventDefault();
    const touch = event.touches[0];
    if (!touch) return;
    const rect = renderer.domElement.getBoundingClientRect();
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;
    addMouseTrail(x, y);
  }

  function addMouseTrail(x, y) {
    const dx = x - lastMousePosition.x;
    const dy = y - lastMousePosition.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const velocity = distance / 8;
    if (distance <= 1) return;

    const velocityInfluence = Math.min(velocity / 10, 2.0);
    const baseIntensity = Math.min(distance / 20, 1.0);
    const fluidIntensity = baseIntensity * velocityInfluence * settings.mouseIntensity;
    const variation = Math.random() * 0.3 + 0.7;
    const finalIntensity = fluidIntensity * variation;
    const jitterX = x + (Math.random() - 0.5) * 3;
    const jitterY = y + (Math.random() - 0.5) * 3;
    addRipple(jitterX, jitterY, finalIntensity);
    lastMousePosition.x = x;
    lastMousePosition.y = y;
  }

  function onPointerDown(event) {
    if (!renderer || event.button !== 0) return;
    if (isEventInsideChatDock(event)) return;
    const rect = renderer.domElement.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    addClickRipple(x, y);
  }

  function onTouchStart(event) {
    if (!renderer) return;
    if (isEventInsideChatDock(event)) return;
    event.preventDefault();
    const touch = event.touches[0];
    if (!touch) return;
    const rect = renderer.domElement.getBoundingClientRect();
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;
    addClickRipple(x, y);
  }

  function isEventInsideChatDock(event) {
    if (!chatDock) return false;
    const target = event?.target;
    return Boolean(target instanceof Node && chatDock.contains(target));
  }

  async function onChatSubmit(event) {
    event.preventDefault();
    if (!chatInput) return;

    const prompt = String(chatInput.value || "").trim();
    if (!prompt) return;

    const rect = getCanvasRect();
    addClickRipple(rect.width / 2, rect.height / 2);

    const api = {
      prompt,
      setSpeech,
      setReply,
      setBusy,
      setHint,
      clearInput: () => {
        if (!chatInput) return;
        chatInput.value = "";
      },
      focusInput: () => {
        chatInput?.focus();
      },
    };

    window.dispatchEvent(new CustomEvent("orb-chat-ui:submit", { detail: api }));

    if (typeof externalSubmitHandler === "function") {
      await Promise.resolve(externalSubmitHandler(api));
      return;
    }

    setSpeech(`You said: ${prompt}`);
    if (chatInput) {
      chatInput.value = "";
      chatInput.focus();
    }
  }

  function setSpeech(text, isError = false) {
    const normalized = String(text || "").replace(/\s+/g, " ").trim();

    if (!normalized) {
      if (chatReply) {
        chatReply.textContent = "";
        chatReply.dataset.state = "";
      }
      if (orbSpeech) {
        orbSpeech.textContent = "";
        orbSpeech.dataset.state = "";
      }
      return;
    }

    if (chatReply) {
      chatReply.textContent = normalized;
      chatReply.dataset.state = isError ? "error" : "ok";
    }

    if (orbSpeech) {
      orbSpeech.textContent = "";
      const speechText = document.createElement("span");
      speechText.className = "orb-speech-text";
      speechText.textContent = normalized;
      orbSpeech.appendChild(speechText);
      orbSpeech.dataset.state = isError ? "error" : "ok";
      orbSpeech.scrollTop = 0;
    }
  }

  function setReply(text, isError = false) {
    setSpeech(text, isError);
  }

  function setHint(text) {
    if (!chatHint) return;
    chatHint.textContent = String(text || "").trim();
  }

  function setBusy(value) {
    const busy = Boolean(value);
    if (chatForm) {
      chatForm.setAttribute("aria-busy", busy ? "true" : "false");
      chatForm.classList.toggle("is-busy", busy);
    }
    if (chatInput) {
      chatInput.disabled = busy;
    }
    if (chatSend) {
      chatSend.disabled = busy;
    }
  }

  function updateComposerActionButton() {
    if (!chatSend) return;
    chatSend.innerHTML = SEND_ICON;
    chatSend.dataset.mode = "send";
    chatSend.setAttribute("aria-label", "Send");
    chatSend.setAttribute("title", "Send");
  }

  function onResize() {
    if (!renderer || !material) return;
    const { width, height } = getViewportSize();
    renderer.setSize(width, height, false);
    material.uniforms.u_resolution.value.set(renderer.domElement.width, renderer.domElement.height);
    centerLastPointerPosition();
  }

  function animate() {
    if (disposed || !renderer || !material || !clock) return;
    animationFrameId = window.requestAnimationFrame(animate);
    material.uniforms.u_time.value = clock.getElapsedTime();
    updateWaterSimulation();
    renderer.render(scene, camera);
  }

  function updateWaterSimulation() {
    const { current, previous, velocity, vorticity } = waterBuffers;
    const { damping, resolution: gridSize } = waterSettings;
    const safeTension = Math.min(waterSettings.tension, 0.05);
    const velocityDissipation = settings.motionDecay;
    const densityDissipation = settings.rippleDecay;
    const vorticityInfluence = Math.min(Math.max(settings.swirlingMotion, 0.0), 0.5);

    for (let i = 0; i < gridSize * gridSize * 2; i += 1) {
      velocity[i] *= 1.0 - velocityDissipation;
    }

    for (let i = 1; i < gridSize - 1; i += 1) {
      for (let j = 1; j < gridSize - 1; j += 1) {
        const index = i * gridSize + j;
        const left = velocity[(index - 1) * 2 + 1];
        const right = velocity[(index + 1) * 2 + 1];
        const bottom = velocity[(index - gridSize) * 2];
        const top = velocity[(index + gridSize) * 2];
        vorticity[index] = (right - left - (top - bottom)) * 0.5;
      }
    }

    if (vorticityInfluence > 0.001) {
      for (let i = 1; i < gridSize - 1; i += 1) {
        for (let j = 1; j < gridSize - 1; j += 1) {
          const index = i * gridSize + j;
          const velIndex = index * 2;
          const left = Math.abs(vorticity[index - 1]);
          const right = Math.abs(vorticity[index + 1]);
          const bottom = Math.abs(vorticity[index - gridSize]);
          const top = Math.abs(vorticity[index + gridSize]);
          const gradX = (right - left) * 0.5;
          const gradY = (top - bottom) * 0.5;
          const length = Math.sqrt(gradX * gradX + gradY * gradY) + 1e-5;
          const safeVorticity = Math.max(-1.0, Math.min(1.0, vorticity[index]));
          const forceX = (gradY / length) * safeVorticity * vorticityInfluence * 0.1;
          const forceY = (-gradX / length) * safeVorticity * vorticityInfluence * 0.1;
          velocity[velIndex] += Math.max(-0.1, Math.min(0.1, forceX));
          velocity[velIndex + 1] += Math.max(-0.1, Math.min(0.1, forceY));
        }
      }
    }

    for (let i = 1; i < gridSize - 1; i += 1) {
      for (let j = 1; j < gridSize - 1; j += 1) {
        const index = i * gridSize + j;
        const velIndex = index * 2;
        const top = previous[index - gridSize];
        const bottom = previous[index + gridSize];
        const left = previous[index - 1];
        const right = previous[index + 1];
        current[index] = (top + bottom + left + right) / 2 - current[index];
        current[index] = current[index] * damping + previous[index] * (1 - damping);
        current[index] += (0 - previous[index]) * safeTension;

        const velMagnitude = Math.sqrt(
          velocity[velIndex] * velocity[velIndex] + velocity[velIndex + 1] * velocity[velIndex + 1]
        );
        const safeVelInfluence = Math.min(velMagnitude * settings.waveHeight, 0.1);
        current[index] += safeVelInfluence;
        current[index] *= 1.0 - densityDissipation * 0.01;
        current[index] = Math.max(-2.0, Math.min(2.0, current[index]));
      }
    }

    for (let i = 0; i < gridSize; i += 1) {
      current[i] = 0;
      current[(gridSize - 1) * gridSize + i] = 0;
      velocity[i * 2] = 0;
      velocity[i * 2 + 1] = 0;
      velocity[((gridSize - 1) * gridSize + i) * 2] = 0;
      velocity[((gridSize - 1) * gridSize + i) * 2 + 1] = 0;

      current[i * gridSize] = 0;
      current[i * gridSize + (gridSize - 1)] = 0;
      velocity[i * gridSize * 2] = 0;
      velocity[i * gridSize * 2 + 1] = 0;
      velocity[(i * gridSize + (gridSize - 1)) * 2] = 0;
      velocity[(i * gridSize + (gridSize - 1)) * 2 + 1] = 0;
    }

    [waterBuffers.current, waterBuffers.previous] = [waterBuffers.previous, waterBuffers.current];
    material.uniforms.u_waterTexture.value.image.data = waterBuffers.current;
    material.uniforms.u_waterTexture.value.needsUpdate = true;
  }

  function addRipple(x, y, strength = 1.0) {
    const { resolution: gridSize, rippleRadius } = waterSettings;
    const rect = getCanvasRect();
    const normalizedX = x / Math.max(rect.width, 1);
    const normalizedY = 1.0 - y / Math.max(rect.height, 1);
    const texX = Math.floor(normalizedX * gridSize);
    const texY = Math.floor(normalizedY * gridSize);
    const radius = Math.max(rippleRadius, Math.floor(settings.rippleSize * gridSize));
    const rippleStrength = strength * (settings.impactForce / 100000);
    const radiusSquared = radius * radius;

    for (let i = -radius; i <= radius; i += 1) {
      for (let j = -radius; j <= radius; j += 1) {
        const distanceSquared = i * i + j * j;
        if (distanceSquared > radiusSquared) continue;

        const posX = texX + i;
        const posY = texY + j;
        if (posX < 0 || posX >= gridSize || posY < 0 || posY >= gridSize) continue;

        const index = posY * gridSize + posX;
        const velIndex = index * 2;
        const distance = Math.sqrt(distanceSquared);
        const falloff = 1.0 - distance / Math.max(radius, 1);
        const rippleValue =
          Math.cos((distance / Math.max(radius, 1)) * Math.PI * 0.5) * rippleStrength * falloff;

        waterBuffers.previous[index] += rippleValue;
        const angle = Math.atan2(j, i);
        const velocityStrength = rippleValue * settings.spiralIntensity;
        waterBuffers.velocity[velIndex] += Math.cos(angle) * velocityStrength;
        waterBuffers.velocity[velIndex + 1] += Math.sin(angle) * velocityStrength;
        const swirlAngle = angle + Math.PI * 0.5;
        const swirlStrength = Math.min(velocityStrength * 0.3, 0.1);
        waterBuffers.velocity[velIndex] += Math.cos(swirlAngle) * swirlStrength;
        waterBuffers.velocity[velIndex + 1] += Math.sin(swirlAngle) * swirlStrength;
      }
    }
  }

  function addClickRipple(x, y) {
    addRipple(x, y, settings.clickIntensity);
    if (!material || !clock) return;
    const rect = getCanvasRect();
    const clickX = x / Math.max(rect.width, 1);
    const clickY = 1.0 - y / Math.max(rect.height, 1);
    material.uniforms.u_ripple_position.value.set(clickX, clickY);
    material.uniforms.u_ripple_time.value = clock.getElapsedTime();
  }

  function addCenterSplash() {
    const rect = getCanvasRect();
    const x = rect.width / 2;
    const y = rect.height / 2;
    addRipple(x, y, 1.5);
    addClickRipple(x, y);
  }

  function applyPreset(name) {
    const preset = colorPresets[name] || colorPresets["Ice White"];
    if (!material || !three) return;
    material.uniforms.u_color1.value.fromArray(preset.color1);
    material.uniforms.u_color2.value.fromArray(preset.color2);
    material.uniforms.u_color3.value.fromArray(preset.color3);
    material.uniforms.u_background.value.fromArray(preset.background);
    material.uniforms.u_speed.value = settings.animationSpeed;
    material.uniforms.u_waterStrength.value = settings.waterStrength;
    material.uniforms.u_ripple_strength.value = settings.rippleStrength;
  }

  function dispose() {
    if (disposed) return;
    disposed = true;

    if (animationFrameId) {
      window.cancelAnimationFrame(animationFrameId);
    }

    window.removeEventListener("mousemove", onPointerMove);
    window.removeEventListener("touchmove", onTouchMove);
    window.removeEventListener("mousedown", onPointerDown);
    window.removeEventListener("touchstart", onTouchStart);
    window.removeEventListener("resize", onResize);
    window.removeEventListener("orientationchange", onResize);
    if (window.visualViewport) {
      window.visualViewport.removeEventListener("resize", onResize);
      window.visualViewport.removeEventListener("scroll", onResize);
    }
    window.removeEventListener("beforeunload", dispose);
    chatForm?.removeEventListener("submit", onChatSubmit);

    if (mesh) {
      mesh.geometry?.dispose?.();
      mesh.material?.dispose?.();
    }
    renderer?.dispose?.();

    if (renderer?.domElement && renderer.domElement.parentElement === container) {
      container.removeChild(renderer.domElement);
    }
  }

  function getCanvasRect() {
    if (!renderer?.domElement) {
      const { width, height } = getViewportSize();
      return { width, height };
    }
    const rect = renderer.domElement.getBoundingClientRect();
    return {
      width: Math.max(1, rect.width),
      height: Math.max(1, rect.height),
    };
  }

  function getViewportSize() {
    const vv = window.visualViewport;
    if (vv && Number.isFinite(vv.width) && Number.isFinite(vv.height)) {
      return {
        width: Math.max(1, Math.round(vv.width)),
        height: Math.max(1, Math.round(vv.height)),
      };
    }
    return {
      width: Math.max(1, Math.round(window.innerWidth || 0)),
      height: Math.max(1, Math.round(window.innerHeight || 0)),
    };
  }

  function centerLastPointerPosition() {
    const rect = getCanvasRect();
    lastMousePosition.x = rect.width / 2;
    lastMousePosition.y = rect.height / 2;
  }

  window.OrbChatUI = {
    setSubmitHandler(handler) {
      externalSubmitHandler = typeof handler === "function" ? handler : null;
    },
    setSpeech,
    setReply,
    setHint,
    setBusy,
    setPreset(name) {
      applyPreset(name);
    },
    dispose,
  };
})();
