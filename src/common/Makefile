build-CommonLayer:
	python3 ./setup.py build
	pip3 wheel -w tmp -e .
	mkdir $(ARTIFACTS_DIR)/python
	pip3 install tmp/common-* --target $(ARTIFACTS_DIR)/python/
