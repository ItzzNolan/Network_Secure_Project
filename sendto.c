#include <stdint.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/udp.h>
#include <netdb.h>
#include <strings.h>
#include <unistd.h>
#include <time.h>
#include <arpa/inet.h>

#define BUFLEN 512
#define MESSAGE "PING"

void stop(char *s){
   perror(s);
   exit(1);
}

int main(int argc, char *argv[]){

   int sockfd,len;
   char message[BUFLEN+1];

   if ((sockfd=socket(AF_INET,SOCK_DGRAM,0))<0){
      stop("socket creation failed");
   }

    int broadcast = 1;
    if (setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast)) < 0) {
        perror("setsockopt SO_BROADCAST");
        return 1;
    }
    struct sockaddr_in serv_addr;

   int portno=1234;
   len=sizeof(serv_addr);
   bzero(&serv_addr, sizeof(serv_addr));
   serv_addr.sin_family = AF_INET;
   serv_addr.sin_port=htons(portno);
   inet_aton("127.0.0.1", &serv_addr.sin_addr);

   if (sendto(sockfd, MESSAGE, strlen(MESSAGE), 0, (struct sockaddr*)&serv_addr,len)<0){
      stop("sendto");
   }
   return EXIT_SUCCESS;
}