#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>

#define CHUNK_SIZE 1400
#define MAX_FRAGMENTS 1024

typedef struct {
    uint16_t total_frag;
    uint16_t frag_index;
} udp_header_t;

message_recv(int fd, char *buffer, int buffer_size, struct sockaddr_in *sender){
    static char *fragments[MAX_FRAGMENTS];
    static int received_count = 0;
    static int total_frag = 0;
    static int init = 0;

    if (!init) {
        for (int i = 0; i < MAX_FRAGMENTS; i++)
            fragments[i] = NULL;
        init = 1;
    }

    char recv_buf[CHUNK_SIZE + sizeof(udp_header_t)];
    socklen_t addr_len = sizeof(*sender);

    int bytes = recvfrom(fd, recv_buf, sizeof(recv_buf), 0,
                         (struct sockaddr*)sender, &addr_len);
    if (bytes < sizeof(udp_header_t)){
        return EXIT_FAILURE;
    }

    udp_header_t header;
    memcpy(&header, recv_buf, sizeof(udp_header_t));
    header.total_frag = ntohs(header.total_frag);
    header.frag_index = ntohs(header.frag_index);

    if (total_frag == 0){
        total_frag = header.total_frag;
    } 

    int frag_size = bytes - sizeof(udp_header_t);
    fragments[header.frag_index] = malloc(frag_size);
    memcpy(fragments[header.frag_index], recv_buf + sizeof(udp_header_t), frag_size);

    received_count++;

    if (received_count == total_frag) {
        int total_size = 0;
        for (int i = 0; i < total_frag - 1; i++) total_size += CHUNK_SIZE;
        total_size += frag_size; // le dernier fragment

        if (total_size > buffer_size - 1) total_size = buffer_size - 1; //pour la sécurité
        char *ptr = buffer;
        for (int i = 0; i < total_frag; i++) {
            int size = (i == total_frag - 1) ? frag_size : CHUNK_SIZE;
            if (ptr - buffer + size > buffer_size - 1) size = buffer_size - 1 - (ptr - buffer);
            memcpy(ptr, fragments[i], size);
            ptr += size;
            free(fragments[i]);
            fragments[i] = NULL;
        }
        *ptr = '\0';

        // Reset pour le prochain message
        received_count = 0;
        total_frag = 0;

        return ptr - buffer; // taille du JSON
    }

    return EXIT_SUCCESS; 
}


int main(int argc, char *argv[]){
}