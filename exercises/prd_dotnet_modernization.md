# PRD: .NET Framework → .NET 8 Cloud-Native Migration

> **Workshop Use:** Practice exercise for legacy modernization. Demonstrates Conductor planning, @architect analysis, and the Developer Knowledge MCP for current .NET 8 patterns.

## Problem

A Windows-bound ASP.NET Framework 4.8 application runs on dedicated VMs. Deployments take 2-3 hours with manual IIS configuration. The application can't scale horizontally, and Windows Server licensing costs $15K/year per instance.

## Business Drivers

| Driver | Impact |
|:---|:---|
| **Licensing** | Eliminate Windows Server licensing — Linux containers on Cloud Run cost ~70% less |
| **Deployment speed** | From 2-3 hours (manual IIS) to 3 minutes (container push) |
| **Scalability** | Cloud Run auto-scales from 0 to N instances based on traffic |
| **Maintainability** | .NET Framework 4.8 receives only security fixes — no new features or performance improvements |

## Target Repository

[Google Cloud .NET Modernization Demo](https://github.com/GoogleCloudPlatform/cloud-solutions/tree/main/projects/dotnet-modernization-demo)

## Scope

### In Scope
- Upgrade project files from .NET Framework 4.8 to .NET 8
- Replace `System.Web` with `Microsoft.AspNetCore`
- Migrate Entity Framework 6 to Entity Framework Core 8
- Replace `web.config` with `appsettings.json`
- Replace In-Memory Session with Redis (Memorystore)
- Create a Linux-based Dockerfile
- Deploy to Cloud Run

### Out of Scope
- Database schema migration (EF Core should map to the existing schema)
- Rewriting the frontend (if any — just ensure it compiles)
- Performance optimization beyond the migration

## Migration Checklist

### Phase 1: Project File Modernization
- [ ] Convert `.csproj` from the verbose XML format to SDK-style:
  ```xml
  <Project Sdk="Microsoft.NET.Sdk.Web">
    <PropertyGroup>
      <TargetFramework>net8.0</TargetFramework>
    </PropertyGroup>
  </Project>
  ```
- [ ] Remove `packages.config` — move all dependencies to `<PackageReference>` in `.csproj`
- [ ] Delete `AssemblyInfo.cs` — properties move to `.csproj`
- [ ] Run `dotnet restore` — resolve any missing packages

### Phase 2: Framework API Replacement
- [ ] Replace `System.Web.HttpContext` → `Microsoft.AspNetCore.Http.HttpContext`
- [ ] Replace `System.Web.Mvc.Controller` → `Microsoft.AspNetCore.Mvc.Controller`
- [ ] Replace `Global.asax` startup code → `Program.cs` with `WebApplication.CreateBuilder()`
- [ ] Replace `web.config` → `appsettings.json` for all config values
- [ ] Replace `ConfigurationManager.AppSettings["key"]` → `IConfiguration` injection
- [ ] Add `builder.Services.AddControllersWithViews()` in `Program.cs`

### Phase 3: Entity Framework Migration
- [ ] Remove `EntityFramework` 6.x package
- [ ] Add `Microsoft.EntityFrameworkCore` and `Microsoft.EntityFrameworkCore.SqlServer` (or `.Npgsql` for PostgreSQL)
- [ ] Update `DbContext`:
  - Remove `Database.SetInitializer<T>(null)`
  - Add `OnConfiguring` or use `AddDbContext` in `Program.cs`
- [ ] Replace `DbModelBuilder` fluent API with `ModelBuilder` (most syntax is similar)
- [ ] Run existing tests to verify query behavior is preserved

### Phase 4: Session State & Caching
- [ ] Remove In-Memory Session dependency
- [ ] Add `Microsoft.Extensions.Caching.StackExchangeRedis`
- [ ] Configure distributed session in `Program.cs`:
  ```csharp
  builder.Services.AddStackExchangeRedisCache(options =>
  {
      options.Configuration = builder.Configuration["Redis:ConnectionString"];
  });
  builder.Services.AddSession();
  ```
- [ ] Replace all `HttpContext.Session["key"]` usage with the new `ISession` API

### Phase 5: Containerization & Deployment
- [ ] Create a multi-stage `Dockerfile`:
  ```dockerfile
  FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
  WORKDIR /src
  COPY . .
  RUN dotnet publish -c Release -o /app

  FROM mcr.microsoft.com/dotnet/aspnet:8.0
  WORKDIR /app
  COPY --from=build /app .
  USER 1000
  EXPOSE 8080
  ENTRYPOINT ["dotnet", "MyApp.dll"]
  ```
- [ ] Add `.dockerignore` (exclude `bin/`, `obj/`, `.git/`)
- [ ] Replace hardcoded connection strings with Google Cloud Secret Manager references
- [ ] Run `docker build` and `docker run` locally to verify
- [ ] Deploy: `gcloud run deploy --source .`

## What the Agent Should Do

1. **@architect**: Analyze the legacy codebase and produce a dependency map showing which files reference `System.Web`, EF6, and `web.config`
2. **Conductor**: Generate a phased plan matching the checklist above
3. **@implementer**: Execute each phase, running `dotnet build` after each to catch errors early
4. **Developer Knowledge MCP**: Look up current .NET 8 migration patterns instead of hallucinating deprecated APIs
5. **@security-scanner**: Scan the final code for hardcoded credentials that should be in Secret Manager

## Acceptance Criteria

- [ ] `dotnet build` compiles without errors or warnings
- [ ] `dotnet test` passes all existing tests
- [ ] Docker image builds and runs on Linux (not Windows containers)
- [ ] Container runs as non-root user (UID 1000)
- [ ] No connection strings or credentials in source code — all in Secret Manager or environment variables
- [ ] `gcloud run deploy` completes with 0 configuration warnings
- [ ] Application responds to health check at `/health` within 2 seconds of cold start
