#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <cjson/cJSON.h>
#include "ipc_c.h"

#define PORT_PY_LOCAL 9998
#define PORT_RESEAU 12345
#define BUF_SIZE 2048

/**
 *
 * envoie le msg soit à py soit au res
 */
int i1_envoyer_message(const char *data, int vers_reseau) {
    int sockfd;
    struct sockaddr_in dest_addr;

    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) return -1;

    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.sin_family = AF_INET;

    if (vers_reseau) {
        // Mode Broadcast Réseau   si vers_reseau=1 
        int broadcast = 1;
        setsockopt(sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast));
        dest_addr.sin_port = htons(PORT_RESEAU);
        inet_aton("255.255.255.255", &dest_addr.sin_addr);
    } else {
        // Mode Local (vers Python)
        dest_addr.sin_port = htons(PORT_PY_LOCAL);
        inet_aton("127.0.0.1", &dest_addr.sin_addr);
    }

    int res = sendto(sockfd, data, strlen(data), 0, (struct sockaddr*)&dest_addr, sizeof(dest_addr));
    close(sockfd);
    return (res < 0) ? -1 : 0;
}

/**
 * À appeler quand il y a des données sur le port 9999.
 * Elle ne boucle pas : elle traite UN message et rend la main.
 */
char* i1_traiter_entree_python(int fd_ipc) {
    static char buffer[BUF_SIZE];
    struct sockaddr_in cliaddr;
    socklen_t len = sizeof(cliaddr);

    // 1. Lecture unique du socket
    int n = recvfrom(fd_ipc, buffer, BUF_SIZE - 1, 0, (struct sockaddr *)&cliaddr, &len);
    if (n <= 0) return NULL;
    buffer[n] = '\0';

    // 2. Analyse cJSON pour valider le format
    cJSON *json = cJSON_Parse(buffer);
    if (!json) {
        printf("[I1 Error] JSON malformé reçu de Python.\n");
        return NULL; 
    }

    // 3. Extraction du type pour log/vérification
    cJSON *type = cJSON_GetObjectItemCaseSensitive(json, "type");
    if (cJSON_IsString(type)) {
        printf("[I1] Message de type %s validé.\n", type->valuestring);
    }

    cJSON_Delete(json);
    
    return buffer;
}
