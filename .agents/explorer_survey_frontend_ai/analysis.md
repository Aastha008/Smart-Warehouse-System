# Comprehensive Analysis: R5 (Frontend Web App) & R6 (Grounded AI Assistant & Real-time Alerts)

**Explorer**: `teamwork_preview_explorer_survey_frontend_ai`  
**Date**: 2026-09-02  
**Working Directory**: `C:/Users/hp/.gemini/antigravity/scratch/ai-warehouse-intelligence/.agents/explorer_survey_frontend_ai`  
**Target Workspace**: `C:/Users/hp/.gemini/antigravity/scratch/ai-warehouse-intelligence`

---

## Executive Summary

This investigation analyzed the authoritative source of truth for **Requirement 5 (Interactive Web Dashboard & Video UI)** and **Requirement 6 (Grounded AI Supervisor Assistant & Real-time Alerts)** in the `ai-warehouse-intelligence` project.

- **Frontend Build & Framework**: The frontend is built on **React 18.2.0 + TypeScript 5.2.2 + Tailwind CSS v4.0.0 (`@tailwindcss/vite`) + Vite 5.2.0**. Key libraries include `lucide-react`, `recharts` (2.12.3), `date-fns` (3.6.0), `axios` (1.6.8), and `react-router-dom` (6.22.3). Once `npm install` is executed, `npm run build` (`tsc && vite build`) executes cleanly with zero syntax/type errors.
- **Current State of R5 (Frontend UI)**: The overall shell, navigation, routing, and basic pages exist, but most interactive features are mock/placeholder implementations. Specifically:
  - `VideoPlayer.tsx` lacks an HTML `<video>` element, using a static black `<div>` with hardcoded CSS overlays rather than dynamic bounding boxes synchronized with video playback time.
  - Timestamp navigation ("jump-to-incident on click") is not wired to the player.
  - `VideoAnalysis.tsx` has static mock incident lists and no functional video upload / background job polling.
  - `Analytics.tsx` is an empty placeholder component.
  - `Incidents.tsx` lacks interactive search/filtering, CSV export, and incident detail inspection modals.
  - Naming mismatches exist between backend API schemas (snake_case: `event_id`, `event_type`, `risk_level`, `explanation`) and frontend types (camelCase: `id`, `type`, `riskLevel`, `description`), causing live API data to fail rendering unless fallbacks/transformers are provided.
- **Current State of R6 (AI Assistant & Alerts)**:
  - The backend assistant (`backend/assistant/assistant.py`) implements a hybrid architecture: an OpenAI LLM tool-calling prompt backed by regex pattern handlers grounded on warehouse event statistics and safety rules.
  - Key bug identified: Property name mismatch between `EventService.get_statistics` (returns `high_risk`, `critical`) and `WarehouseAssistant._handle_today_events` / `_handle_summary` (looks for `high_risk_count`, `critical_count`).
  - `AssistantTools` class contains empty stub queries (`pass`) when accessed directly.
  - Real-time alerts (Web Audio API alerts, HTML5 Browser Notification permissions/toasts, and structured intervention cards for HIGH and CRITICAL events) are missing in the frontend.

---

## 1. R5: React + TypeScript + Tailwind CSS Web Application

### 1.1 Project Structure & Build Configuration

| File | Purpose | Observed Status |
|---|---|---|
| `frontend/package.json` | Dependencies & build scripts | Uses Vite 5.2, React 18.2, TS 5.2, Tailwind v4, Recharts, Lucide-React, Axios, Date-fns. |
| `frontend/vite.config.ts` | Vite configuration | Configures `@vitejs/plugin-react` and `@tailwindcss/vite`, proxies `/api` to `http://localhost:8000`. |
| `frontend/tsconfig.json` | TS compiler options | Strict mode enabled, `noEmit: true`, `jsx: react-jsx`, `moduleResolution: bundler`. |
| `frontend/src/index.css` | Global styling & Tailwind theme | Configures `@import "tailwindcss";` and custom color theme tokens (`--color-risk-low`, `--color-risk-medium`, `--color-risk-high`, `--color-risk-critical`). |
| `frontend/src/main.tsx` | Entry point | Mounts `<App />` to `#root` in `React.StrictMode`. |
| `frontend/src/App.tsx` | Router definition | Configures `BrowserRouter` with 7 child routes inside `Layout`. |

**Build Verification Result**:
```bash
> npm run build
> tsc && vite build
✓ 2655 modules transformed.
dist/index.html                   0.44 kB
dist/assets/index-CG2_Yfbs.css   26.83 kB
dist/assets/index-CdkKIfEB.js   661.82 kB
✓ built in 31.30s (exit code 0)
```

### 1.2 Route & Component Hierarchy

```
App (src/App.tsx)
└── Layout (src/components/Layout.tsx)
    ├── Sidebar Navigation (Dashboard, Video Analysis, Live Monitoring, Incidents, Analytics, AI Assistant, Settings)
    ├── Header (Notifications Bell, User Avatar)
    └── Content Outlet (<Outlet />)
        ├── /dashboard  → Dashboard (src/pages/Dashboard.tsx)
        │                 ├── StatCard (src/components/StatCard.tsx)
        │                 ├── RiskChart (src/components/RiskChart.tsx)
        │                 └── EventTimeline (src/components/EventTimeline.tsx)
        ├── /video      → VideoAnalysis (src/pages/VideoAnalysis.tsx)
        │                 └── VideoPlayer (src/components/VideoPlayer.tsx)
        ├── /live       → LiveMonitoring (src/pages/LiveMonitoring.tsx)
        ├── /incidents  → Incidents (src/pages/Incidents.tsx)
        │                 └── RiskBadge (src/components/RiskBadge.tsx)
        ├── /analytics  → Analytics (src/pages/Analytics.tsx) [CURRENTLY EMPTY PLACEHOLDER]
        ├── /assistant  → AIAssistant (src/pages/AIAssistant.tsx)
        └── /settings   → Settings (src/pages/Settings.tsx)
```

---

### 1.3 Detailed Page-by-Page & Component Analysis

#### 1.3.1 Enterprise Dashboard (`src/pages/Dashboard.tsx`)
- **KPI Summary Cards**: Renders 4 `StatCard` items (`Total Events (30d)`, `Events Today`, `High Risk Events`, `Critical Incidents`).
- **Risk Distribution Chart**: Renders `RiskChart` (Recharts AreaChart stacked by Critical/High).
- **Recent Incident Feed**: Renders `EventTimeline` with severity indicators and relative timestamps.
- **Identified Deficiencies**:
  - Two summary cards ("Most Frequent Issue" and "Highest Risk Area") have hardcoded static text ("Missing PPE (Helmet)" and "Loading Bay 3") instead of dynamically using `/api/dashboard/behaviours` and `/api/dashboard/locations`.
  - Field naming mismatch between backend response (`total_events`, `events_today`, `high_risk_count`) and frontend (`totalEvents`, `eventsToday`, `highRisk`).

#### 1.3.2 Video Analysis & Incident Replay (`src/pages/VideoAnalysis.tsx` & `src/components/VideoPlayer.tsx`)
- **Observed Code in `VideoPlayer.tsx`**:
  ```tsx
  // src/components/VideoPlayer.tsx lines 7-16
  <div className="bg-black aspect-video rounded-xl overflow-hidden relative group">
    <div className="w-full h-full bg-slate-800 flex items-center justify-center text-slate-500">
      {url ? "Video Playing" : "No Video Source"}
    </div>
    <div className="absolute top-[30%] left-[40%] w-32 h-48 border-2 border-red-500 flex items-start">
      <span className="bg-red-500 text-white text-xs px-1 font-bold">Forklift - High Risk</span>
    </div>
  ```
- **Identified Deficiencies**:
  1. No actual HTML5 `<video ref={videoRef} src={...}>` element is rendered.
  2. Bounding box overlay is hardcoded HTML (`top-[30%] left-[40%]`) rather than dynamic overlay computed from bounding box tracking coordinates `[x1, y1, x2, y2]` per frame / timestamp.
  3. No video playback state synchronization (current time, play/pause, duration).
  4. Clicking on detected incidents in `VideoAnalysis.tsx` does not seek or navigate video playback (`currentTime = event.video_start`).
  5. Upload button does not trigger file picker or send multipart `POST /api/video/upload` and `POST /api/video/analyze`.

#### 1.3.3 Live Monitoring (`src/pages/LiveMonitoring.tsx`)
- Displays a 4-grid multi-cam layout (Cam 01 to Cam 04) and an Active Alerts panel.
- **Identified Deficiencies**:
  - Grid viewports display static text "Live Feed Processing...".
  - Active Alerts list is hardcoded `[1,2,3,4,5]` without polling `/api/alerts/recent` or subscribing to live events.

#### 1.3.4 Incident Log & Details (`src/pages/Incidents.tsx`)
- Displays a table of incidents with columns: Incident ID, Timestamp, Type, Location, Risk Level, Actions.
- **Identified Deficiencies**:
  - Search input is uncontrolled and does not filter table rows.
  - Filter button has no modal or dropdown.
  - Export CSV button has no download trigger.
  - "View Details" button has no click handler or detail inspection modal (which should display the bounding box snapshot, evidence metrics like drop height/velocity, explanation, and intervention recommendation).

#### 1.3.5 Analytics (`src/pages/Analytics.tsx`)
- **Observed Code**:
  ```tsx
  export default function Analytics() {
    return (
      <div className="p-6 flex items-center justify-center min-h-[500px]">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-slate-800 mb-2">Analytics & Reports</h2>
          <p className="text-slate-500">Advanced analytical views are currently under development.</p>
        </div>
      </div>
    );
  }
  ```
- **Identified Deficiencies**:
  - Complete placeholder. Needs 10-behavior distribution charts, multi-day risk trend comparisons, bay risk ranking/heatmap, and shift/hourly statistics.

#### 1.3.6 Settings (`src/pages/Settings.tsx`)
- Contains UI sliders for detection sensitivity and checkboxes for Responsible AI privacy features (Face Blurring, Data Minimization).
- **Identified Deficiencies**:
  - Static state without persistence or integration with backend configuration YAML files.

---

### 1.4 API Client & Type Mappings (`src/services/api.ts` & `src/types/index.ts`)

| Frontend Interface (`src/types/index.ts`) | Backend Model (`backend/schemas/`) | Discrepancy / Mapping Issue |
|---|---|---|
| `Event.id` | `EventResponse.event_id` | Property mismatch: frontend expects `id`, backend sends `event_id`. |
| `Event.type` | `EventResponse.event_type` | Property mismatch: frontend expects `type`, backend sends `event_type`. |
| `Event.riskLevel` | `EventResponse.risk_level` | Property mismatch: camelCase vs snake_case. |
| `Event.description` | `EventResponse.explanation` | Property mismatch: `description` vs `explanation`. |
| `DashboardSummary.totalEvents` | `DashboardSummary.total_events` | Property mismatch: camelCase vs snake_case. |
| `DashboardSummary.highRisk` | `DashboardSummary.high_risk_count` | Property mismatch: camelCase vs snake_case. |
| `DashboardSummary.eventsToday` | `DashboardSummary.events_today` | Property mismatch: camelCase vs snake_case. |
| `RiskTrend: { date, low, medium, high, critical }` | `DashboardService.get_trends()` returns `[{ date, risk_level, count }]` | Backend `DashboardService.get_trends` flattens data per risk level rather than grouping by date. |
| `api.get('/alerts')` | `backend/api/alerts.py` defines `@router.get('/recent')` | Route mismatch: frontend calls `/api/alerts`, backend expects `/api/alerts/recent`. |

---

## 2. R6: Grounded AI Supervisor Assistant & Real-time Alerts

### 2.1 AI Assistant Architecture (`backend/assistant/assistant.py` & `backend/api/assistant.py`)

1. **Processing Flow**:
   - Operator submits query to `/api/assistant/query`.
   - `backend/api/assistant.py` fetches live statistics (`EventService.get_statistics`) and recent events (`EventService.get_events`), then calls `WarehouseAssistant.process_query(query, events_data, stats)`.
   - If `OPENAI_API_KEY` is present, `_llm_response()` creates a system context with grounded warehouse statistics and events, using temperature `0.3` and strict system instructions ("NEVER invent events").
   - If no LLM API key is present, fallback `_template_response()` matches query regex patterns to 12 domain handlers:
     - Today's events summary (`_handle_today_events`)
     - High-risk events breakdown (`_handle_high_risk`)
     - Common risky behaviors (`_handle_common_behaviours`)
     - Location / Bay analysis (`_handle_location_query`)
     - Risk explanation reasons (`_handle_why_risk`)
     - Corrective action recommendations (`_handle_recommendations`)
     - Trend analysis (`_handle_trends`)
     - Operator training opportunities (`_handle_training`)
     - Warehouse summary (`_handle_summary`)
     - Stacking behavior analysis (`_handle_stacking_query`)
     - Drop behavior analysis (`_handle_drop_query`)
     - Dragging behavior analysis (`_handle_drag_query`)
     - General / out-of-domain guidance (`_handle_general`)

2. **Grounding & Refusal Logic**:
   - The assistant explicitly refuses to assert unverified physical damage, strictly classifying occurrences as "potential damage-causing events" requiring inspection.
   - When no events exist, it states: *"No events have been detected today so far... I will explicitly tell you when information is unavailable."*

3. **Critical Bugs Identified in Assistant Logic**:
   - **Statistic Key Mismatches**:
     - `EventService.get_statistics()` returns: `{"high_risk": ..., "critical": ..., "events_today": ..., "total_events": ...}`
     - `WarehouseAssistant._handle_today_events()` (lines 152-153) and `_handle_summary()` (lines 419-420) look for: `stats.get("high_risk_count", 0)` and `stats.get("critical_count", 0)`. Because the key in `EventService` is `"high_risk"`, `high_risk` evaluates to `0` even when high-risk events exist in the database.
   - **Direct Tool Calling Stub**:
     - `AssistantTools.get_events()` (line 26) contains `pass` and returns `[]`.
     - `AssistantTools.get_statistics()` returns hardcoded zeros.

---

### 2.2 Real-time Alerts & Browser Notifications

1. **Backend Alert Infrastructure**:
   - `backend/database/models.py`: `AlertLog` model with `event_id`, `alert_type`, `sent_at`, `acknowledged`.
   - `backend/services/alert_service.py`: `create_alert`, `get_recent_alerts`, `acknowledge_alert`.
   - `backend/api/alerts.py`: `GET /api/alerts/recent`, `POST /api/alerts/{alert_id}/acknowledge`.

2. **Frontend Alert Gaps**:
   - **Web Audio API**: No audio synthesizer or chime sound for `HIGH` or `CRITICAL` incidents.
   - **HTML5 Browser Notifications**: No `Notification.requestPermission()` or notification dispatch on alert reception.
   - **Structured Intervention Recommendations**: The backend generates specific prevention recommendations (via `backend/risk/risk_explanation.py:generate_recommendation`), but the frontend does not render prominent intervention cards on the dashboard or live feed.
   - **Acknowledgement UI**: No button to acknowledge or clear active alerts from the frontend.

---

## 3. Comprehensive Summary of Findings

| Subsystem | Component | Status | Key Issues / Required Fixes |
|---|---|---|---|
| **R5** | Build & Tooling | ✅ Verified | Builds cleanly (`npm run build` exits 0 after `npm install`). |
| **R5** | Router & Layout | ✅ Working | Sidebar navigation, active route styling, header layout functional. |
| **R5** | Enterprise Dashboard | ⚠️ Partial | StatCards work with mock fallback; needs camelCase/snake_case API transformer; dynamic behaviour/bay cards. |
| **R5** | Video Player & Replay | ❌ Mock/Incomplete | Needs real `<video>` tag, canvas/SVG bounding box overlays synchronized with `currentTime`, and timestamp jump handler. |
| **R5** | Video Analysis Page | ⚠️ Partial | File upload UI not connected to `/api/video/upload`; incident list is static mock data. |
| **R5** | Live Monitoring Page | ⚠️ Partial | Cam feeds are static placeholders; alerts list is hardcoded numbers. |
| **R5** | Incident Log & Details | ⚠️ Partial | Table displays data but search, filter, CSV export, and detail modal are unimplemented. |
| **R5** | Analytics Page | ❌ Placeholder | 13-line placeholder; needs behavior distribution, risk trend, and location risk charts. |
| **R5** | Settings Page | ⚠️ Static | Form inputs not connected to backend configs. |
| **R5** | API Client | ⚠️ Discrepant | Field name mismatches (`id` vs `event_id`, `type` vs `event_type`, `riskLevel` vs `risk_level`, `alerts` route path). |
| **R6** | AI Assistant Backend | ✅ Strong Logic | Solid 12-pattern template engine + OpenAI LLM fallback. Needs key consistency fix (`high_risk` vs `high_risk_count`). |
| **R6** | AI Assistant Frontend | ⚠️ Functional UI | Chat works; needs display of `sources`, grounding indicators, and structured recommendations. |
| **R6** | Real-time Audio Alerts | ❌ Missing | No Web Audio API tone generator for HIGH/CRITICAL events. |
| **R6** | Browser Notifications | ❌ Missing | No HTML5 Notification API integration. |
| **R6** | Intervention Guidance | ⚠️ Backend Only | Recommendations exist in backend risk engine but need prominent UI callout styling. |
