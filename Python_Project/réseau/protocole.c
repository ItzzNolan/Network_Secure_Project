#include <stdint.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/udp.h>
#include <netdb.h>
#include <strings.h>
#include <unistd.h>
#include <time.h>
#include <arpa/inet.h>

#define PORT 12345
#define MAX_DGRAM_SIZE 1400

// socket persistant pour pas le recréer à chaque appel
static int sockfd = -1;
static int bound = 0;

void stop(char *s){
   perror(s);
   exit(1);
}

int udp_recv(void *data, size_t max_len){
    // créer le socket une seule fois
    if (sockfd == -1) {
        sockfd = socket(AF_INET, SOCK_DGRAM, 0);
        if (sockfd < 0) {
            stop("error socket");
        }
    }

    // bind une seule fois
    if (!bound) {
        int opt = 1;
        setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        struct sockaddr_in serv_addr;
        bzero(&serv_addr, sizeof(serv_addr));
        serv_addr.sin_addr.s_addr = INADDR_ANY;
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(PORT);

        if (bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
            stop("Error on binding");
        }
        bound = 1;
    }

    struct sockaddr_in cli_addr;
    socklen_t addrlen = sizeof(cli_addr);

    int nbbytes = recvfrom(sockfd, data, max_len, 0,
                           (struct sockaddr*)&cli_addr, &addrlen);
    if (nbbytes < 0) {
        stop("error recvfrom");
    }

    return nbbytes;
}

char* message_receive() {
    char buffer[MAX_DGRAM_SIZE];

    int recv_len = udp_recv(buffer, sizeof(buffer));
    if (recv_len <= 0) {
        return NULL;
    }

    int header_size = sizeof(uint32_t) + 2 * sizeof(uint16_t);

    // pas de fragmentation, 1 seul paquet
    if (recv_len < header_size) {
        char *msg = malloc(recv_len + 1);
        memcpy(msg, buffer, recv_len);
        msg[recv_len] = '\0';
        return msg;
    }

    // lire le header
    uint32_t msg_id = ntohl(*(uint32_t*)buffer);
    uint16_t total  = ntohs(*(uint16_t*)(buffer + sizeof(uint32_t)));
    uint16_t index  = ntohs(*(uint16_t*)(buffer + sizeof(uint32_t) + sizeof(uint16_t)));

    // allocation pour les fragments
    char **fragments = calloc(total, sizeof(char*));
    int *sizes = calloc(total, sizeof(int));

    // stocker 1er fragment
    int payload_size = recv_len - header_size;
    fragments[index] = malloc(payload_size);
    memcpy(fragments[index], buffer + header_size, payload_size);
    sizes[index] = payload_size;

    int received = 1;

    // recevoir les autres fragments
    while (received < total) {
        recv_len = udp_recv(buffer, sizeof(buffer));
        if (recv_len <= 0) continue;

        uint32_t mid = ntohl(*(uint32_t*)buffer);
        if (mid != msg_id) continue;

        uint16_t idx = ntohs(*(uint16_t*)(buffer + sizeof(uint32_t) + sizeof(uint16_t)));
        if (fragments[idx] != NULL) continue;

        int size = recv_len - header_size;
        fragments[idx] = malloc(size);
        memcpy(fragments[idx], buffer + header_size, size);
        sizes[idx] = size;

        received++;
    }

    // réassembler les fragments
    int total_size = 0;
    for (int i = 0; i < total; i++) {
        total_size += sizes[i];
    }

    char *message = malloc(total_size + 1);
    int offset = 0;

    for (int i = 0; i < total; i++) {
        memcpy(message + offset, fragments[i], sizes[i]);
        offset += sizes[i];
        free(fragments[i]);
    }

    message[total_size] = '\0';

    free(fragments);
    free(sizes);

    return message;
}

int main(int argc, char *argv[]) {
    char *message = message_receive();
    if (message) {
        printf("Reçu : %s\n", message);
        free(message);
    }
    return 0;
}