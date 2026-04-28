#include <stdlib.h>
#include <stdio.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>

#define MAX_PEERS 100
#define SERVER "127.0.0.1"
#define BUFLEN 52
#define PORT 1234

typedef struct{
    struct sockaddr_in addr;
    int player_id; 
}peer_t;

static peer_t peers[MAX_PEERS];
static int peer_count = 0;

int peer_add(struct sockaddr_in addr, int player_id){

    if (peer_count >= MAX_PEERS) {
        return EXIT_FAILURE; 
    }

    for (int i = 0; i < peer_count; i++) {
        if (peers[i].player_id == player_id) {
            return EXIT_FAILURE; 
        }
    }

    peers[peer_count].addr = addr;
    peers[peer_count].player_id = player_id;
    peer_count++;

    return EXIT_SUCCESS; 
}


int peer_remove(int player_id){
     for (int i = 0; i < peer_count; i++) {
        if (peers[i].player_id == player_id) {
            peers[i] = peers[peer_count - 1]; //remplace par le dernier pour pas avoir de trou
            peer_count--;
            return EXIT_SUCCESS;
        }
    }
    return EXIT_FAILURE;
}

void peer_get_all(){
    for (int i = 0; i < peer_count; i++){
        printf("%d \n", peers[i].player_id);
    }
}

int peer_find(struct sockaddr_in addr){
    for (int i = 0; i < peer_count; i++){
        if(peers[i].addr.sin_addr.s_addr == addr.sin_addr.s_addr &&
            peers[i].addr.sin_port == addr.sin_port){
            printf("%d \n", peers[i].player_id);
            return EXIT_SUCCESS;
        }
    }
    printf("player not found");
    return EXIT_FAILURE;

}

int main(int argc, char *argv[]){

    int sockfd1 = socket(AF_INET, SOCK_DGRAM,0);
    int sockfd2 = socket(AF_INET, SOCK_DGRAM,0);
    int sockfd3 = socket(AF_INET, SOCK_DGRAM,0);

    int  port = PORT;

    struct sockaddr_in sock1;
    sock1.sin_addr.s_addr = inet_addr(SERVER);
    sock1.sin_family = AF_INET;
    sock1.sin_port = htons(port);


    struct sockaddr_in sock2;
    sock2.sin_addr.s_addr = inet_addr(SERVER);
    sock2.sin_family = AF_INET;
    sock2.sin_port = htons(port);

    struct sockaddr_in sock3;
    sock3.sin_addr.s_addr = inet_addr(SERVER);
    sock3.sin_family = AF_INET;
    sock3.sin_port = htons(port);

    peer_add(sock1,10);
    peer_add(sock2,20);
    peer_add(sock3,30);

    peer_get_all();

    peer_remove(20);

    int sockfd4 = socket(AF_INET, SOCK_DGRAM,0);
    struct sockaddr_in sock4;
    sock4.sin_addr.s_addr = inet_addr(SERVER);
    sock4.sin_family = AF_INET;
    sock4.sin_port = htons(port);

    peer_add(sock4,40);

    peer_get_all();

    peer_find(sock3); //pb même  adresse IP et même port, prend la première

}