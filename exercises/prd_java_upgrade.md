# PRD: Java 8 → Java 21 & Spring Boot 3 Migration

> **Workshop Use:** Practice exercise for large-scale codebase refactoring using the 1M token context window, Conductor's planning workflow, and context engineering. Demonstrates how the agent can bootstrap its own project understanding before performing mechanical migration work.

## Problem

An enterprise Java REST API (Spring PetClinic REST) runs on Java 8 and Spring Boot 2.6.x. Java 8 reached end of public updates in 2022. The application can't use Virtual Threads, modern GC improvements, or the latest security patches. Compliance requires migration to a supported LTS version.

## Business Drivers

| Driver | Impact |
|:---|:---|
| **Security compliance** | Java 8 is EOL — no security patches. Audit finding blocks next SOC 2 renewal. |
| **Performance** | Java 21 Virtual Threads reduce thread pool contention on high-concurrency endpoints. Estimated 30% reduction in p99 latency. |
| **Cost** | Improved memory footprint means smaller container instances. Estimated 20% infrastructure savings. |
| **Developer experience** | Records, sealed classes, pattern matching, text blocks — reduces boilerplate by ~15%. |

## Scope

### In Scope
- Upgrade from Java 8 to Java 21 (LTS)
- Upgrade from Spring Boot 2.6.x to Spring Boot 3.3.x
- Migrate from javax.* to jakarta.* namespace
- Replace deprecated Security configuration (`WebSecurityConfigurerAdapter`)
- Migrate OpenAPI/Swagger from SpringFox to SpringDoc
- Enable Virtual Threads
- Ensure all existing tests pass

### Out of Scope
- Microservice decomposition (monolith stays monolith)
- Database schema changes
- New feature development

## Workshop Setup: Version Alignment

To ensure the migration exercise remains consistent with the target state defined in this PRD, we use the **Spring PetClinic REST** variant at **tag `v2.6.2`**. This specific tag serves as our stable baseline — it uses **Spring Boot 2.6.2 and Java 8**, and critically includes real Spring Security configuration with `WebSecurityConfigurerAdapter`, making the security migration phase authentic.

```bash
git clone --branch v2.6.2 --depth 1 https://github.com/spring-petclinic/spring-petclinic-rest.git
cd spring-petclinic-rest
```

> **Why this variant?** The main `spring-petclinic` repo has never included Spring Security. The REST variant has `BasicAuthenticationConfig` extending `WebSecurityConfigurerAdapter` with JDBC-backed authentication, `@PreAuthorize` role-based access, and CORS configuration — all patterns that require hands-on migration to Spring Security 6.

## Migration Checklist

### Phase 0: Context Engineering — Agent Self-Onboarding

Before writing a single line of migration code, the agent should build its own understanding of the codebase. This phase uses the **codebase investigator** pattern: the agent reads the entire project, maps architectural patterns, and generates a `GEMINI.md` that encodes what it learned — effectively writing its own context file.

- [ ] **Investigate the codebase:**
  ```
  @codebase_investigator Analyze the full project structure, dependencies,
  and architectural patterns. Map all Spring Security configuration classes,
  data access layers (JDBC, JPA, Spring Data), and REST controller patterns.
  ```
- [ ] **Generate a migration-aware GEMINI.md:**
  ```
  Based on your analysis, write a GEMINI.md file for this project that:
  1. Documents the current architecture (Boot 2.6, Java 8, javax namespace)
  2. Defines the target architecture (Boot 3.3, Java 21, jakarta namespace)
  3. Lists migration rules (one module at a time, preserve API contracts, etc.)
  4. Encodes testing standards (every migrated endpoint must pass tests)
  5. Notes known migration risks you identified
  ```
- [ ] **Review and approve the generated GEMINI.md** before proceeding
- [ ] **Verify context loads correctly:** `/stats` to confirm GEMINI.md is active

> **Why this matters:** This is the "context engineering for migrations" pattern. Instead of a human writing the GEMINI.md from scratch, the agent uses its codebase investigation capabilities to bootstrap a rich context file. The agent then uses this file to guide its own migration work in subsequent phases — a self-reinforcing loop where better context produces better code changes.

### Phase 1: Build System
- [ ] Update `pom.xml`: set `java.version` to 21
- [ ] Update Spring Boot parent to 3.3.x
- [ ] Replace removed JDK APIs:
  - JAXB → `jakarta.xml.bind:jakarta.xml.bind-api` + Glassfish runtime
  - `javax.annotation` → `jakarta.annotation:jakarta.annotation-api`
  - `mysql-connector-java` → `com.mysql:mysql-connector-j`
- [ ] Run `mvn clean compile` — fix all compilation errors before proceeding

### Phase 2: Namespace Migration
- [ ] Global find-and-replace: `javax.persistence` → `jakarta.persistence`
- [ ] Global find-and-replace: `javax.validation` → `jakarta.validation`
- [ ] Global find-and-replace: `javax.servlet` → `jakarta.servlet`
- [ ] Global find-and-replace: `javax.annotation` → `jakarta.annotation`
- [ ] Verify: no remaining `javax.*` imports (except `javax.sql.*` which is unchanged)

### Phase 3: Security Configuration
- [ ] Remove classes extending `WebSecurityConfigurerAdapter` (deleted in Spring Security 6):
  - `BasicAuthenticationConfig`
  - `DisableSecurityConfig`
- [ ] Create replacement `SecurityConfig` class with `@Bean SecurityFilterChain`
- [ ] Migrate `.authorizeRequests()` → `.authorizeHttpRequests()`
- [ ] Migrate `@EnableGlobalMethodSecurity` → `@EnableMethodSecurity`
- [ ] Migrate `configureGlobal(AuthenticationManagerBuilder)` → `@Bean AuthenticationManager`
- [ ] Verify: JDBC-backed auth, role-based access, and CORS still work

### Phase 4: OpenAPI/Swagger Migration
- [ ] Remove SpringFox dependencies (`springfox-boot-starter`, `springfox-swagger2`)
- [ ] Add SpringDoc dependency (`springdoc-openapi-starter-webmvc-ui`)
- [ ] Migrate Swagger annotations: `@Api` → `@Tag`, `@ApiOperation` → `@Operation`
- [ ] Migrate `@ApiResponse` from `io.swagger` to `io.swagger.v3.oas`
- [ ] Update `ApplicationSwaggerConfig` to SpringDoc configuration
- [ ] Verify: Swagger UI accessible at `/swagger-ui.html`

### Phase 5: Virtual Threads & Validation
- [ ] Add to `application.properties`: `spring.threads.virtual.enabled=true`
- [ ] Review any `@Async` methods — Virtual Threads make custom thread pools unnecessary for I/O-bound work
- [ ] Run full test suite: `mvn clean verify`
- [ ] Verify no Spring Boot deprecation warnings in startup logs

## What the Agent Should Do

This PRD is designed to test the agent's ability to:

1. **Bootstrap its own context** — use codebase investigation to write a GEMINI.md before starting migration work (Phase 0)
2. **Understand the full codebase** — needs the 1M context window to see all files simultaneously
3. **Follow a phased plan** — Conductor should generate a plan matching these phases
4. **Perform mechanical refactoring** — namespace migration is repetitive and error-prone for humans
5. **Verify its own work** — run `mvn clean verify` after each phase and fix any breakages
6. **Know current APIs** — the Security migration requires knowledge of Spring Security 6 patterns (use Developer Knowledge MCP to avoid hallucinating deprecated patterns)

## Acceptance Criteria

- [ ] A `GEMINI.md` exists in the project root encoding the migration context
- [ ] `mvn clean verify` passes with 0 test failures on Java 21
- [ ] Zero `javax.*` imports remain (except `javax.sql.*`)
- [ ] No usage of `WebSecurityConfigurerAdapter` anywhere in the codebase
- [ ] SpringFox dependencies fully replaced by SpringDoc
- [ ] `application.properties` includes `spring.threads.virtual.enabled=true`
- [ ] No Spring Boot deprecation warnings in startup logs

## Target Repository

[Spring PetClinic REST](https://github.com/spring-petclinic/spring-petclinic-rest) at tag [`v2.6.2`](https://github.com/spring-petclinic/spring-petclinic-rest/tree/v2.6.2) — Spring Boot 2.6.2, Java 8, with Spring Security and OpenAPI.
