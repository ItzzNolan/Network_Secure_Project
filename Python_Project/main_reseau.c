#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <errno.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include "ipc_c.h"
#include "udprecv.h"


int main(int argc, char **argv){
	char *msg;
	pid_t status;
    int sock_ipc = socket(AF_INET, SOCK_DGRAM, 0);
    struct sockaddr_in addr_ipc;
    memset(&addr_ipc, 0, sizeof(addr_ipc));
    addr_ipc.sin_family = AF_INET;
    addr_ipc.sin_addr.s_addr = INADDR_ANY;
    addr_ipc.sin_port = htons(9999);
    bind(sock_ipc, (struct sockaddr*)&addr_ipc, sizeof(addr_ipc));
	status=fork();
	switch (status){
		case -1 :
			perror("Probleme dans le fork");
			exit(EXIT_FAILURE);
		case 0 :
            printf("[TEST] Message vient du RESEAU\n");
			udp_recv();
		default :
			do{
                printf("[TEST] Message vient de PYTHON\n");
				msg = i1_traiter_entree_python(sock_ipc);
				i1_envoyer_message(msg,1);
			}while(1);
	}
	exit(EXIT_SUCCESS);
}
