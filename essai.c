#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int findidsend(char message[], char myid[], int i){
    
    char idsend[] = "id_send";
    for(int j = 0; j<i; j++){
        if(strstr(message[j], idsend)){
            printf("%s \n", message[j+2]);

            int idlen = strlen(message[j+2]);
            char idfind[idlen];
            strcpy(idfind, message[j+2]);
        
            idfind[idlen -1] = '\0';
            printf("%s \n", idfind);
            return strcmp(myid,idfind);
        }else{
            return 0;
        }
   }

}

int main(int argc, char *argv[]){
    /*char chaine[] = "Ceci est un test";
    char recherche[] ="test";
    char faux[]= "blabla";

    if(strstr(chaine, recherche)){
        printf("C'est ok \n");
    }else{
        printf("C'est pas ok \n");
    }

    if(strstr(chaine, faux)){
        printf("C'est ok \n");
    }else{
        printf("C'est pas ok \n");
    }*/
   char chaine[] = "{\"type\" : \"REQUEST_PROP\", \"entity_id\" : n, \"x\" : x, \"y\" : y, \"id_send\" : id_Michel, \"id_recv\" : id_Jean}";
   //int len = strlen(str);
   char sep[] = " ";
   char *p = strtok(chaine, sep);
   char *tab[25];
   int i = 0;
   while(p != NULL){
        tab[i] = p;
        i = i+1;
        p= strtok(NULL,sep);
   }
   /*char idsend[] = "id_send";
   
   for(int j = 0; j<i; j++){
    if(strstr(tab[j], idsend)){
        printf("%s \n", tab[j+2]);

        int idlen = strlen(tab[j+2]);
        char idfind[idlen];
        strcpy(idfind, tab[j+2]);
        
        idfind[idlen -1] = '\0';
        printf("%s \n", idfind);
    }
   }*/

   printf("%d \n", findidsend(tab,"id_michel",i));





}