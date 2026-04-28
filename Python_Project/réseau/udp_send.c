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

#define PORT 12345
#define MAX_DGRAM_SIZE 1400

extern void stop(char *s);
int udp_send(const void* data){
   int sockfd;
   size_t len = strlen(data);
   if ((sockfd=socket(AF_INET,SOCK_DGRAM,0))<0){
      stop("socket creation failed");
   }

   int broadcast = 1;
   if (setsockopt(sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast)) < 0) {
      stop("setsockopt SO_BROADCAST");
   }

   struct sockaddr_in serv_addr;
   len=sizeof(serv_addr);

   bzero(&serv_addr, sizeof(serv_addr));
   
   serv_addr.sin_family = AF_INET;
   serv_addr.sin_port=htons(PORT);
   inet_aton("255.255.255.255", &serv_addr.sin_addr);

   if (sendto(sockfd, data, len, 0, (struct sockaddr*)&serv_addr,len)<0){
      stop("sendto");
   }

   return EXIT_SUCCESS;
}

/*
void message_send(char* json){
   size_t len = strlen(json);

   int header_size = sizeof(uint32_t) + 2*sizeof(uint16_t);
   int max_payload = MAX_DGRAM_SIZE - header_size;

   // Un seul packet
   if (len <= MAX_DGRAM_SIZE) {
      udp_send(json, len);
      //return;
   }

   // Plusieurs packets
   uint32_t msg_id = rand();
   int total = (len / max_payload) + 1;
   printf("c%d\n",total);

   for (int i = 0; i < total; i++) {

      char buffer[MAX_DGRAM_SIZE];

      uint32_t *p_msg_id = (uint32_t*)buffer;
      uint16_t *p_total  = (uint16_t*)(buffer + sizeof(uint32_t));
      uint16_t *p_index  = (uint16_t*)(buffer + sizeof(uint32_t) + sizeof(uint16_t));

      *p_msg_id = htonl(msg_id);
      *p_total  = htons(total);
      *p_index  = htons(i);

      int offset = i * max_payload;
      int chunk_size = (len - offset > max_payload) ? max_payload : (len - offset);

      memcpy(buffer + header_size, json + offset, chunk_size);

      udp_send(buffer, header_size + chunk_size);
   }
}
*/

/*
int main(int argc, char*argv[]){
   udp_send(argv[1]);
}
*/