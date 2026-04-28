#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <cjson/cJSON.h>
#include <sys/select.h> 
#define PORT_C 9999      
#define PORT_PY 9998     
#define BUF_SIZE 2048

void envoyer_a_python(int sockfd, struct sockaddr_in *dest_addr, const char *message) {
    sendto(sockfd, message, strlen(message), 0, 
           (struct sockaddr *)dest_addr, sizeof(*dest_addr));
    printf("[C -> PY] Message envoyé à Python : %s\n", message);
}


void interpreter_msg_python(char *raw_json) {
    cJSON *json = cJSON_Parse(raw_json);
    if (!json) return;

    cJSON *type = cJSON_GetObjectItemCaseSensitive(json, "type");
    if (cJSON_IsString(type)) {
        if (strcmp(type->valuestring, "UPDATE") == 0) {
            printf("[PY -> C] Logique de combat : Mise à jour reçue. Diffusion réseau...\n");
        }
    }
    cJSON_Delete(json);
}

int main() {
    int sockfd;
    char buffer[BUF_SIZE];
    struct sockaddr_in servaddr, py_addr;
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);

    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = INADDR_ANY;
    servaddr.sin_port = htons(PORT_C);
    memset(&py_addr, 0, sizeof(py_addr));
    py_addr.sin_family = AF_INET;
    py_addr.sin_port = htons(PORT_PY);
    inet_pton(AF_INET, "127.0.0.1", &py_addr.sin_addr);

    if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
        perror("Bind échoué");
        exit(1);
    }

    printf("I1 : Système IPC actif. En attente de messages...\n");

    while(1) {
        fd_set readfds;
        FD_ZERO(&readfds);
        FD_SET(sockfd, &readfds);
        int activity = select(sockfd + 1, &readfds, NULL, NULL, NULL);

        if (activity > 0 && FD_ISSET(sockfd, &readfds)) {
            struct sockaddr_in cliaddr;
            int len = sizeof(cliaddr);
            int n = recvfrom(sockfd, buffer, BUF_SIZE, 0, (struct sockaddr *)&cliaddr, (socklen_t*)&len);
            buffer[n] = '\0';

            interpreter_msg_python(buffer);
            envoyer_a_python(sockfd, &py_addr, "{\"status\": \"OK\", \"msg\": \"Action recue\"}");
        }
    }
    return 0;
}