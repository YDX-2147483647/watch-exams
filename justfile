set dotenv-load
set windows-shell := ["pwsh", "-NoLogo", "-Command"]

python := env_var_or_default('PYTHON', 'python')


# List available recipes
@default:
    just --list

# Update the message
update *options:
	{{ python }} main.py --verbose {{ options }}

# Update the message and send to Ding
update-ding *options:
	{{ python }} main.py --verbose --ding {{ options }}

# See what has changed in VS Code
diff:
	code --diff output/message-old.txt output/message.txt
