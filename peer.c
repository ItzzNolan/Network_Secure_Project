#include <stdlib.h>
#include <stdio.h>
#include <netinet/in.h>


#define MAX_PEERS 100

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

}