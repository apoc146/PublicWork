// Server side C/C++ program to demonstrate Socket
// programming
#include<arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <ctype.h>
#include<pthread.h>
#include<stdlib.h>

#define PORT 12000

struct client
{
	char* cin_addr;
	int* cin_socket;
	int cin_port;
};


// Single client support handler
void connectionHandler(int new_socket){
	while(1){
		char sentence[1024] = { 0 };
		int valread = read(new_socket, sentence, 1024);
		printf("Recevied sentence:\n");
		printf("%s\n", sentence);
		char modifiedSentence[1024] = { 0 };
		int j = 0;
		char ch;
		while (sentence[j]){
			ch = sentence[j];
			modifiedSentence[j] = toupper(ch);
			j++;
		}
		printf("Modified sentence:\n");
		printf("%s\n", modifiedSentence);
		send(new_socket, modifiedSentence, strlen(modifiedSentence), 0);
	}
	// closing the connected socket
	close(new_socket);
}


//Multi client support handler
void* multiConnectionHandler(void* cltDetails){
	struct client *clinet = cltDetails;
	int p_new_socket=*(clinet->cin_socket);
	char* client_ip=clinet->cin_addr;
	int client_port=clinet->cin_port;

	while(1){
		char clientQuery[1024] = { 0 };
		int valread = read(p_new_socket, clientQuery, 1024);
		if(valread<=0){
			// closing the connected socket
			printf("close-client: %s, %d\n",client_ip,client_port);
			close(p_new_socket);
			return NULL;
		}
		char serverResponse[1024] = { 0 };

		int retVal=sprintf(serverResponse,"message-from-client: %s %d \n%s",client_ip,client_port,clientQuery);
		printf("%s\n",serverResponse);
		send(p_new_socket, clientQuery, strlen(clientQuery), 0);
	}
}



int main(int argc, char const* argv[])
{
	int server_fd, new_socket, valread;
	struct sockaddr_in address, clinetAddress;
	int opt = 1;
	int addrlen = sizeof(address);

	//PARAMS
	int port=atoi(argv[1]);
	// struct arg_struct *args = details;

	if(argc!=2){
		printf("Enter Port Number in CLI. Defaulting to 12000\n");
	}

	// port=1215;
	// printf("port is->%d\n",port);

	// Creating socket file descriptor
	if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		perror("socket failed");
		exit(EXIT_FAILURE);
	}

	// Forcefully attaching socket to the port 12000
	if (setsockopt(server_fd, SOL_SOCKET,
				SO_REUSEADDR, &opt,
				sizeof(opt))) {
		perror("setsockopt");
		exit(EXIT_FAILURE);
	}

	address.sin_family = AF_INET;
	address.sin_addr.s_addr = INADDR_ANY;
	address.sin_port = htons(port);

	// Forcefully attaching socket to the port 12000
	if (bind(server_fd, (struct sockaddr*)&address,
			sizeof(address))
		< 0) {
		perror("bind failed");
		exit(EXIT_FAILURE);
	}

	if (listen(server_fd, 3) < 0) {
		perror("listen");
		exit(EXIT_FAILURE);
	}

	printf("The server is ready to receive\n");
		
	int clientSocketLen=sizeof(struct sockaddr_in);

	while (1){
		if ((new_socket
			= accept(server_fd, (struct sockaddr *)&clinetAddress, (socklen_t*)&clientSocketLen)) < 0){
			perror("accept");
			exit(EXIT_FAILURE);
		}
		char *client_ip = inet_ntoa(clinetAddress.sin_addr);
		int client_port = ntohs(clinetAddress.sin_port);

		// printf("BLAH BLAH-->%d--",client_port);
		



		/**** Talk to Client *****/
		// Single Client Support - Uncomment Below
		// connectionHandler(new_socket);


		//Multi Client Support - Uncomment Below
		struct client cltDetails;
		pthread_t t;
		int* p_client = malloc(sizeof(int));
		*p_client=new_socket;

		cltDetails.cin_addr=client_ip;
		cltDetails.cin_port=client_port;
		cltDetails.cin_socket=p_client;

		pthread_create(&t,NULL,multiConnectionHandler,(void*)&cltDetails);
	}

	// closing the listening socket
	shutdown(server_fd, SHUT_RDWR);
	return 0;
}
