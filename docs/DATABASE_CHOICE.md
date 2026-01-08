# Database Choice: SQLite vs PostgreSQL

## Recommendation: SQLite for Personal Use

For a **personal, single-user** trading system, **SQLite is the recommended choice** and is now the default.

## Why SQLite?

### Advantages for Personal Use:
1. ✅ **Zero Setup** - No separate server process needed
2. ✅ **Single File** - Database is just one file (`data/stockport.db`)
3. ✅ **No Configuration** - Works out of the box
4. ✅ **Sufficient Performance** - More than enough for personal trading
5. ✅ **Easy Backup** - Just copy the database file
6. ✅ **Portable** - Move the file anywhere
7. ✅ **No Password Management** - No authentication needed

### When SQLite is Perfect:
- Single user (you)
- Personal trading system
- No concurrent access from multiple applications
- Moderate data volume (< 100GB typically)
- Local deployment

## PostgreSQL (Optional)

PostgreSQL is available if you prefer it, but **not necessary** for personal use.

### When PostgreSQL Makes Sense:
- You already have it set up and prefer it
- You want to practice with PostgreSQL
- Future multi-user expansion (unlikely for personal use)
- Very large datasets (> 100GB)

## Current Setup

The system now:
- **Defaults to SQLite** (no configuration needed)
- **Supports PostgreSQL** as an optional alternative
- **Automatically converts** schema between both

## Quick Start

### SQLite (Default - Recommended):
```bash
# Just run this - no setup needed!
python database/init_db.py
```

### PostgreSQL (Optional):
```bash
# Set in .env file:
# DATABASE_TYPE=postgresql
# POSTGRES_PASSWORD=admin

python database/init_db.py --postgresql
```

## Your Current Setup

Since you mentioned PostgreSQL is already installed with password "admin", you can:

1. **Use SQLite (Recommended)**: Just run `python database/init_db.py` - no config needed
2. **Use PostgreSQL (Optional)**: Set `DATABASE_TYPE=postgresql` in `.env` and use password "admin"

Both work perfectly! SQLite is simpler for personal use.

