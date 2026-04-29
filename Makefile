CC = gcc
CFLAGS = -g -W -Wall
LDFLAGS = -lcjson
OBJ = main_reseau.o ipc_c.o udprecv.o

main_reseau: $(OBJ)
	$(CC) $(OBJ) $(CFLAGS) -o main_reseau $(LDFLAGS)

ipc_c.o: ipc_c.c ipc_c.h
udprecv.o: udprecv.c ipc_c.h
main_reseau.o: main_reseau.c ipc_c.h udprecv.h

clean:
	rm -f $(OBJ) main_reseau
