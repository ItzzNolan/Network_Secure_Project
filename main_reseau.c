#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include "ipc_c.h"
#include "udprecv.h"

int main(int argc, char **argv){
	char *msg;
	pid_t status;
	status=fork();
	switch (status){
		case -1 :
			perror("Probleme dans le fork");
			exit(EXIT_FAILURE);
		case 0 :
			udp_recv();
		default :
			do{
				msg = i1_traiter_entree_python(PORT_PY_LOCAL);
				i1_envoyer_message(msg,1);
			}while(1);
	}
	exit(EXIT_SUCCESS);
}
