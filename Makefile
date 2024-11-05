all: run_game 
	cd src

run_game: check_node
	cd 3D_Game/src && npm start

# Define the check_node target to verify Node.js and npm installation
check_node:
	@if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then \
		echo "Node.js or npm not found, running install..."; \
		$(MAKE) install; \
	else \
		echo "Node.js and npm are installed."; \
	fi

# Install Node.js and dependencies if needed
install:
	sudo apt-get update
	sudo apt-get install -y nodejs npm
	cd 3D_Game/src && npm install