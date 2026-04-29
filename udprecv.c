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
#define BUFLEN 2000 // a changer quand on connaitra la taille max

static void stop(char *s){
   perror(s);
   exit(1);
}

int udp_recv(){
   int sockfd = socket(AF_INET, SOCK_DGRAM,0); 
   if(sockfd < -1){
      stop("error socket");
        
   }
   int opt = 1;
   setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

   struct sockaddr_in serv_addr;
   bzero(&serv_addr, sizeof(serv_addr));

   serv_addr.sin_addr.s_addr = INADDR_ANY;
   serv_addr.sin_family = AF_INET;
   serv_addr.sin_port = htons(PORT);

   if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr))<0){
      stop("Error on biding");
   }

   char message[BUFLEN+1];

   struct sockaddr_in cli_addr;

   do{
      bzero(&message, BUFLEN+1);
      socklen_t addrlen = sizeof(cli_addr);
      int nbbytes = recvfrom(sockfd,message,BUFLEN, 0,(struct sockaddr*)&cli_addr,&addrlen);

      if (nbbytes < 0) {
         stop("error recvfrom");
      }

      message[nbbytes]='\0';
      int em;
      em = i1_envoyer_message(message, 0);
      if (em < 0) {
         stop("error send message");
      }
   }while(1);
   close(sockfd);
}


