# Active Handoff Docs And Experiment Record Policy v1

## Purpose

This policy separates global handoff state from experiment history.

## Handoff Docs

The handoff docs exist only for information that must be read when work is resumed.

That means:

- active route state
- still-active global risks
- current process rules
- current next allowed action

The handoff docs must not accumulate routine experiment logs.

## What `docs/01_project_overview_and_plan.md` Is Allowed To Hold

`docs/01_project_overview_and_plan.md` may hold:

- current project scope
- current main-line route
- current process state
- current task hold or next allowed action
- links to the current active checkpoint docs

It must not hold long chronological experiment logs.

## What `docs/02_pitfalls_log.md` Is Allowed To Hold

`docs/02_pitfalls_log.md` may hold only still-active global pitfalls, such as:

- environment traps
- encoding traps
- Git boundary traps
- identifier stability rules

It must not hold resolved local history that no longer matters during handoff.

## Experiment Record Rule

From this policy forward:

- one experiment record gets one new numbered doc
- one route checkpoint gets one new numbered doc
- do not append routine experiment history into `docs/01_project_overview_and_plan.md`
- do not append experiment outcomes into `docs/02_pitfalls_log.md`

## Archive Split Performed In This Task

Oversized historical content was split out of the old large handoff docs into archive docs:

- `docs/66_archive_repo_state_and_asset_inventory_from_old_01_v1.md`
- `docs/67_archive_route_progress_log_from_old_01_v1.md`
- `docs/68_archive_historical_pitfalls_from_old_02_v1.md`

These archive docs preserve historical context and are not part of the active handoff read path.
