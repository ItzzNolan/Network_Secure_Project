#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/select.h>
#include <cjson/cJSON.h>
#include "ipc_c.h"


#define PORT_C_ENTREE 9999   // Le C écoute Python 
#define PORT_PY_SORTIE 9998  // Le C parle à Python 
#define PORT_RESEAU 12345
#define BUF_SIZE 4096


/**
 * Envoi ciblé (Amélioration)
 * Permet d'envoyer soit à Python, soit en Broadcast, soit à une IP précise.
 */
int i1_envoyer_destination(const char *data, const char *ip_dest, int port_dest, int is_broadcast) {
    int sockfd;
    struct sockaddr_in addr;


    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) return -1;


    if (is_broadcast) {
        int broadcast = 1;
        setsockopt(sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast));
    }


    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port_dest);
    inet_aton(ip_dest, &addr.sin_addr);


    int res = sendto(sockfd, data, strlen(data), 0, (struct sockaddr*)&addr, sizeof(addr));
    close(sockfd);
    return (res < 0) ? -1 : 0;
}


/**
 * Logique de routage
 * Analyse le JSON pour décider où envoyer le message.
 */
void i1_router_message_python(char *raw_json) {
    cJSON *json = cJSON_Parse(raw_json);
    if (!json) return;


    cJSON *type = cJSON_GetObjectItemCaseSensitive(json, "type");
    if (!cJSON_IsString(type)) {
        cJSON_Delete(json);
        return;
    }


    // 1. CAS BROADCAST : UPDATE, JOIN, DISCONNECT
    if (strcmp(type->valuestring, "UPDATE") == 0 || strcmp(type->valuestring, "JOIN") == 0) {
        printf("[V2] Routage : Diffusion générale pour %s\n", type->valuestring);
        i1_envoyer_destination(raw_json, "255.255.255.255", PORT_RESEAU, 1);
    }


    // 2. CAS CIBLÉ (UNICAST) : GRANT_PROP, DENY_PROP
    else if (strcmp(type->valuestring, "GRANT_PROP") == 0 || strcmp(type->valuestring, "DENY_PROP") == 0) {
        // Ici, en V3, on cherchera l'IP du joueur dans une table.
        // Pour l'instant, on simule l'envoi ciblé.
        printf("[V2] Routage : Envoi ciblé pour %s\n", type->valuestring);
        // i1_envoyer_destination(raw_json, "IP_DU_JOUEUR", PORT_RESEAU, 0);
    }


    cJSON_Delete(json);
}


/**
 * TRAITEMENT DES ENTRÉES (Version non-bloquante pour select)
 */
void i1_ecouter_canaux(int fd_python, int fd_reseau) {
    fd_set readfds;
    char buffer[BUF_SIZE];
    struct sockaddr_in cliaddr;
    socklen_t len = sizeof(cliaddr);


    while (1) {
        FD_ZERO(&readfds);
        FD_SET(fd_python, &readfds);
        FD_SET(fd_reseau, &readfds);


        int max_fd = (fd_python > fd_reseau) ? fd_python : fd_reseau;


        // select attend qu'un des deux sockets reçoive quelque chose
        int activity = select(max_fd + 1, &readfds, NULL, NULL, NULL);


        if (activity > 0) {
            // A. Si ça vient de Python -> On route vers le réseau
            if (FD_ISSET(fd_python, &readfds)) {
                int n = recvfrom(fd_python, buffer, BUF_SIZE - 1, 0, (struct sockaddr *)&cliaddr, &len);
                if (n > 0) {
                    buffer[n] = '\0';
                    i1_router_message_python(buffer);
                }
            }


            // B. Si ça vient du Réseau -> On envoie à Python Local
            if (FD_ISSET(fd_reseau, &readfds)) {
                int n = recvfrom(fd_reseau, buffer, BUF_SIZE - 1, 0, (struct sockaddr *)&cliaddr, &len);
                if (n > 0) {
                    buffer[n] = '\0';
                    printf("[V2] Réseau -> Python : %s\n", buffer);
                    i1_envoyer_destination(buffer, "127.0.0.1", PORT_PY_SORTIE, 0);
                }
            }
        }
    }
}


