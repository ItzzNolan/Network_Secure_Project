#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]){
    char request[] = "REQUEST_PROP";
    char answer[] ="ANSWER_PROP";
    char message[]= ;

    if(strstr(message, request)){
        printf("C'est ok \n");
    }else if(strstr(message, answer)){
        printf("C'est pas ok \n");
    }else{

}