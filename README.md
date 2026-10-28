# harlequin-oracle

Oracle database adapter for [Harlequin](https://github.com/tconbeer/harlequin) — a fast, beautiful SQL terminal client.

## Features

- **Hierarchical catalog tree**: schema → tables, views, functions, procedures, packages, indexes, synonyms, sequences
- **Package subprograms**: expand packages to see their nested functions and procedures
- **Column details**: expand tables/views to see column names, types, and nullability
- **Rich context menu interactions** (right-click any object):

| Interaction | Description |
|---|---|
| Insert Columns at Cursor | Select column names into the query buffer |
| Preview Data | `SELECT * FROM ... WHERE rownum <= 100` |
| Count Rows | `SELECT COUNT(*) FROM ...` |
| Describe | Query `user_tab_columns` for type info |
| Show DDL | `DBMS_METADATA.GET_DDL` |
| Next Value | `SELECT seq.NEXTVAL FROM DUAL` |
| Copy Qualified Name | `quoted_identifiers` at cursor |
| Drop Table / Drop View | Confirmation-based DROP |
| Open in New Buffer | Open query in a new editor buffer |
| Insert Name at Cursor | Generic name insertion |

## Install

### System-wide (all users)

```bash
sudo -H python3.11 -m pip install harlequin
sudo -H python3.11 -m pip install harlequin-oracle
```

System-wide install available to all users.

### Per-user install

```bash
python3.11 -m pip install --user harlequin
python3.11 -m pip install --user harlequin-oracle
```

Installed to `~/.local/bin`, only available to the current user. Ensure `~/.local/bin` is on `$PATH` if `harlequin` isn't found.

Requires Python 3.11 and Oracle Instant Client libraries.

## Usage

### OS Authentication

Set `username = "os"` (the default) for OS auth, equivalent to `sqlplus /`.

Create `~/.config/harlequin/harlequin.toml`:

```toml
[profiles.dev]
adapter = "oracle"
username = "os"
host = "db.example.com"
port = 1521
service_name = "pdb1"
```

Then connect:

```bash
harlequin -P pdb1
```

### Password Authentication

```toml
[profiles.dev]
adapter = "oracle"
username = "scott"
password = "tiger"
host = "db.example.com"
port = 1521
service_name = "pdb1"
```

## Catalog Types

| Type | Type Label | Description |
|------|-----------|-------------|
| Tables | `t` | Base table |
| Views | `v` | Materialized and regular views |
| Functions | `fn` | Standalone functions |
| Procedures | `pr` | Standalone procedures |
| Packages | `pk` | Package specs |
| Subprograms | `sub` | Package functions/procedures |
| Indexes | `ix` | Index definitions |
| Synonyms | `sn` | Private synonyms |
| Sequences | `sq` | Sequence definitions |
| Columns | `col` | Table/view columns |

## Catalog Search

Type in the search bar to filter objects by name. Searching supports `relations`, `columns`, and `all` kinds.

## Architecture

Single-file package with sibling modules:

| Module | Contents |
|--------|----------|
| `harlequin_oracle.py` | Adapter, connection, cursor, options, DDL/query helpers |
| `catalog.py` | Hierarchical catalog dataclasses |
| `interactions.py` | Context menu handler functions |

## Development

```bash
# Clone and install in editable mode
cd harlequin-oracle
pip install -e .

# Run harlequin pointing to the profile
harlequin -P <profile_name>
```

## License

MIT. See [LICENSE](LICENSE).
