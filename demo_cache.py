"""
Demo Cache — Pre-built responses for instant demo showcases.
Features SVG diagram code for Fourier Transform, Taylor Series, and Newton's Laws.
"""


def get_cached_response(query: str) -> dict | None:
    query_lower = query.lower().strip()
    for keywords, response in DEMO_CACHE.items():
        if any(kw in query_lower for kw in keywords):
            return response
    return None


# ── SVG Diagram Code Constants ──────────────────────────────────────

FOURIER_SVG = '''<svg viewBox="0 0 650 320" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Inter, Arial, sans-serif">
  <rect width="650" height="320" rx="12" fill="#ffffff"/>
  <defs>
    <marker id="ah" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#1a1a2e"/></marker>
  </defs>
  <!-- Time Domain -->
  <text x="140" y="30" text-anchor="middle" font-size="14" font-weight="600" fill="#1a1a2e">Time Domain</text>
  <line x1="30" y1="160" x2="270" y2="160" stroke="#1a1a2e" stroke-width="1.5" marker-end="url(#ah)"/>
  <line x1="40" y1="260" x2="40" y2="60" stroke="#1a1a2e" stroke-width="1.5" marker-end="url(#ah)"/>
  <text x="265" y="178" font-size="11" fill="#1a1a2e">t</text>
  <text x="25" y="68" font-size="11" fill="#1a1a2e">f(t)</text>
  <path d="M50,160 Q80,80 110,160 Q140,240 170,160 Q200,80 230,160" stroke="#3b82f6" stroke-width="2.5" fill="none"/>
  <text x="140" y="290" text-anchor="middle" font-size="11" fill="#6b7280">Complex signal</text>
  <!-- Arrow -->
  <text x="325" y="140" text-anchor="middle" font-size="28" fill="#3b82f6">⟹</text>
  <text x="325" y="170" text-anchor="middle" font-size="12" font-weight="600" fill="#3b82f6">FT</text>
  <!-- Frequency Domain -->
  <text x="510" y="30" text-anchor="middle" font-size="14" font-weight="600" fill="#1a1a2e">Frequency Domain</text>
  <line x1="390" y1="250" x2="630" y2="250" stroke="#1a1a2e" stroke-width="1.5" marker-end="url(#ah)"/>
  <line x1="400" y1="260" x2="400" y2="60" stroke="#1a1a2e" stroke-width="1.5" marker-end="url(#ah)"/>
  <text x="625" y="268" font-size="11" fill="#1a1a2e">ω</text>
  <text x="385" y="68" font-size="11" fill="#1a1a2e">|F(ω)|</text>
  <rect x="430" y="100" width="28" height="150" rx="4" fill="#3b82f6" opacity="0.85"/>
  <rect x="480" y="150" width="28" height="100" rx="4" fill="#3b82f6" opacity="0.65"/>
  <rect x="530" y="190" width="28" height="60" rx="4" fill="#3b82f6" opacity="0.45"/>
  <rect x="580" y="215" width="28" height="35" rx="4" fill="#3b82f6" opacity="0.3"/>
  <text x="444" y="268" font-size="10" fill="#1a1a2e">f₁</text>
  <text x="494" y="268" font-size="10" fill="#1a1a2e">f₂</text>
  <text x="544" y="268" font-size="10" fill="#1a1a2e">f₃</text>
  <text x="594" y="268" font-size="10" fill="#1a1a2e">f₄</text>
  <text x="510" y="290" text-anchor="middle" font-size="11" fill="#6b7280">Frequency components</text>
</svg>'''

TAYLOR_SVG = '''<svg viewBox="0 0 650 340" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Inter, Arial, sans-serif">
  <rect width="650" height="340" rx="12" fill="#ffffff"/>
  <defs>
    <marker id="ah2" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#1a1a2e"/></marker>
  </defs>
  <text x="325" y="28" text-anchor="middle" font-size="15" font-weight="700" fill="#1a1a2e">Taylor Series Approximation of f(x)</text>
  <!-- Axes -->
  <line x1="60" y1="260" x2="600" y2="260" stroke="#1a1a2e" stroke-width="1.5" marker-end="url(#ah2)"/>
  <line x1="80" y1="300" x2="80" y2="50" stroke="#1a1a2e" stroke-width="1.5" marker-end="url(#ah2)"/>
  <text x="595" y="278" font-size="12" fill="#1a1a2e">x</text>
  <text x="65" y="58" font-size="12" fill="#1a1a2e">y</text>
  <!-- Original function curve -->
  <path d="M100,220 Q200,40 350,140 Q500,240 580,80" stroke="#1a1a2e" stroke-width="2.5" fill="none"/>
  <!-- n=1 linear -->
  <line x1="100" y1="250" x2="550" y2="100" stroke="#ef4444" stroke-width="1.8" stroke-dasharray="8,4" opacity="0.7"/>
  <!-- n=2 quadratic -->
  <path d="M100,240 Q300,60 550,110" stroke="#f59e0b" stroke-width="1.8" stroke-dasharray="6,3" fill="none" opacity="0.7"/>
  <!-- n=4 closer -->
  <path d="M100,222 Q200,45 350,138 Q450,210 550,95" stroke="#3b82f6" stroke-width="2" fill="none" opacity="0.8"/>
  <!-- Expansion point -->
  <circle cx="200" cy="130" r="6" fill="#3b82f6" stroke="#1a1a2e" stroke-width="1.5"/>
  <text x="212" y="122" font-size="11" font-weight="600" fill="#3b82f6">a (center)</text>
  <!-- Legend -->
  <rect x="400" y="280" width="230" height="52" rx="6" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
  <line x1="412" y1="296" x2="440" y2="296" stroke="#1a1a2e" stroke-width="2.5"/>
  <text x="448" y="300" font-size="10" fill="#1a1a2e">f(x) original</text>
  <line x1="412" y1="314" x2="440" y2="314" stroke="#ef4444" stroke-width="1.8" stroke-dasharray="8,4"/>
  <text x="448" y="318" font-size="10" fill="#ef4444">n=1</text>
  <line x1="498" y1="314" x2="526" y2="314" stroke="#f59e0b" stroke-width="1.8" stroke-dasharray="6,3"/>
  <text x="534" y="318" font-size="10" fill="#f59e0b">n=2</text>
  <line x1="568" y1="314" x2="596" y2="314" stroke="#3b82f6" stroke-width="2"/>
  <text x="604" y="318" font-size="10" fill="#3b82f6">n=4</text>
</svg>'''

NEWTON_SVG = '''<svg viewBox="0 0 650 380" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Inter, Arial, sans-serif">
  <rect width="650" height="380" rx="12" fill="#ffffff"/>
  <defs>
    <marker id="ah3" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#3b82f6"/></marker>
    <marker id="ah3r" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#ef4444"/></marker>
  </defs>
  <text x="325" y="28" text-anchor="middle" font-size="15" font-weight="700" fill="#1a1a2e">Newton&#39;s Three Laws of Motion</text>
  <!-- Law 1: Inertia -->
  <rect x="20" y="50" width="190" height="100" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="115" y="72" text-anchor="middle" font-size="12" font-weight="700" fill="#1a1a2e">1st Law: Inertia</text>
  <circle cx="60" cy="110" r="10" fill="#3b82f6"/>
  <line x1="75" y1="110" x2="130" y2="110" stroke="#3b82f6" stroke-width="2" stroke-dasharray="6,3"/>
  <circle cx="150" cy="110" r="10" fill="#3b82f6" opacity="0.5"/>
  <text x="115" y="140" text-anchor="middle" font-size="10" fill="#6b7280">No force → constant velocity</text>
  <!-- Law 2: F=ma -->
  <rect x="230" y="50" width="190" height="100" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="325" y="72" text-anchor="middle" font-size="12" font-weight="700" fill="#1a1a2e">2nd Law: F = ma</text>
  <text x="325" y="105" text-anchor="middle" font-size="22" font-weight="700" fill="#3b82f6">F = ma</text>
  <text x="325" y="140" text-anchor="middle" font-size="10" fill="#6b7280">Force = mass × acceleration</text>
  <!-- Law 3: Action-Reaction -->
  <rect x="440" y="50" width="190" height="100" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="535" y="72" text-anchor="middle" font-size="12" font-weight="700" fill="#1a1a2e">3rd Law: Action-Reaction</text>
  <circle cx="500" cy="112" r="12" fill="#3b82f6"/>
  <circle cx="570" cy="112" r="12" fill="#ef4444"/>
  <line x1="515" y1="108" x2="555" y2="108" stroke="#3b82f6" stroke-width="2" marker-end="url(#ah3)"/>
  <line x1="555" y1="116" x2="515" y2="116" stroke="#ef4444" stroke-width="2" marker-end="url(#ah3r)"/>
  <text x="535" y="140" text-anchor="middle" font-size="10" fill="#6b7280">Equal and opposite forces</text>
  <!-- Force diagram below -->
  <text x="325" y="185" text-anchor="middle" font-size="13" font-weight="600" fill="#1a1a2e">Free Body Diagram</text>
  <rect x="260" y="250" width="130" height="60" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="325" y="285" text-anchor="middle" font-size="12" font-weight="600" fill="#1a1a2e">Mass (m)</text>
  <line x1="325" y1="250" x2="325" y2="200" stroke="#3b82f6" stroke-width="2.5" marker-end="url(#ah3)"/>
  <text x="340" y="215" font-size="11" font-weight="600" fill="#3b82f6">N (Normal)</text>
  <line x1="325" y1="310" x2="325" y2="360" stroke="#ef4444" stroke-width="2.5" marker-end="url(#ah3r)"/>
  <text x="340" y="350" font-size="11" font-weight="600" fill="#ef4444">mg (Weight)</text>
  <line x1="390" y1="280" x2="450" y2="280" stroke="#3b82f6" stroke-width="2.5" marker-end="url(#ah3)"/>
  <text x="430" y="270" font-size="11" font-weight="600" fill="#3b82f6">F (Applied)</text>
  <line x1="260" y1="280" x2="200" y2="280" stroke="#f59e0b" stroke-width="2.5" marker-end="url(#ah3)"/>
  <text x="215" y="270" font-size="11" font-weight="600" fill="#f59e0b">f (Friction)</text>
</svg>'''

# ── Demo Cache ──────────────────────────────────────────────────────

DEMO_CACHE = {
    ("fourier", "fourier transform"): {
        "synthesized": """## 🧠 Concept

The **Fourier Transform** is one of the most elegant ideas in mathematics — and it's hiding in plain sight everywhere around you. Think of it as a **musical prism**.

When white light passes through a glass prism, it separates into individual colors (frequencies of light). The Fourier Transform does exactly the same thing, but for *any* signal — sound, images, radio waves, even stock prices.

**Here's the intuition:** Imagine you're at a concert listening to an orchestra. Your ears receive one combined sound wave — a messy, complicated signal. But somehow, your brain can pick out the violin, the drums, the flute. The Fourier Transform is the *mathematical version* of what your brain does: it takes a complex signal and reveals the individual frequencies hiding inside it.

**Why does this matter?** It's the backbone of modern technology:
- **MP3/Spotify** compresses music by keeping only the frequencies you can hear
- **JPEG** compresses images using a 2D version (DCT)
- **MRI machines** reconstruct body images from frequency data
- **Your phone** uses it constantly for signal processing

**Key insight:** Any signal, no matter how chaotic, is secretly just a combination of simple sine waves — and the Fourier Transform reveals the recipe.

## 📐 Math

### Step-by-Step Mathematical Derivation

**Step 1: Define the Continuous Fourier Transform**

$$F(\\omega) = \\int_{-\\infty}^{\\infty} f(t) \\cdot e^{-j\\omega t} \\, dt$$

where $F(\\omega)$ = frequency-domain representation, $f(t)$ = time-domain signal, $\\omega = 2\\pi f$ = angular frequency.

This integral essentially "tests" how much of each frequency $\\omega$ is present in the signal $f(t)$.

**Step 2: Euler's Formula — The Bridge**

$e^{-j\\omega t} = \\cos(\\omega t) - j\\sin(\\omega t)$

This tells us the transform computes the correlation between $f(t)$ and sinusoids at every frequency — it's literally asking "how much does my signal look like a sine wave at frequency $\\omega$?"

**Step 3: The Inverse Transform — Going Back**

$$f(t) = \\frac{1}{2\\pi} \\int_{-\\infty}^{\\infty} F(\\omega) \\cdot e^{j\\omega t} \\, d\\omega$$

This confirms the transform is *reversible* — no information is lost.

**Step 4: Key Properties**
- **Linearity**: $\\mathcal{F}\\{af + bg\\} = aF + bG$
- **Convolution Theorem**: $\\mathcal{F}\\{f * g\\} = F \\cdot G$ — convolution in time becomes simple multiplication in frequency

**Step 5: Discrete Fourier Transform (DFT)**

For N samples: $X[k] = \\sum_{n=0}^{N-1} x[n] \\cdot e^{-j2\\pi kn/N}$

This is the computational version used by all digital systems (via the FFT algorithm).

## 🎨 Visual

The diagram illustrates the core transformation visually. On the **left**, you see a complex, oscillating waveform in the time domain — this represents the raw signal as it unfolds over time. The **right side** shows the frequency domain: a series of bars at different frequencies ($f_1$ through $f_4$), each representing a pure sine wave component hidden within the original signal.

The large **FT arrow** connecting them represents the Fourier Transform operation — the mathematical prism that separates the signal into its frequency ingredients. Notice how the tallest bar ($f_1$) indicates the dominant frequency, while shorter bars show weaker components.

## ✅ Final Understanding

The Fourier Transform reveals that **every complex signal is secretly a recipe of simple sine waves**. It converts time-domain complexity into frequency-domain clarity, enabling everything from audio compression to medical imaging. The math ($F(\\omega) = \\int f(t)e^{-j\\omega t}dt$) is elegant because it's essentially asking one question: "how much of each frequency is hiding in my signal?" """,
        "visual_diagram": {
            "format": "svg",
            "code": FOURIER_SVG,
            "description": "Fourier Transform: converting a complex time-domain signal into its frequency-domain components"
        },
        "visual_image": None,
    },

    ("taylor", "taylor series", "taylor expansion"): {
        "synthesized": """## 🧠 Concept

The **Taylor Series** answers one of the most practical questions in mathematics: *"How do I work with complicated functions using only addition, subtraction, and multiplication?"*

**The big idea:** Any smooth function — no matter how complex — can be perfectly approximated by a polynomial (a sum of powers of x). And polynomials are the easiest things in math to compute.

**Analogy:** Imagine you're trying to describe a winding mountain road to someone. You could start simple: "it goes uphill" (that's the linear approximation). Then add more detail: "it goes uphill, then curves right" (quadratic). Then even more: "uphill, curves right, then levels off" (cubic). Each term you add captures more detail about the road's shape. The Taylor Series does exactly this — it builds up a perfect description of any function, one term at a time.

**Why it matters:**
- **Calculators** use Taylor Series to compute sin, cos, eˣ, and ln
- **Physics** uses it to simplify complex equations (small-angle approximation: sin θ ≈ θ)
- **Engineering** relies on it for linearization of nonlinear systems
- **Machine learning** uses it in optimization (gradient descent is a first-order Taylor approximation!)

**Key insight:** The Taylor Series tells us that *local information* (the value of a function and its derivatives at a single point) contains *global information* about the function's behavior everywhere.

## 📐 Math

### Step-by-Step Mathematical Derivation

**Step 1: The Taylor Series Formula**

$$f(x) = \\sum_{n=0}^{\\infty} \\frac{f^{(n)}(a)}{n!}(x-a)^n$$

This says: any function $f(x)$ can be written as an infinite sum of terms involving its derivatives at point $a$.

**Step 2: Expanding the Sum**

$$f(x) = f(a) + f'(a)(x-a) + \\frac{f''(a)}{2!}(x-a)^2 + \\frac{f'''(a)}{3!}(x-a)^3 + \\cdots$$

Each term captures the function's behavior to higher precision.

**Step 3: Example — Taylor Series for $e^x$ around $a=0$**

Since all derivatives of $e^x$ equal $e^x$, and $e^0 = 1$:

$$e^x = 1 + x + \\frac{x^2}{2!} + \\frac{x^3}{3!} + \\frac{x^4}{4!} + \\cdots = \\sum_{n=0}^{\\infty} \\frac{x^n}{n!}$$

**Step 4: Convergence**

The series converges when the remainder term $R_n(x) \\to 0$ as $n \\to \\infty$:

$$R_n(x) = \\frac{f^{(n+1)}(c)}{(n+1)!}(x-a)^{n+1}$$

for some $c$ between $a$ and $x$ (Lagrange remainder).

**Step 5: Common Taylor Series**
- $\\sin(x) = x - \\frac{x^3}{3!} + \\frac{x^5}{5!} - \\cdots$
- $\\cos(x) = 1 - \\frac{x^2}{2!} + \\frac{x^4}{4!} - \\cdots$
- $\\frac{1}{1-x} = 1 + x + x^2 + x^3 + \\cdots$ (for $|x| < 1$)

## 🎨 Visual

The diagram shows how Taylor polynomial approximations converge to the original function. The **solid black curve** represents the actual function $f(x)$. The **red dashed line** ($n=1$) is the linear (tangent line) approximation — it captures the slope at the expansion point but diverges quickly. The **orange dashed curve** ($n=2$) adds curvature information, following the function more closely. The **blue curve** ($n=4$) includes higher-order terms and closely hugs the original function over a wide range.

The **blue dot** marks the expansion point $a$ (center) — where all the derivative information is sampled. Notice how all approximations are most accurate near this point and gradually diverge farther away.

## ✅ Final Understanding

The Taylor Series is mathematics' way of saying: **if you know everything about a function at one point (its value and all its derivatives), you can reconstruct the function everywhere.** Each additional term adds more precision, like zooming in on a map. The formula $f(x) = \\sum \\frac{f^{(n)}(a)}{n!}(x-a)^n$ is the foundation of numerical computing, physics approximations, and modern optimization.""",
        "visual_diagram": {
            "format": "svg",
            "code": TAYLOR_SVG,
            "description": "Taylor Series: polynomial approximations converging to the original function"
        },
        "visual_image": None,
    },

    ("newton", "newton's laws", "laws of motion"): {
        "synthesized": """## 🧠 Concept

**Newton's Laws of Motion** are three deceptively simple rules that govern how everything in the universe moves — from a rolling ball to orbiting planets.

**First Law (Inertia):** Objects are lazy. A ball sitting on a table won't suddenly start moving on its own, and a hockey puck sliding on frictionless ice would keep going forever. Things only change their motion when a force makes them. This isn't obvious — Aristotle thought objects naturally "wanted" to stop. Newton showed that motion, not rest, is the default state.

**Second Law (F = ma):** This is the master equation of motion. It says force equals mass times acceleration. Think of it as a recipe: how much an object accelerates depends on how hard you push it (force) and how heavy it is (mass). Push a shopping cart with the same force — an empty one zooms, a full one barely moves.

**Third Law (Action-Reaction):** Forces always come in pairs. When you push against a wall, the wall pushes back against you with exactly the same force. A rocket works because it pushes exhaust gases downward, and those gases push the rocket upward. *You can't touch without being touched.*

**Key insight:** These three laws are really one idea — $F = ma$ — with the other two being special cases (zero force and force pairs).

## 📐 Math

### Step-by-Step Derivation

**Step 1: The Second Law — The Foundation**

$\\vec{F}_{net} = m\\vec{a}$

This is a vector equation — force and acceleration have both magnitude and direction.

**Step 2: Connecting to Velocity**

Since $\\vec{a} = d\\vec{v}/dt$: $\\vec{F} = m \\frac{d\\vec{v}}{dt}$

This shows force causes the *rate of change* of velocity.

**Step 3: Momentum Form**

Defining momentum $\\vec{p} = m\\vec{v}$, we get the more general form: $\\vec{F} = \\frac{d\\vec{p}}{dt}$

This is actually Newton's original formulation and works even when mass changes (like a rocket burning fuel).

**Step 4: First Law as a Special Case**

When $F = 0$: $\\frac{dv}{dt} = 0$, so $v = $ constant

No force means no acceleration — velocity stays the same (including zero).

**Step 5: Third Law**

$\\vec{F}_{A \\to B} = -\\vec{F}_{B \\to A}$

Forces always come in equal-and-opposite pairs acting on *different* objects.

**Step 6: Gravitational Application**

In free fall: $F = mg = ma$, so $a = g = 9.8$ m/s²

All objects fall at the same rate regardless of mass (in a vacuum).

## 🎨 Visual

The diagram is organized into three color-coded panels at the top, one for each law. The **First Law** panel shows a ball in two positions connected by a dashed line — illustrating that without force, an object continues in its state of motion. The **Second Law** panel prominently displays $F = ma$, the central equation. The **Third Law** panel shows two objects (blue and red) exchanging equal and opposite forces, depicted by opposing arrows.

Below, the **Free Body Diagram** shows a rectangular mass with four force vectors: the blue upward **Normal force (N)**, the red downward **Weight (mg)**, the blue rightward **Applied force (F)**, and the orange leftward **Friction (f)**. This diagram is the essential tool for applying Newton's Second Law to real problems — you sum all forces to find the net force and resulting acceleration.

## ✅ Final Understanding

Newton's Laws boil down to one profound equation: **$F = ma$**. The First Law tells us what happens when $F = 0$ (nothing changes), and the Third Law tells us that forces always come in pairs. Together, these three laws form the complete foundation for predicting how any object will move — from a thrown baseball to a spacecraft navigating through the solar system.""",
        "visual_diagram": {
            "format": "svg",
            "code": NEWTON_SVG,
            "description": "Newton's Three Laws of Motion with free body diagram"
        },
        "visual_image": None,
    },
}
