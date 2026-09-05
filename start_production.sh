#!/bin/bash
echo 'Starting AI Warehouse Intelligence Production Server'
cd frontend && npm run build && cd ..
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
