#include <string.h>
#include <stdio.h>

void separer(char *message, char *tab[], int *count) {
    char separateur[] = " ";
    char *p = strtok(message, separateur);
    int i = 0;

    while (p != NULL) {
        tab[i++] = p;
        p = strtok(NULL, separateur);
    }

    *count = i;
}

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

int main() {
    char myid[] = "id_Michel";
    char message[] = "{\"type\" : \"REQUEST_PROP\", \"entity_id\" : n, \"x\" : x, \"y\" : y, \"id_send\" : id_Michel, \"id_recv\" : id_Jean}";
    
    char *tab[25];
    int count = 0;

    separer(message, tab, &count);

    for (int j = 0; j < count; j++) {
        printf("%s\n", tab[j]);
    }

    if (strstr(message,"REQUEST_PROP")){
        if (!findidrcv(tab,myid,count)){
            printf("envoi requête");
        }
    }
    else if (strstr(message,"ANSWER_PROP")){
        if (!findidsend(tab,myid,count)){
            printf("envoi réponse");
        }
    }
    else printf("autre message");
    
    return 0;
}