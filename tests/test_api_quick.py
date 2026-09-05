"""API Test Script"""
import httpx
import json

base = "http://localhost:8000"
results = []

def check_endpoint(name, r, expected=200):
    ok = r.status_code == expected
    icon = "PASS" if ok else "FAIL"
    msg = f"[{icon}] {name}: {r.status_code}"
    try:
        data = r.json()
        if isinstance(data, dict):
            msg += f" keys={list(data.keys())[:5]}"
    except Exception:
        pass
    results.append((ok, msg))
    print(msg)

# Core endpoints
check_endpoint("Root", httpx.get(f"{base}/"))
check_endpoint("Dashboard summary", httpx.get(f"{base}/api/dashboard/summary"))
check_endpoint("Events list", httpx.get(f"{base}/api/events"))
check_endpoint("High risk events", httpx.get(f"{base}/api/events/high-risk"))
check_endpoint("Today events", httpx.get(f"{base}/api/events/today"))
check_endpoint("Statistics", httpx.get(f"{base}/api/events/statistics"))
check_endpoint("Statistics alias", httpx.get(f"{base}/api/statistics"))
check_endpoint("Dashboard trends", httpx.get(f"{base}/api/dashboard/trends"))
check_endpoint("Dashboard locations", httpx.get(f"{base}/api/dashboard/locations"))
check_endpoint("Dashboard behaviours", httpx.get(f"{base}/api/dashboard/behaviours"))

# AI Assistant
r = httpx.post(f"{base}/api/assistant/query", json={"query": "What happened today?"})
check_endpoint("Assistant - today", r)
resp = r.json()
print(f"  Response preview: {resp.get('response', '')[:100]}...")

r = httpx.post(f"{base}/api/assistant/query", json={"query": "Show me high-risk events"})
check_endpoint("Assistant - high risk", r)

r = httpx.post(f"{base}/api/assistant/query", json={"query": "What corrective action should we take?"})
check_endpoint("Assistant - actions", r)

r = httpx.post(f"{base}/api/assistant/query", json={"query": "Which loading bay needs attention?"})
check_endpoint("Assistant - location", r)

# Alerts and video
check_endpoint("Recent alerts", httpx.get(f"{base}/api/alerts/recent"))
check_endpoint("Video list", httpx.get(f"{base}/api/video/list"))

# Error handling
check_endpoint("Non-existent event", httpx.get(f"{base}/api/events/nonexistent"), expected=404)
check_endpoint("Non-existent job", httpx.get(f"{base}/api/video/status/nonexistent"), expected=404)
check_endpoint("Events by location", httpx.get(f"{base}/api/events/by-location/loading_bay_1"))

# OpenAPI docs
check_endpoint("OpenAPI docs", httpx.get(f"{base}/docs"))

# Summary
passed = sum(1 for ok, _ in results if ok)
total = len(results)
print(f"\n{'='*50}")
print(f"Results: {passed}/{total} passed")
if passed == total:
    print("ALL TESTS PASSED!")
else:
    print("Some tests failed - check above for details")
