
test-102:
	uv run pytest --timeout 2.0 --address 192.168.56.102

test-activ-vm:
	tests/run_test_on_vm.sh
test-ip:
	uv run pytest --timeout 5.0 --address $(IP)

lint:
	uvx ruff check --fix --config ./pyproject.toml .

format:
#	uv run ruff format
	uvx black . --config ./pyproject.toml

fix_spelling:
	uv run codespell --toml pyproject.toml

build:
	uv build

msgfmt:
	msgfmt ./pyLSV2/locales/en/LC_MESSAGES/error_text.po -o ./pyLSV2/locales/en/LC_MESSAGES/error_text.mo
	msgfmt ./pyLSV2/locales/en/LC_MESSAGES/message_text.po -o ./pyLSV2/locales/en/LC_MESSAGES/message_text.mo
	msgfmt ./pyLSV2/locales/de/LC_MESSAGES/error_text.po -o ./pyLSV2/locales/de/LC_MESSAGES/error_text.mo
	msgfmt ./pyLSV2/locales/de/LC_MESSAGES/message_text.po -o ./pyLSV2/locales/de/LC_MESSAGES/message_text.mo

doc:
	cd docs && $(MAKE) html


all: lint format fix_spelling msgfmt doc build
