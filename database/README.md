# Database scripts

- `schema.sql` creates the application tables and indexes.
- `test_seed.sql` resets and seeds a dedicated test database with synthetic data.

Create a database whose name ends in `_test`, apply `schema.sql`, and copy
`.env.test.example` to `.env.test` with your local PostgreSQL credentials.

```powershell
psql -U postgres -d neighbourhood_library_test -f database/schema.sql
psql -U postgres -d neighbourhood_library_test -f database/test_seed.sql
pytest backend/tests
```

The test suite truncates and reseeds its configured database before every test.
Its safety check refuses to run unless `DB_NAME` ends in `_test`.
