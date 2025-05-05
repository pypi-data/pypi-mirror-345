# Modification Timekeeper
Keep modification time in a Markdown file's YAML front matter up to date.

## Usage as a pre-commit hook

Add the following to your `.pre-commit-config.yaml` file:

```yaml
- repo: https://github.com/stefmolin/modification-timekeeper
  rev: 0.1.1
  hooks:
    - id: modification-timekeeper
```

You can also configure the name of the last modified field (`--field-name`), which field to put the modified field after it it doesn't already exist (`--after-key`), whether to use UTC (`--as-utc`), and the number of seconds after which the modified time in the file is considered stale (`--tolerance`):

```yaml
- repo: https://github.com/stefmolin/modification-timekeeper
  rev: 0.1.1
  hooks:
    - id: modification-timekeeper
      args: [--field-name=modified, --after-key=publication_date, --as-utc, --tolerance=30]
```

Be sure to check out the [pre-commit documentation](https://pre-commit.com/#pre-commit-configyaml---hooks) for additional configuration options.

## Contributing

Please consult the [contributing guidelines](https://github.com/stefmolin/modification-timekeeper/blob/main/CONTRIBUTING.md).
