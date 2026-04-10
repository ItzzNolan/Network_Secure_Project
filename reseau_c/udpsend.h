#ifndef UDPSEND_H
#define UDPSEND_H

extern void stop (char* s);
extern int udp_send(const void* data, size_t len);
void message_send(char* json);

#endif