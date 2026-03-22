(() => {
  const container = document.getElementById("landingOrbContainer");
  if (!container) return;

  const colorPreset = {
    color1: [1.0, 1.0, 1.0],
    color2: [0.9, 0.95, 1.0],
    color3: [0.8, 0.9, 1.0],
    background: [0.02, 0.02, 0.05],
  };

  const settings = {
    animationSpeed: 1.25,
    waterStrength: 0.55,
    mouseIntensity: 1.15,
    clickIntensity: 2.5,
    damping: 0.913,
    impactForce: 42000,
    rippleSize: 0.085,
  };

  const waterSettings = {
    resolution: 192,
    damping: 0.913,
    tension: 0.02,
    rippleRadius: 7,
  };

  const resolution = waterSettings.resolution;
  const waterBuffers = {
    current: new Float32Array(resolution * resolution),
    previous: new Float32Array(resolution * resolution),
  };

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

    varying vec2 vUv;

    void main() {
      vec2 r = u_resolution;
      vec2 FC = gl_FragCoord.xy;
      vec2 screenP = (FC.xy * 2.0 - r) / max(r.y, 1.0);

      vec2 wCoord = vec2(FC.x / max(r.x, 1.0), FC.y / max(r.y, 1.0));
      float waterHeight = texture2D(u_waterTexture, wCoord).r;
      float waterInfluence = clamp(waterHeight * u_waterStrength, -0.6, 0.6);

      float circleRadius = 0.9 + waterInfluence * 0.28;
      float distFromCenter = length(screenP);
      float inCircle = smoothstep(circleRadius + 0.1, circleRadius - 0.1, distFromCenter);

      vec3 finalColor = u_background;
      if (inCircle > 0.0) {
        vec2 p = screenP * 1.1;
        float angle = length(p) * 4.0;
        mat2 R = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
        p *= R;

        float l = length(p) - 0.7 + waterInfluence * 0.42;
        float t = u_time * u_speed + waterInfluence * 1.7;
        float enhancedY = p.y + waterInfluence * 0.28;

        float pattern1 = 0.5 + 0.5 * tanh(0.1 / max(l / 0.1, -l) - sin(l + enhancedY * max(1.0, -l / 0.1) + t));
        float pattern2 = 0.5 + 0.5 * tanh(0.1 / max(l / 0.1, -l) - sin(l + enhancedY * max(1.0, -l / 0.1) + t + 1.0));
        float pattern3 = 0.5 + 0.5 * tanh(0.1 / max(l / 0.1, -l) - sin(l + enhancedY * max(1.0, -l / 0.1) + t + 2.0));

        vec3 orbColor = vec3(
          pattern1 * u_color1.r,
          pattern2 * u_color2.g,
          pattern3 * u_color3.b
        );
        float intensity = 1.0 + waterInfluence * 0.35;
        finalColor = mix(u_background, orbColor * intensity, inCircle);
      }

      gl_FragColor = vec4(finalColor, 1.0);
    }
  `;

  let disposed = false;
  let three = null;
  let scene = null;
  let camera = null;
  let renderer = null;
  let mesh = null;
  let material = null;
  let clock = null;
  let animationFrameId = 0;
  let mouseThrottleTime = 0;
  let resizeObserver = null;
  const lastPointerPosition = { x: 0, y: 0 };

  bindEvents();
  void initialize();

  async function initialize() {
    try {
      three = await import("https://esm.sh/three@0.177.0");
      if (disposed) return;
      buildRenderer();
      addCenterSplash();
      animate();
    } catch (error) {
      console.error(`[landing-orb] Failed to initialize renderer: ${error?.message || error}`);
    }
  }

  function bindEvents() {
    container.addEventListener("mousemove", onPointerMove, { passive: true });
    container.addEventListener("touchmove", onTouchMove, { passive: false });
    container.addEventListener("mousedown", onPointerDown, { passive: true });
    container.addEventListener("touchstart", onTouchStart, { passive: false });
    window.addEventListener("resize", onResize);
    window.addEventListener("beforeunload", dispose);

    if (typeof ResizeObserver !== "undefined") {
      resizeObserver = new ResizeObserver(() => {
        onResize();
      });
      resizeObserver.observe(container);
    }
  }

  function buildRenderer() {
    scene = new three.Scene();
    camera = new three.OrthographicCamera(-1, 1, 1, -1, 0.1, 10);
    camera.position.z = 1;

    renderer = new three.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    const { width, height } = getContainerSize();
    renderer.setSize(width, height, false);
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    renderer.domElement.style.display = "block";
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
        u_color1: { value: new three.Vector3(...colorPreset.color1) },
        u_color2: { value: new three.Vector3(...colorPreset.color2) },
        u_color3: { value: new three.Vector3(...colorPreset.color3) },
        u_background: { value: new three.Vector3(...colorPreset.background) },
        u_waterTexture: { value: waterTexture },
        u_waterStrength: { value: settings.waterStrength },
      },
    });

    mesh = new three.Mesh(new three.PlaneGeometry(2, 2), material);
    scene.add(mesh);
    clock = new three.Clock();
    centerLastPointerPosition();
  }

  function onPointerMove(event) {
    if (!renderer) return;
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
    event.preventDefault();
    const touch = event.touches[0];
    if (!touch) return;
    const rect = renderer.domElement.getBoundingClientRect();
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;
    addMouseTrail(x, y);
  }

  function onPointerDown(event) {
    if (!renderer || event.button !== 0) return;
    const rect = renderer.domElement.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    addRipple(x, y, settings.clickIntensity);
  }

  function onTouchStart(event) {
    if (!renderer) return;
    event.preventDefault();
    const touch = event.touches[0];
    if (!touch) return;
    const rect = renderer.domElement.getBoundingClientRect();
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;
    addRipple(x, y, settings.clickIntensity);
  }

  function addMouseTrail(x, y) {
    const dx = x - lastPointerPosition.x;
    const dy = y - lastPointerPosition.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    if (distance <= 1) return;

    const velocity = distance / 8;
    const velocityInfluence = Math.min(velocity / 10, 2.0);
    const baseIntensity = Math.min(distance / 20, 1.0);
    const finalIntensity = baseIntensity * velocityInfluence * settings.mouseIntensity;
    const jitterX = x + (Math.random() - 0.5) * 3;
    const jitterY = y + (Math.random() - 0.5) * 3;

    addRipple(jitterX, jitterY, finalIntensity);
    lastPointerPosition.x = x;
    lastPointerPosition.y = y;
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
        const distance = Math.sqrt(distanceSquared);
        const falloff = 1.0 - distance / Math.max(radius, 1);
        const rippleValue =
          Math.cos((distance / Math.max(radius, 1)) * Math.PI * 0.5) * rippleStrength * falloff;
        waterBuffers.previous[index] += rippleValue;
      }
    }
  }

  function addCenterSplash() {
    const rect = getCanvasRect();
    addRipple(rect.width / 2, rect.height / 2, 1.8);
  }

  function onResize() {
    if (!renderer || !material) return;
    const { width, height } = getContainerSize();
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
    const { current, previous } = waterBuffers;
    const { damping, resolution: gridSize } = waterSettings;
    const safeTension = Math.min(waterSettings.tension, 0.05);

    for (let i = 1; i < gridSize - 1; i += 1) {
      for (let j = 1; j < gridSize - 1; j += 1) {
        const index = i * gridSize + j;
        const top = previous[index - gridSize];
        const bottom = previous[index + gridSize];
        const left = previous[index - 1];
        const right = previous[index + 1];

        current[index] = (top + bottom + left + right) / 2 - current[index];
        current[index] = current[index] * damping + previous[index] * (1 - damping);
        current[index] += (0 - previous[index]) * safeTension;
        current[index] *= 1.0 - 0.01;
        current[index] = Math.max(-2.0, Math.min(2.0, current[index]));
      }
    }

    for (let i = 0; i < gridSize; i += 1) {
      current[i] = 0;
      current[(gridSize - 1) * gridSize + i] = 0;
      current[i * gridSize] = 0;
      current[i * gridSize + (gridSize - 1)] = 0;
    }

    [waterBuffers.current, waterBuffers.previous] = [waterBuffers.previous, waterBuffers.current];
    material.uniforms.u_waterTexture.value.image.data = waterBuffers.current;
    material.uniforms.u_waterTexture.value.needsUpdate = true;
  }

  function getContainerSize() {
    const rect = container.getBoundingClientRect();
    return {
      width: Math.max(1, Math.round(rect.width || container.clientWidth || 0)),
      height: Math.max(1, Math.round(rect.height || container.clientHeight || 0)),
    };
  }

  function getCanvasRect() {
    if (!renderer?.domElement) return getContainerSize();
    const rect = renderer.domElement.getBoundingClientRect();
    return {
      width: Math.max(1, rect.width),
      height: Math.max(1, rect.height),
    };
  }

  function centerLastPointerPosition() {
    const rect = getCanvasRect();
    lastPointerPosition.x = rect.width / 2;
    lastPointerPosition.y = rect.height / 2;
  }

  function dispose() {
    if (disposed) return;
    disposed = true;

    if (animationFrameId) {
      window.cancelAnimationFrame(animationFrameId);
    }

    container.removeEventListener("mousemove", onPointerMove);
    container.removeEventListener("touchmove", onTouchMove);
    container.removeEventListener("mousedown", onPointerDown);
    container.removeEventListener("touchstart", onTouchStart);
    window.removeEventListener("resize", onResize);
    window.removeEventListener("beforeunload", dispose);

    if (resizeObserver) {
      resizeObserver.disconnect();
      resizeObserver = null;
    }

    if (mesh) {
      mesh.geometry?.dispose?.();
      mesh.material?.dispose?.();
    }
    renderer?.dispose?.();

    if (renderer?.domElement && renderer.domElement.parentElement === container) {
      container.removeChild(renderer.domElement);
    }
  }
})();
