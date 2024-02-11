// Client side C/C++ program to demonstrate Socket
// programming
#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdbool.h>
#include <stdlib.h>

#define PORT 12000

int main(int argc, char const* argv[])
{
    bool logs=false;
	int sock = 0, valread, client_fd;
	struct sockaddr_in serv_addr;

    int port;
    char ip_addr[128];
    char clientMessage[256];
    char serverResponse[256];

    
    strcpy(ip_addr,argv[1]);
    port=atoi(argv[2]);
    strcpy(clientMessage,argv[3]);

    if(logs){
        printf("Port:%d\nIP:%s\nMessage:%s\n",port,ip_addr,clientMessage);
    }


	// printf("Input lowercase sentence:\n");
	
	// fgets(sentence, sizeof(sentence), stdin);
	// char modifiedSentence[1024] = { 0 };
	
    
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		printf("\n Socket creation error \n");
		return -1;
	}

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_port = htons(port);

	// Convert IPv4 and IPv6 addresses from text to binary
	// form
	if (inet_pton(AF_INET, ip_addr, &serv_addr.sin_addr)
		<= 0) {
		printf(
			"\nInvalid address/ Address not supported \n");
		return -1;
	}

	if ((client_fd
		= connect(sock, (struct sockaddr*)&serv_addr,
				sizeof(serv_addr)))
		< 0) {
		printf("\nConnection Failed \n");
		return -1;
	}
	send(sock, clientMessage, strlen(clientMessage), 0);
	valread = read(sock, serverResponse, 1024);
	printf("Response:%s\n",serverResponse);
    sleep(60);
	// closing the connected socket
	close(client_fd);
	return 0;
}
