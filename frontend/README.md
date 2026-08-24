# HeatShield: ShadeStop

HeatShield: ShadeStop helps municipal resilience planners identify which bus stops in Hartford, Connecticut, should receive shade interventions first. The tool prioritizes locations by combining microclimate temperature analysis, local canopy shade deficits, community transit dependencies, and social equity vulnerability indicators.

This frontend is a production-quality, responsive dashboard designed for Next.js (App Router), TypeScript, and Tailwind CSS. It is decoupled from any hardcoded state and fetches data dynamically from typed API routes matching the official backend contract.

---

## Key Features

1. **Overview Dashboard**: Track critical Prioritizations, average dangerous duration exposure, and the highest priority recommendation.
2. **Dynamic Weighting MCDA**: Planner settings allow adjusting weights (Heat Exposure, Shade Deficit, Vulnerability, Transit Importance) and risk thresholds (90°F–102°F) to recalculate scores dynamically.
3. **Interactive Priority Map**: MapLibre GL JS integration displaying Hartford boundaries and priority-colored markers. Automatically switches to an **Interactive Vector SVG Map** fallback in environments without WebGL or graphics rendering resources.
4. **Shade Intervention Simulator**: Planners can simulate Conservative (20%), Moderate (35%), or High (50%) shade scenario interventions, reviewing avoided exposure duration, projected scores, and ranking shift.
5. **Planning Assistant Box**: A natural-language engine allowing planners to query rankings, persistent heat, and weight impacts using preset queries or inputs.
6. **High-Density Table Queue**: Searchable, filterable, and sortable rankings table displaying full technical details for 110 Hartford stops.
7. **CSV Action Reports**: Complete technical summary tables can be downloaded locally with one click.

---

## Directory Layout

```
├── app/
│   ├── api/v1/             # Mock API Route Handlers (dynamic calculations)
│   ├── globals.css         # Styling (Tailwind + MapLibre)
│   ├── layout.tsx          # App framework layout
│   ├── page.tsx            # Main Orchestrating Dashboard Container
│   └── providers.tsx       # TanStack Query wrap
├── components/             # Reusable UI Dashboard Widgets
├── lib/
│   ├── api-client.ts       # Typed API client with Zod validations
│   ├── types.ts            # API data structure Zod schemas & types
│   └── fixtures/           # Hartford boundaries, bus stops, and timeseries
├── package.json            # Node dependencies (Next.js, Recharts, MapLibre, Zod)
├── tailwind.config.ts      # Tailwind settings
└── tsconfig.json           # TS configuration
```

---

## Setup & Running Locally

### Prerequisites
- Node.js &nbsp;`v18+` or `v20+`
- npm &nbsp;`v9+` or `v10+`

### 1. Configure Environment
Create a `.env` file in the root directory (copied from `.env.example`):
```bash
cp .env.example .env
```
Ensure `DATA_MODE=fixture` is set. In fixture mode, the Next.js API routes will automatically compute scores and simulations locally from the Hartford dataset without contacting remote backend networks.

### 2. Install Dependencies
```bash
npm install
```

### 3. Run Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser to interact with the dashboard.

### 4. Build for Production
```bash
npm run build
npm run start
```

---

## Priority Scoring Model

Priority scores are computed dynamically inside the Route Handlers using normalized percentiles (0–100):

$$Priority\ Score = w_{heat} \times Heat + w_{shade} \times Shade + w_{vuln} \times Vuln + w_{transit} \times Transit$$

Where:
- **Heat Score**: $0.50 \times Exceedance + 0.30 \times Duration + 0.20 \times Persistence$
- **Shade Deficit**: Canopy deficit fraction in 100m buffer.
- **Vulnerability**: Census tract indicators (zero-vehicle rates, median income, etc.).
- **Transit Importance**: Overlapping route counts and passenger boarding proxies.
