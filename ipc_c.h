#ifndef IPC_INTERFACE_H
#define IPC_INTERFACE_H

/**
 * @file ipc_c.h
 * @brief Module de communication (I1) pour le pont entre Python (IA) et le Réseau (C).
 */

// --- CONSTANTES ---
#define PORT_C_ECOUTE_PY 9999  // Port où le coordinateur écoute Python
#define PORT_PY_LOCAL    9998  // Port où l'IA Python écoute les mises à jour
#define PORT_RESEAU_R1   12345 // Port de diffusion réseau (Broadcast)

// --- FONCTIONS ---

/**
 * @brief Envoie un message JSON à une destination choisie.
 * * @param data Le message JSON sous forme de chaîne de caractères.
 * @param vers_reseau Si 1, envoie en Broadcast (255.255.255.255). 
 * Si 0, envoie à l'IA locale (127.0.0.1).
 * @return int 0 en cas de succès, -1 en cas d'erreur.
 */
int i1_envoyer_message(const char *data, int vers_reseau);
void i1_router_message_python(char *raw_json);

/**
 * @brief Lit un message venant de Python, le valide et l'analyse.
 * * @param fd_ipc Le descripteur de fichier du socket d'écoute (port 9999).
 * @return char* Un pointeur vers le buffer contenant le JSON validé, 
 * ou NULL si le message est invalide/inexistant.
 * * @note Le buffer retourné est statique, il ne doit pas être libéré manuellement.
 */
char* i1_traiter_entree_python(int fd_ipc);

#endif // IPC_INTERFACE_H
