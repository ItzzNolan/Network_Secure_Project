#include <stdlib.h>
#include <stdio.h>

struct peer_t{
    addr : struct sockaddr_in;
    player_id : int; 
}peer_t;

static peer_t peers[MAX_PEERS];
static int peer_count = 0;

void peer_add(struct sockaddr_in, int player_id){

    if (peer_count >= MAX_PEERS) {
        return -1; 
    }

    for (int i = 0; i < peer_count; i++) {
        if (peers[i].player_id == player_id) {
            return 0; 
        }
    }

    peers[peer_count].addr = addr;
    peers[peer_count].player_id = player_id;
    peer_count++;

    return 1; 
}


void peer_remove(int_player_id){
     for (int i = 0; i < peer_count; i++) {
        if (peers[i].player_id == player_id) {
            peers[i] = peers[peer_count - 1]; //remplace par le dernier pour pas avoir de trou
            peer_count--;
            return 1;
        }
    }
}

void peer_get_all(){
    for (int i = 0; i < peer_count; i++){
        print(peers[i].addr);
        print(peers[i].player_id);
    }
}

void peer_find(struct sockaddr_in addr){
    for (int i = 0; i < peer_count; i++){
        if(peer[i].addr = addr){
            print(peer[i].pkayer_id);
            return 1;
        }
    }
    print("player not found");

}

int main(int argc, char *argv[]){

}