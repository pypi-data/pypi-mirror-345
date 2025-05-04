.PHONY: all clean

all: src/pygnuregex/stub.so

src/pygnuregex/stub.so: src/pygnuregex/stub.c
	$(CC) $(CFLAGS) -fPIC -shared $< -o $@

clean:
	rm -f src/pygnuregex/stub.so
