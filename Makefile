SKILL_NAME := typst-technical-report
SKILL_DIR  := .agents/skills/$(SKILL_NAME)
OUT_DIR    := local_data
ZIP_FILE   := $(OUT_DIR)/$(SKILL_NAME).zip

.PHONY: zip clean

zip: $(ZIP_FILE)

$(ZIP_FILE): $(shell find $(SKILL_DIR) -type f ! -path '*/__pycache__/*' ! -name '*.pyc' ! -name '.DS_Store')
	@mkdir -p $(OUT_DIR)
	@rm -f $@
	cd $(SKILL_DIR) && zip -r ../../../$@ . \
		-x '*/__pycache__/*' \
		-x '*.pyc' \
		-x '*.pyo' \
		-x '.DS_Store'
	@echo "Created $@ ($$(du -h $@ | cut -f1))"
	@echo "Contents:"; unzip -l $@

clean:
	rm -f $(ZIP_FILE)
