---
name: fastapi-expert
description: Idiomatic FastAPI and Pydantic development practices. Use when building, extending, or reviewing FastAPI endpoints, Pydantic v2 models, API routers, dependency injection, and request/response lifecycles.
---

# FastAPI & Pydantic Expert Development

## Overview

High-performance, maintainable API design using FastAPI and Pydantic v2. Focuses on type safety, clear request/response boundaries, idiomatic dependency injection, and testability.

## Core Principles

1. **Pydantic v2 Strict Typing:**
   - Define explicit request and response models for all endpoints.
   - Use `Field(..., description="...")` with default factories (`default_factory=list`, `default_factory=dict`) to prevent mutable default bugs.
   - Use `model_config = ConfigDict(...)` instead of legacy v1 `class Config`.

2. **Async vs Sync Separation:**
   - Use `async def` for I/O-bound operations (network calls, external APIs).
   - Use regular `def` for CPU-bound computations (e.g. data enrichment, hashing, regex parsing) to allow FastAPI to run them in an external threadpool without blocking the main event loop.

3. **Dependency Injection:**
   - Encapsulate shared state, configuration access, and database/store handles in `Depends(...)` providers.
   - Enables effortless overriding in test suites via `app.dependency_overrides`.

4. **Error Handling & HTTP Semantics:**
   - Raise explicit `HTTPException(status_code=..., detail=...)` rather than returning error objects with HTTP 200.
   - Validate input boundaries at the router level and isolate business logic in `app/core/` and `app/services/`.

5. **Testing Contract:**
   - Test every endpoint using Starlette/FastAPI `TestClient` or `httpx.AsyncClient`.
   - Verify status codes, header configurations (CORS), and exact JSON serialization.

