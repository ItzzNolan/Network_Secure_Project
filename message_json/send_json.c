message_send(char* json){
   
}


#define MAX_DGRAM_SIZE 512

void message_send(char *json_str)
{
    size_t len = strlen(json_str);

    int header_size = sizeof(uint32_t) + 2*sizeof(uint16_t);
    int max_payload = MAX_DGRAM_SIZE - header_size;

    // ✅ CAS SIMPLE : tient dans un seul paquet
    if (len <= MAX_DGRAM_SIZE) {
        udp_send_raw(json_str, len);
        return;
    }

    // 🔥 CAS FRAGMENTÉ
    uint32_t msg_id = rand();
    int total = (len + max_payload - 1) / max_payload;

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

        memcpy(buffer + header_size, json_str + offset, chunk_size);

        udp_send_raw(buffer, header_size + chunk_size);

        // optionnel (évite saturation)
        usleep(1000);
    }
}