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
   char chaine[] = "Le chien est bleu";
   //int len = strlen(str);
   char sep[] = " ";
   char *p = strtok(chaine, sep);
   char tab[25];
   while(p != NULL){
        printf("%s \n", p);
        p= strtok(NULL,sep);
   }
   printf("\n");


}