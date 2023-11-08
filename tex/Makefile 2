TOPTARGETS := pdf clean check

SUBDIRS := $(wildcard */.)

$(TOPTARGETS): $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS)

zip:
	find -type f -regex '\./[0-9a-zA-Z_]+/[0-9a-zA-Z_]+.pdf' | xargs zip -j pdfs.zip

.PHONY: $(TOPTARGETS) $(SUBDIRS)
