# Copier Templates

This file lists available Copier templates for bootstrapping new projects.

## Template Registry

| Project Type | Template URL | Description |
|-------------|-------------|-------------|
| fastapi | TBD | FastAPI service with layered architecture |
| rabbitmq-worker | TBD | RabbitMQ worker service |
| cli-tool | TBD | Command-line tool with proper packaging |
| react-frontend | TBD | React frontend application |
| aws-lambda | TBD | AWS Lambda function |
| google-cloud-function | TBD | Google Cloud Function |

## Template URL Format

Templates can be specified as:
- GitHub URL: `gh:user/repo` or `https://github.com/user/repo`
- Local path: `/path/to/template`
- Git URL: `git@github.com:user/repo.git`

## Adding New Templates

To add a new template:
1. Add a row to the table above with:
   - Project type identifier (lowercase-with-hyphens)
   - Template repository URL
   - Brief description
2. Update the skill by editing this file

## Template Conventions

Each template should include:
- `AGENTS.md` - Conventions and guidance for AI agents
- `copier.yml` - Template configuration and questions
- Default answers that produce a working project
