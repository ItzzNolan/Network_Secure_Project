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

int main(int argc, char **argv)
{
	char *msg;
	pid_t status;

	int sock_ipc = socket(AF_INET, SOCK_DGRAM, 0);
	if (sock_ipc < 0)
	{
		perror("[ERREUR C] Impossible de créer le socket");
		exit(EXIT_FAILURE);
	}

	struct sockaddr_in addr_ipc;
	memset(&addr_ipc, 0, sizeof(addr_ipc));
	addr_ipc.sin_family = AF_INET;
	addr_ipc.sin_addr.s_addr = INADDR_ANY;
	addr_ipc.sin_port = htons(9999);
	if (bind(sock_ipc, (struct sockaddr *)&addr_ipc, sizeof(addr_ipc)) < 0)
	{
		perror("\n[ERREUR FATALE C] Le port 9999 est déjà utilisé ! (Processus zombie)");
		printf("Astuce : Tape 'killall main_reseau' dans ton terminal pour nettoyer.\n\n");
		exit(EXIT_FAILURE);
	}

	status = fork();
	switch (status)
	{
	case -1:
		perror("[ERREUR C] Probleme dans le fork");
		exit(EXIT_FAILURE);
	case 0:
		printf("[RESEAU C] Lancement de l'ecoute UDP (Enfant)...\n");
		udp_recv();
		exit(EXIT_SUCCESS);
	default:
		printf("[IPC C] Lancement de l'ecoute Python (Parent)...\n");
		do
		{
			msg = i1_traiter_entree_python(sock_ipc);
			if (msg != NULL && strlen(msg) > 0)
			{
				i1_envoyer_message(msg, 1);
			}
			else
			{
				usleep(10000);
			}
		} while (1);
	}
	exit(EXIT_SUCCESS);
}