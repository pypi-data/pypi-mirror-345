# djstart

A simple CLI tool to scaffold Django projects with a virtual environment, apps, and auto-configured settings.

## Installation

```bash
pip install djstart
```

## Usage

```bash
djstart --root myproject --app blog --app users
```

- Automatically creates a virtual environment
- Installs Django
- Starts a project and apps
- Configures settings and URLs using Jinja2 templates

## License

MIT
