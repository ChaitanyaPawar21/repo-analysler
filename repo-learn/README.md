# Repo-Learn 🚀

**Repo-Learn** is a modern, developer-centric repository analysis dashboard. It bridges the gap between structured code repositories and conversational AI, presenting deeply nested folder architectures and complex architectural dependency graphs in a stunning, interactive, and beautifully animated UI.

---

## 🌟 Key Features

### 1. ChatGPT-Inspired Landing Page
A beautifully minimalistic, centralized entry-point mimicking modern AI conversational interfaces. Complete with glowing search inputs, premium spacing, and "Quick Search" chips for popular mock frameworks (React, Next.js, etc.).

### 2. GenZ-Aesthetic Folder UI
The core Dashboard features a massive, full-width **Repository Folder Architecture** visualizer.
- **Deep Hierarchical Data:** Navigate deeply nested structural trees natively.
- **Interactive Explanations:** Every click vividly highlights the active node and slides in an "AI Insight Box" detailing the architectural function of the selected file or process.

### 3. Interactive Dependency Graph (React Flow)
A robust, scalable architectural layout engine built specifically for large graphs.
- **Semantic Grouping:** File structures are visually grouped into aesthetic bounding boxes (e.g., `Auth & Identity`, `Order & Checkout`) using pastel backgrounds and neon borders.
- **Smoothstep Routing:** Operations are perfectly connected via right-angled orthogonal edges to avoid chaotic UI webbing.
- **Interactive Canvas:** Supports infinite click-and-drag panning, and precise zooming (via `Ctrl + Scroll` or trackpad pinch).
- **Custom Tooltips:** Hovering over specific nodes elevates the element and provides dynamic tooltips explaining the core background logic.

### 4. Fluid Animations (GSAP)
The entire application is driven by `@gsap/react`, delivering silky-smooth 60fps staggered entrance animations, glowing node pulses, and state transitions without heavy performance penalties.

---

## 🛠️ Tech Stack
- **Framework:** React 18 + Vite
- **Styling:** Custom Vanilla CSS (Design Tokens, Glassmorphism, CSS Variables)
- **Animations:** GSAP (`@gsap/react`)
- **Graphing Engine:** React Flow (`@xyflow/react`)
- **Icons:** Lucide React

---

## 💻 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/ChaitanyaPawar21/repo-analysler.git
cd repo-analysler/repo-learn
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Start the Development Server
```bash
npm run dev
```

### 4. Build for Production
```bash
npm run build
```

---

## 🎨 Design Philosophy
* **Deep Dark Theme:** Primary colors are strict deep blacks (`#0B0F19`) and deep slate (`#0F172A`), completely eliminating harsh whites.
* **Premium Accents:** Elements are highlighted using an electric bright blue (`#2563EB`) via sophisticated neon box-shadow glows rather than simple flat borders.
* **Glassmorphism:** Context menus and floating structural elements employ subtle `backdrop-filter: blur()` effects.

---

## 🤝 Next Steps
* Integrate backend Node.js APIs to pull actual filesystem reads.
* Hook up large language models (LLMs) to dynamically populate the currently mocked AI context boxes based on syntax tree parsing.
