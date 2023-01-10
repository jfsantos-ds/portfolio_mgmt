.PHONY: setup
setup:
	@ echo "Setting up package..."
	@ poetry install

.PHONY: clean
clean:
	@ rm -rf __pycache__

