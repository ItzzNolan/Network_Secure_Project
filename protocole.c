#include <stdlib.h>
#include <stdio.h>

typedef enum {
    MSG_JOIN,
    MSG_FULL_STATE,
    MSG_FULL_STATE_CHUNK,
    MSG_UPDATE,
    MSG_DISCONNECT
} type_message;

typedef struct {
    type_message type;
    int player_id;
    int entity_id;
    char *action;    
    char *data; 
} message_t;

const char *type_to_string(message_type_t type)
{
    switch (type) {
        case MSG_JOIN: return "JOIN";
        case MSG_FULL_STATE: return "FULL_STATE";
        case MSG_UPDATE: return "UPDATE";
        case MSG_DISCONNECT: return "DISCONNECT";
        default: return "UNKNOWN";
    }
}

//envoie le json, découpe si trop gros
message_send(int fd, struct sockaddr_in *dest, char *json_str){

}

//
message_recv(int fd, char *buffer, int buffer_size, struct sockaddr_in *sender){

}

char *message_to_json(message_t *msg){
    if (!msg) return NULL;

    const char *type_str = type_to_string(msg->type);


}

json_to_message(char json){

}

int main(int argc, char *argv[]){
}