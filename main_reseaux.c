//A enlever :  le message "j'ai bien reçu" pour écouter seulement


#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <errno.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>


#define SERVER "127.0.0.1"
#define BUFLEN 52
#define PORT 1234



void stop(char *s){
   perror(s);   
   exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]){


   int sockfd = socket(AF_INET, SOCK_DGRAM,0);

   char message[BUFLEN+1];
 

   struct sockaddr_in clia_addr;

   struct sockaddr_in serv_addr; 
   int len, nbbytes;
   

   if(sockfd == -1){
      stop("error socket");
   }
   int opt = 1;
   setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

   serv_addr.sin_addr.s_addr = inet_addr(SERVER);

   serv_addr.sin_family = AF_INET;
 
   int  port = PORT;
   serv_addr.sin_port = htons(port);


   if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr))<0){
      stop("Error on biding");
   }

   bzero(&message,BUFLEN+1);
   len = sizeof(clia_addr);

   do{
 
      if  ((nbbytes = recvfrom(sockfd,message, BUFLEN,0, (struct sockaddr *) &clia_addr,
               (socklen_t*)&len))<0){
         stop("error recvfrom");
       }
      message[nbbytes] = '\0';
      printf("%s",message);
    
      sleep(1);
      
   }while(1);
   close(sockfd);   

}