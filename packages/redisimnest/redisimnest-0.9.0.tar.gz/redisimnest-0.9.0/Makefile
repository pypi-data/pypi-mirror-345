.PHONY: release

release:
ifndef VERSION
	$(error VERSION is required. Usage: make release VERSION=1.2.3 COMMIT_MSG="your message")
endif
ifndef COMMIT_MSG
	$(error COMMIT_MSG is required. Usage: make release VERSION=1.2.3 COMMIT_MSG="your message")
endif
	git add .
	git commit -m "$(COMMIT_MSG)"
	git push origin main
	git tag -a v$(VERSION) -m "v$(VERSION)"
	git push origin v$(VERSION)
	python -m build
	twine upload dist/*
