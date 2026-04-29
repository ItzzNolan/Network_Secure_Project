#include <stdlib.h>
#include <stdio.h>
#include <string.h>


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


int main(int argc, char *argv[]){
    char request[] = "REQUEST_PROP";
    char answer[] ="ANSWER_PROP";
    char message[] = "{\"type\" : \"ANSWER_PROP\", \"entity_id\" : n, \"x\" : x, \"y\" : y, \"id_send\" : id_Michel, \"id_recv\" : id_Jean}" ;
    char myid[] = "id_Jean";

    char messagecpy[strlen(message)];
    strcpy(messagecpy,message);

    printf("%s \n", messagecpy);
    
    int count = 0;
    char *tab[25];

    separer(messagecpy, tab, &count);


    if (strstr(message,request)){
        printf("requête");
       
        
        if (findidsend(tab,myid,count)==0){
            printf("envoi requête \n");
        }
    }
    else if (strstr(message,"ANSWER_PROP")){
        

        if (findidrcv(tab,myid,count)==0){
            printf("envoi réponse \n");
        }
    }
    else printf("autre message \n");
    
    return 0;
}