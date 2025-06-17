#!/bin/bash
exec uvicorn chatbot_api:app --host 0.0.0.0 --port 8080
