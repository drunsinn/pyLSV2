test-101:
	uv run pytest --timeout 2.0 --address 192.168.56.101

test-102:
	uv run pytest --timeout 2.0 --address 192.168.56.102

test-103:
	uv run pytest --timeout 2.0 --address 192.168.56.103

test-104:
	uv run pytest --timeout 2.0 --address 192.168.56.104

lint:
	uv run ruff check

format:
#	uv run ruff format
	uv run black . --config ./pyproject.toml

build:
	uv build

msgfmt:
	msgfmt ./pyLSV2/locales/en/LC_MESSAGES/error_text.po -o ./pyLSV2/locales/en/LC_MESSAGES/error_text.mo
	msgfmt ./pyLSV2/locales/en/LC_MESSAGES/message_text.po -o ./pyLSV2/locales/en/LC_MESSAGES/message_text.mo
	msgfmt ./pyLSV2/locales/de/LC_MESSAGES/error_text.po -o ./pyLSV2/locales/de/LC_MESSAGES/error_text.mo
	msgfmt ./pyLSV2/locales/de/LC_MESSAGES/message_text.po -o ./pyLSV2/locales/de/LC_MESSAGES/message_text.mo

doc:
	cd docs && $(MAKE) html
