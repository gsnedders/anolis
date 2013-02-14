
all: README.html example.html

README.html: README.src.html
	./anolis --enable=xspecxref $< $@

example.html: example.src.html
	# run sub after toc rather than before it!
	./anolis --disable=sub --enable=sub $< $@
