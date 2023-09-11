set dotenv-load := true

# `just` works with the sh provided by Git for Windows, GitHub Desktop, or Cygwin.
# If you'd rather use PowerShell (which is slower), uncomment the following line.
# set windows-shell := ["pwsh", "-NoLogo", "-Command"]

python := env_var_or_default('PYTHON', 'poetry run python')

# List available recipes
@default:
    just --list

# Update the message
update *options:
    {{ python }} -m watch_exams --verbose {{ options }}

# Update the message and send to Ding
update-ding *options:
    {{ python }} -m watch_exams --verbose --ding {{ options }}

# Reset “message.txt” to the old
undo:
    cp output/message-old.txt output/message.txt

# See what has changed in VS Code
diff:
    code --diff output/message-old.txt output/message.txt

# Format and Lint
fmt:
    -pre-commit run black --all-files
    -just --fmt --unstable
    -pre-commit run ruff --all-files
    -{{ python }} -m mypy .
