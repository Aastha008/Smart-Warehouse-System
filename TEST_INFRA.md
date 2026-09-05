# E2E Test Infra: AI Warehouse Intelligence

## Test Philosophy
- Opaque-box, requirement-driven. Derives test assertions from ORIGINAL_REQUEST.md.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workload Testing.

## Feature Inventory
| # | Feature | Source | Tier 1 | Tier 2 | Tier 3 |
|---|---------|--------|:------:|:------:|:------:|
| 1 | Video Ingestion & Stream Compatibility | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ |
| 2 | Warehouse Entity Detection | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ |
| 3 | Object Tracking & Motion Estimation | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ |
| 4 | 10 Behaviour Detectors | ORIGINAL_REQUEST §R2 | 10 | 10 | ✓ |
| 5 | Externalized YAML Configurations | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ |
| 6 | Multi-factor Risk Engine | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ |
| 7 | Damage-prevention Explainability | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ |
| 8 | Structured Incident Storage | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ |
| 9 | FastAPI REST Endpoints | ORIGINAL_REQUEST §R4 | 5 | 5 | ✓ |
| 10 | Grounded AI Supervisor | ORIGINAL_REQUEST §R6 | 5 | 5 | ✓ |
| 11 | Synchronized Video Player & Replay | ORIGINAL_REQUEST §R5 | 5 | 5 | ✓ |
| 12 | Enterprise KPI Dashboard & Analytics | ORIGINAL_REQUEST §R5 | 5 | 5 | ✓ |
| 13 | Incident Log & Detail Modal | ORIGINAL_REQUEST §R5 | 5 | 5 | ✓ |
| 14 | Real-time Alerts & Notifications | ORIGINAL_REQUEST §R6 | 5 | 5 | ✓ |
| 15 | Demo & Synthetic Scenarios | ORIGINAL_REQUEST §R7 | 5 | 5 | ✓ |
| 16 | Test Suite & E2E Verification | ORIGINAL_REQUEST §R7 | 5 | 5 | ✓ |
| 17 | Comprehensive Documentation | ORIGINAL_REQUEST §R7 | 5 | 5 | ✓ |

## Test Architecture
- **Unit & Behaviour Tests**: `pytest tests/unit/`, `pytest tests/behaviour/`
- **API Tests**: `pytest tests/api/test_api.py`
- **Integration Tests**: `pytest tests/integration/test_pipeline_e2e.py`
- **Frontend Build Verification**: `cd frontend && npm run build`

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | High-velocity Package Drop in Loading Bay 3 | F1, F2, F3, F4, F6, F7, F8, F9, F14 | High |
| 2 | Forklift Approaching Pedestrian Zone & Stacking | F2, F3, F4, F5, F6, F7, F8, F12, F14 | High |
| 3 | Operator Querying AI Supervisor for Shift High-Risk Events | F8, F9, F10, F12 | Medium |
| 4 | Incident Review & Synchronized Video Jump on Web UI | F1, F8, F9, F11, F13 | Medium |
| 5 | Synthetic Video Processing & Dashboard Heatmap Aggregation | F1, F4, F8, F9, F12, F15 | High |

## Coverage Thresholds
- Tier 1: ≥5 per feature
- Tier 2: ≥5 per feature (where boundaries exist)
- Tier 3: Pairwise coverage of major feature interactions
- Tier 4: ≥5 realistic application scenarios
