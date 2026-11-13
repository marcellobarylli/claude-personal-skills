# Request: export

Add `tasklog export`.

- Formats: `csv` and `json`, chosen with `--format` (default `csv`).
- Writes to stdout, or to a file with `--out FILE`.
- Must refuse to overwrite an existing file unless `--force` is given: exit code 1 and a message on stderr.
- CSV columns: `id,title,done,due,tags`. Tags are joined with `;`. A missing due date is empty.
- JSON: a list of task objects sorted by id.
