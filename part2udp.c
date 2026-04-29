#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int findidsend(char *message[], char myid[], int i){
    
    char idsend[] = "id_send";
    for(int j = 0; j<i; j++){
        printf("%s \n", message[j]);
        if(strstr(message[j], idsend)){
            printf("%s \n", message[j+2]);

            int idlen = strlen(message[j+2]);
            char idfind[idlen];
            strcpy(idfind, message[j+2]);
        
            idfind[idlen -1] = '\0';
            printf("%s \n", idfind);
            return strcmp(myid,idfind);
        }
    }
    return 4;

}


int findidrcv(char *message[], char myid[], int i){
    
    char idrcv[] = "id_recv";
    for(int j = 0; j<i; j++){
        printf("%s \n", message[j]);
        if(strstr(message[j], idrcv)){
            printf("%s \n", message[j+2]);

            int idlen = strlen(message[j+2]);
            char idfind[idlen];
            strcpy(idfind, message[j+2]);
        
            idfind[idlen -1] = '\0';
            printf("%s \n", idfind);
            return strcmp(myid,idfind);
        }
    }
    return 4;

}


int main(int argc, char *argv[]){
    char request[] = "REQUEST_PROP";
    char answer[] ="ANSWER_PROP";
    char message[]= ;



    if(strstr(message, request)){
        printf("C'est ok \n");
    }else if(strstr(message, answer)){
        printf("C'est pas ok \n");
    }else{
        NULL;
    }

}