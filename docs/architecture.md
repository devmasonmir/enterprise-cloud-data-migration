# Enterprise Cloud Data Migration Architecture

## Migration Strategy
1. **Zero Downtime**: Employs historical backfills coupled with incremental CDC delta syncs.
2. **Reconciliation Auditor**: The Python utility compares exact row counts and financial aggregate totals with a strict absolute tolerance below `0.01`, using decimal arithmetic without rounding the difference. Non-finite totals raise `ValueError`. Prefer `Decimal` inputs for database financial totals. Matching aggregates do not prove primary key integrity or row-level equality; checksum verification and wiring the auditor into the Airflow cutover gate remain future work.
