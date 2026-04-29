#include <stdlib.h>
#include <stdio.h>
#include <string.h>

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
   char idsend[] = "id_send";

   for(int j = 0; j<i; j++){
    if(strstr(tab[j], idsend)){
        printf("%s \n", tab[j+2]);
    }
   }





}