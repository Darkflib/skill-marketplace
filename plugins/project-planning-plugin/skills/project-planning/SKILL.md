---
name: project-planning
description: Structured 4-step methodology for planning and breaking down new software projects. Use when starting a new project, planning an MVP, or decomposing requirements into executable sub-projects. Follows a human-in-the-loop gated process with clear deliverables at each stage.
---

# Project Planning Methodology

## Overview

Provides a systematic 4-step workflow for planning software projects from initial concept through to executable sub-project definitions. Each step produces specific deliverables and requires user approval before proceeding to the next stage.

## Process Principles

**Human-in-the-Loop Gating**: Stop after each step for user feedback. Never proceed to the next step without explicit user approval.

**Progressive Refinement**: Each step builds on the output of the previous one. If requirements for a step aren't available, prompt the user to provide them.

**Modular Delivery**: Break work into small, testable, independently deployable chunks with clearly defined interfaces.

## Step 1: Understand the Problem

**Objective**: Establish clear understanding of what we're building and why.

**Deliverables**:

1. **Concise Project Summary**
   - One paragraph capturing the core problem and proposed solution
   - Key stakeholders and their needs
   - Success criteria for the project

2. **MoSCoW Analysis for MVP**
   - **Must Have**: Core features essential for MVP (absolute minimum)
   - **Should Have**: Important features for next version(s)
   - **Could Have**: Nice-to-haves for future consideration
   - **Won't Have**: Explicitly out of scope to avoid painting ourselves into a corner

3. **Constraints**
   - Required technologies (languages, frameworks, databases)
   - Deployment platforms (K3s, Cloud Run, AWS, etc.)
   - Integration requirements (existing APIs, services)
   - Performance/scale requirements
   - Security/compliance requirements
   - Budget/timeline constraints

**Stop here and wait for user approval before proceeding.**

## Step 2: Consider Possible Solutions

**Objective**: Explore solution space and select the optimal approach.

**Deliverables**:

1. **One-Three-One Document**
   - **Problem Statement**: Refined problem definition
   - **Three Potential Solutions**: 
     - Solution A: [Description, pros, cons, complexity]
     - Solution B: [Description, pros, cons, complexity]
     - Solution C: [Description, pros, cons, complexity]
   - **One Recommendation**: Selected solution with justification

2. **Solution Architecture Overview**
   - High-level component diagram
   - Data flow between components
   - External dependencies and integrations

3. **Information Gaps**
   - **Known**: Technologies, patterns, APIs we're confident about
   - **Unknown**: Information we need to gather
     - Specific language/framework versions
     - Hosting requirements and costs
     - Third-party API capabilities/pricing
     - Performance characteristics
     - Integration complexity
   - **Risks**: Potential blockers or unknowns that could derail the project

**Stop here and wait for user approval before proceeding.**

## Step 3: Define a Plan

**Objective**: Create an executable roadmap with clear dependencies.

**Deliverables**:

1. **Finalized Tech Stack**
   - Languages and versions
   - Frameworks and libraries
   - Databases and storage
   - Infrastructure and hosting
   - CI/CD tooling
   - Monitoring and observability

2. **MVP Feature Set**
   - Minimum features required for first deployment
   - Acceptance criteria for each feature
   - Definition of "done" for MVP

3. **Dependency Graph**
   - Visual representation of sub-projects and their dependencies
   - Critical path identification
   - Parallelization opportunities

4. **Sub-Project Breakdown**
   
   Break the project into independently deliverable modules:
   
   - **Backend API**: REST/GraphQL endpoints
   - **Frontend/UI**: Web templates, React components
   - **Workers**: Background jobs, message processors
   - **Integrations**: Third-party API clients
   - **Infrastructure**: Docker configs, K8s manifests, CI/CD pipelines
   - **Shared Libraries**: Reusable packages (e.g., API clients, auth helpers)
   
   For each sub-project:
   - Clear scope and boundaries
   - Defined interfaces (API contracts, function signatures)
   - Dependencies on other sub-projects
   - Independent testability
   - Reusability potential

5. **Package Strategy**
   
   Identify opportunities for reusable packages:
   - API client libraries (if no suitable 3rd party package exists)
   - Common utilities (auth, logging, config management)
   - Shared data models
   - Consider publishing internally or publicly

6. **CI/CD Strategy**
   
   - Automated testing at each level (unit, integration, e2e)
   - Deployment pipeline design
   - Environment strategy (dev, staging, prod)
   - Rollback procedures
   - Monitoring and alerting

**Stop here and wait for user approval before proceeding.**

## Step 4: Execute the Plan

**Objective**: Produce detailed specifications for each sub-project that can be executed in parallel.

**For Each Sub-Project, Produce**:

1. **Product Requirements Document (PRD)**
   
   Agent-friendly specifications including:
   - **Purpose**: What this sub-project accomplishes
   - **Scope**: What's included and excluded
   - **Inputs**: Required data, APIs, dependencies
   - **Outputs**: Deliverables, interfaces, contracts
   - **Acceptance Criteria**: How to verify completion
   - **Technical Constraints**: Performance, security, compatibility requirements

2. **Interface Definitions**
   
   - API contracts (OpenAPI/Swagger specs)
   - Function signatures and type definitions
   - Data schemas (Pydantic models, database schemas)
   - Event/message formats
   - Configuration requirements

3. **Dependency Manifest**
   
   - Required libraries and versions
   - Environment variables
   - External services and credentials
   - Prerequisites from other sub-projects

4. **Testing Strategy**
   
   - Unit test requirements
   - Integration test scenarios
   - Mocking strategies for dependencies
   - Test coverage goals
   - Linting and code quality checks

5. **Agent-Friendly Documentation**
   
   Each sub-project needs documentation that enables:
   - **Setup**: Getting the development environment running
   - **Usage**: How to use/integrate the component
   - **Examples**: Concrete usage examples
   - **Troubleshooting**: Common issues and solutions

6. **Execution Readiness Checklist**
   
   Before a sub-project can begin:
   - [ ] All dependencies available
   - [ ] Interface contracts defined
   - [ ] PRD complete and approved
   - [ ] Testing strategy defined
   - [ ] Development environment ready
   - [ ] Agent/developer assigned

## Parallelization Strategy

**Identify Independent Work Streams**:
- Sub-projects with no dependencies can start immediately
- Sub-projects with satisfied dependencies can start in parallel
- Maintain a dependency graph to track readiness

**Example Parallel Execution**:
```
Phase 1 (Parallel):
├── Shared library: API client for Service X
├── Infrastructure: Docker configs
└── Infrastructure: CI/CD pipeline

Phase 2 (After Phase 1, Parallel):
├── Backend API (depends on: API client, Docker)
├── Frontend scaffolding (depends on: Docker)
└── Worker: Email sender (depends on: API client, Docker)

Phase 3 (After Phase 2):
└── Integration testing (depends on: all components)
```

## Quality Gates

**For Each Sub-Project**:
- Code passes linting/formatting checks
- Unit tests achieve coverage target
- Integration tests pass
- Documentation is complete
- Security scan passes
- Performance benchmarks met

**For MVP Completion**:
- All "Must Have" features implemented
- End-to-end tests pass
- Deployment successful to staging
- User acceptance testing complete
- Production deployment checklist satisfied

## Reusability Principles

**When Creating Packages**:
- Single responsibility principle
- Clear, stable interfaces
- Comprehensive documentation
- Semantic versioning
- Example usage code
- Contribution guidelines

**Package Candidates**:
- Third-party API clients
- Authentication/authorization helpers
- Configuration management
- Logging and monitoring utilities
- Data validation and transformation
- Common data models

## Example Application

**Scenario**: Build a URL monitoring service

**Step 1 Output**:
- Summary: Service that monitors URLs for availability and sends alerts
- Must Have: Check URLs every 5 minutes, email alerts on downtime
- Should Have: Dashboard, historical uptime stats
- Won't Have: Custom alerting rules, team management
- Constraints: Python, FastAPI, K3s deployment, budget $50/month

**Step 2 Output**:
- Solution A: Serverless (Cloud Run + Cloud Scheduler)
- Solution B: K3s with CronJob + FastAPI
- Solution C: Managed service (UptimeRobot)
- Recommendation: Solution B (K3s) - meets constraints, full control

**Step 3 Output**:
- Tech: Python 3.12, FastAPI, PostgreSQL, Redis, RabbitMQ
- Sub-projects: Checker worker, API server, Email worker, K8s manifests
- Dependency: Shared library → Workers → API → Deployment

**Step 4 Output**:
- PRD for Checker: "Worker that polls URLs from DB every 5 minutes..."
- Interface: `URLChecker.check(url: str) -> CheckResult`
- Tests: Mock HTTP responses, verify retry logic
- Docs: Setup, configuration, adding new URLs to monitor

## Critical Reminders

- **Always stop after each step** for user feedback
- **Never proceed without explicit approval** 
- **If information is missing**, prompt the user rather than making assumptions
- **Prioritize MVP scope** - resist scope creep
- **Design for modularity** from the start
- **Enable parallel work** through clear interfaces
- **Make everything testable** independently
