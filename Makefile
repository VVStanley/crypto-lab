.PHONY: doctor pull download backtest strategy-check sensitivity-check dry-run live logs stop ps config

pull:
	docker compose pull

download:
	./scripts/download-data.sh

backtest:
	./scripts/backtest.sh

strategy-check:
	./scripts/strategy-check.sh

dry-run:
	docker compose up -d bot

live:
	./scripts/live.sh

logs:
	docker compose logs -f bot

stop:
	docker compose down

ps:
	docker compose ps

config:
	docker compose config

doctor:
	./scripts/doctor.sh

sensitivity-check:
	./scripts/sensitivity-check.sh