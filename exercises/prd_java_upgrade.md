# PRD: Java 8 → Java 21 & Spring Boot 3 Migration

> **Workshop Use:** Practice exercise for large-scale codebase refactoring using the 1M token context window and Conductor's planning workflow.

## Problem

An enterprise Java monolith (Spring PetClinic or equivalent) runs on Java 8 and Spring Boot 2.7.x. Java 8 reached end of public updates in 2022. The application can't use Virtual Threads, modern GC improvements, or the latest security patches. Compliance requires migration to a supported LTS version.

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
- Upgrade from Spring Boot 2.7.x to Spring Boot 3.3.x
- Migrate from javax.* to jakarta.* namespace
- Replace deprecated Security configuration
- Migrate JUnit 4 tests to JUnit 5
- Enable Virtual Threads
- Ensure all existing tests pass

### Out of Scope
- Microservice decomposition (monolith stays monolith)
- Database schema changes
- UI changes
- New feature development

## Migration Checklist

### Phase 1: Build System
- [ ] Update `pom.xml` / `build.gradle`: set `java.version` to 21
- [ ] Update Spring Boot parent to 3.3.x
- [ ] Update Spring Cloud dependencies (if present) to compatible versions
- [ ] Replace removed JDK APIs:
  - JAXB → `jakarta.xml.bind:jakarta.xml.bind-api` + Glassfish runtime
  - JAX-WS → `jakarta.xml.ws:jakarta.xml.ws-api` (if used)
  - `javax.annotation` → `jakarta.annotation:jakarta.annotation-api`
- [ ] Run `mvn clean compile` — fix all compilation errors before proceeding

### Phase 2: Namespace Migration
- [ ] Global find-and-replace: `javax.persistence` → `jakarta.persistence`
- [ ] Global find-and-replace: `javax.validation` → `jakarta.validation`
- [ ] Global find-and-replace: `javax.servlet` → `jakarta.servlet`
- [ ] Global find-and-replace: `javax.annotation` → `jakarta.annotation`
- [ ] Verify: no remaining `javax.*` imports (except `javax.sql.*` which is unchanged)

### Phase 3: Security Configuration
- [ ] Remove class extending `WebSecurityConfigurerAdapter` (deleted in Spring Security 6)
- [ ] Create a `SecurityConfig` class with `@Bean SecurityFilterChain`
- [ ] Migrate `.antMatchers()` → `.requestMatchers()`
- [ ] Migrate `.access("hasRole('ADMIN')")` → `.hasRole("ADMIN")`
- [ ] Verify: login, logout, and role-based access still work

### Phase 4: Test Migration
- [ ] Replace `junit:junit:4.x` dependency with `org.junit.jupiter:junit-jupiter:5.x`
- [ ] Add JUnit Vintage Engine if you need to run both JUnit 4 and 5 temporarily
- [ ] Migrate annotations:
  - `@Test` (org.junit.Test) → `@Test` (org.junit.jupiter.api.Test)
  - `@Before` → `@BeforeEach`
  - `@After` → `@AfterEach`
  - `@Ignore` → `@Disabled`
  - `@RunWith(SpringRunner.class)` → `@ExtendWith(SpringExtension.class)`
- [ ] Replace `Assert.assertEquals()` → `Assertions.assertEquals()`
- [ ] Replace `@Rule ExpectedException` → `assertThrows()`
- [ ] Run full test suite: `mvn clean verify`

### Phase 5: Virtual Threads
- [ ] Add to `application.properties`: `spring.threads.virtual.enabled=true`
- [ ] Review any `@Async` methods — Virtual Threads make custom thread pools unnecessary for I/O-bound work
- [ ] Load test to verify no thread-safety regressions

## What the Agent Should Do

This PRD is designed to test the agent's ability to:

1. **Understand the full codebase** — needs the 1M context window to see all files simultaneously
2. **Follow a phased plan** — Conductor should generate a plan matching these phases
3. **Perform mechanical refactoring** — namespace migration is repetitive and error-prone for humans
4. **Verify its own work** — run `mvn clean verify` after each phase and fix any breakages
5. **Know current APIs** — the Security migration requires knowledge of Spring Security 6 patterns (use Developer Knowledge MCP to avoid hallucinating deprecated patterns)

## Acceptance Criteria

- [ ] `mvn clean verify` passes with 0 test failures on Java 21
- [ ] Zero `javax.*` imports remain (except `javax.sql.*`)
- [ ] No usage of `WebSecurityConfigurerAdapter` anywhere in the codebase
- [ ] All tests use JUnit 5 annotations and assertions
- [ ] `application.properties` includes `spring.threads.virtual.enabled=true`
- [ ] No Spring Boot deprecation warnings in startup logs

## Target Repository

[Spring PetClinic](https://github.com/spring-projects/spring-petclinic) — or clone and pin to a known Spring Boot 2.7.x commit for reproducibility.
