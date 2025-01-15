ifneq ($(shell command -v docker compose 2>/dev/null),)
DOCKER_COMPOSE = docker compose
else ifneq ($(shell command -v docker-compose 2>/dev/null),)
DOCKER_COMPOSE = docker-compose
else
$(error Neither "docker compose" nor "docker-compose" found. Please install Docker Compose.)
endif
ENV_FILE = --env-file src/.env
COMPOSE = -f ./src/docker-compose.yml
COMPOSE_CMD = ${DOCKER_COMPOSE} ${COMPOSE} ${ENV_FILE}

all:
	docker run --rm -v /home/${USER}/data:/parentdir alpine sh -c "rm -rf /parentdir/lobby_db"
	mkdir -p /home/${USER}/data/lobby_db
	mkdir -p /home/${USER}/data/userdata_db
	@${COMPOSE_CMD} build --no-cache

up:
	@${COMPOSE_CMD} up || true

run: all up

down:
	@${COMPOSE_CMD} down

clean: down
	docker system prune -f

fclean:
	@${COMPOSE_CMD} down -v
	docker system prune -f --volumes

re:	fclean run

fclean-local: fclean
	docker run --rm -v /home/${USER}/data/lobby_db:/data alpine sh -c "rm -rf /data/*"
	docker run --rm -v /home/${USER}/data:/parentdir alpine sh -c "rm -rf /parentdir/lobby_db"
	docker run --rm -v /home/${USER}/data:/parentdir alpine sh -c "rm -rf /parentdir/userdata_db"

fclean-local-run: fclean-local run


.PHONY: all up run down clean fclean re reset
