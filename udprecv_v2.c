#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <errno.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include "ipc_c.h"

#define PORT 12345
#define BUFLEN 2000

extern void stop(char *s){
   perror(s);
   exit(1);
}

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

int udp_recv(int myid){
   int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
   if(sockfd < 0){
      stop("error socket");
   }
   int opt = 1;
   setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

   struct sockaddr_in serv_addr;
   bzero(&serv_addr, sizeof(serv_addr));

   serv_addr.sin_addr.s_addr = INADDR_ANY;
   serv_addr.sin_family = AF_INET;
   serv_addr.sin_port = htons(PORT);

   if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0){
      stop("Error on binding");
   }

   char message[BUFLEN+1];
   struct sockaddr_in cli_addr;


   do{
      bzero(&message, BUFLEN+1);
      socklen_t addrlen = sizeof(cli_addr);
      int nbbytes = recvfrom(sockfd, message, BUFLEN, 0, (struct sockaddr*)&cli_addr, &addrlen);

      if (nbbytes < 0) {
         stop("error recvfrom");
      }

      message[nbbytes] = '\0';
      printf("[RESEAU] Reçu: %s\n", message);

      char messagecpy[strlen(message)];
      strcpy(messagecpy,message);

      int count=0;
      char *tab[25];
      
      separer(messagecpy,tab,&count);

      if (strstr(message,"REQUEST_PROP")){
         if (findidsend(tab,myid,count)==0){
            int em = i1_envoyer_message(message, 0);
            if (em < 0) {
            stop("error send message");
            }
         }
      }
      else if (strstr(message,"ANSWER_PROP")){
         if (findidrcv(tab,myid,count)==0){
            int em = i1_envoyer_message(message, 0);
            if (em < 0) {
            stop("error send message");
            }
         }
      }
      else{
         int em = i1_envoyer_message(message, 0);
         if (em < 0) {
            stop("error send message");
         }
      }
   }while(1);

   close(sockfd);
}
/*int main() {
    udp_recv();
    return 0;
}*/
