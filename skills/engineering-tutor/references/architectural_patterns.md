# Reference: Architectural Patterns & Trade-offs

Use this to help defend your tech stack choices.

## 1. Databases
*   **PostgreSQL (Relational):** Best for structured data, complex queries, and ACID compliance. 
    *   *Trade-off:* Higher setup overhead than NoSQL; harder to scale horizontally.
*   **MongoDB/NoSQL:** Best for flexible schemas and rapid prototyping.
    *   *Trade-off:* Consistency can be harder to manage; no complex joins.
*   **Redis (In-Memory):** Best for speed, caching, and real-time state.
    *   *Trade-off:* Data is lost if not persisted; limited by RAM.

## 2. Languages / Runtimes
*   **TypeScript/Node.js:** Fast development, huge ecosystem, shared logic with frontend.
    *   *Trade-off:* Single-threaded (event loop); can be messy as it grows.
*   **Python:** Excellent for AI, data science, and readable scripts.
    *   *Trade-off:* Slower execution than compiled languages; dependency management (`pip`) can be brittle.
*   **Go/Rust:** High performance, safety, and concurrency.
    *   *Trade-off:* Steeper learning curve; more "boilerplate" for simple tasks.

## 3. Communication
*   **REST API:** Standard, easy to cache, widely supported.
    *   *Trade-off:* Over-fetching/under-fetching data is common.
*   **WebSockets:** Real-time, bi-directional.
    *   *Trade-off:* Harder to scale; keeps connections open.
*   **GraphQL:** Client asks for exactly what it needs.
    *   *Trade-off:* Complex to set up on the backend; harder to cache.
