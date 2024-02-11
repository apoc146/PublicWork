// Server side C/C++ program to demonstrate Socket
// programming
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <ctype.h>
#include<pthread.h>
#include<stdbool.h>
#include<arpa/inet.h>

#define PORT 12000
// Max token=128 && Max token-len=128
#define SIZE_128 128
#define H_SIZE_128 128
#define BUFFER_SIZE 1024
#define HTTP_TWO_BUFFER 40960 
#define MEDIA_COUNT 10
int logs=false;

//global fileName
char destFileName[128]={0};

struct client
{
	char* cin_addr;
	int* cin_socket;
	int cin_port;
};

struct media
{
	char name[1000];
	int size;
	int totalFrames;
	int frameCounter;
};

int mediaCounter=0;


typedef struct media* mediaFile;
mediaFile mediaFileVec[10];

// struct object{
// 	int id
	
// }

/*
* taken string, tokenizes it using delimiter and returns number of tokens
*/
int tokenizeString(char* str,char* delim,char** reqTokens){
	// char* ret[20]={NULL};
	int tokenCnt=0;
	char* p = strtok(str, delim);
	// ret[i]=p;
	while (p!=NULL) {
    	// printf ("Token: %s\n", p);
		strcpy(*(reqTokens+tokenCnt),p);
    	p = strtok(NULL, delim);
		tokenCnt++;
	}

	return tokenCnt;
}


void tokenizer(char* str){
	char *p = strtok(str, " ");
	while(p != NULL) {
    	printf("%s\n", p);
    	p = strtok(NULL, " ");
	}
}


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

//Return HTTP 1.0 error code
char* error(int errorCode){

	switch(errorCode){
		case 200: return "HTTP/2.0 200 OK\n";
		case 404: return "404 Not Found\n";
		case 400: return "400 Bad Request\n";
		case 505: return "505 HTTP Version Not Supported\n";
		default: printf("Wrong ErrorCode\n");
	}
	return NULL;
}

//Check if the request str has 3 tokens- GET <File> <HTTP Protocol>
// bool hasThreeTokens(char* req){
// 	char** reqTokens = tokenizeString(req," ");
// 		//check number of tokens
// 		int cnt=0;
// 		while(*(reqTokens+cnt)!=NULL){
// 			cnt++;
// 		}

// 		//Wrong request-more than 3 tokens
// 		return (cnt>3)?false:true;
// }

bool hasGet(char* s){
	return strcmp(s,"GET")==0;
}

bool isHttpOne(char* s){
	if(logs){
		printf("\nhttp type %s\n",s);
	}
	return strcmp(s,"HTTP/1.1")==0;
}

bool isHttpTwo(char* s){
	return strcmp(s,"HTTP/2.0")==0;
}

//returns type
int httpType(char* s){
	if(isHttpOne(s)){
		return 1;
	}else if(isHttpTwo(s)){
		return 2;
	}else{
		//Do nothing Here
		//return -1
	}
	return -1;
}

bool hasFile(const char *fname)
{
    FILE *file;
	file=fopen(fname,"r");
	if(file){
		//if file is read then close it
		fclose(file);
		return true;
	}
	return false;
}

//check if the last 5 chars are ".html"
bool isHtmlFile(char* s){
	//last 5 chars are ".html"
	int len=strlen(s);
	if(len<5){
		return false;
	}

	if(s[len-1]=='l' && s[len-2]=='m' && s[len-3]=='t' && s[len-4]=='h' && s[len-5]=='.'){
		return true;
	}

	if(logs){
		printf("---> %s",s);
	}
	return false;
}

bool isImage(char* s){
	int len=strlen(s);
	//x.jpeg
	if(len>=6 && s[len-1]=='g' && s[len-2]=='e' && s[len-3]=='p' && s[len-4]=='j' && s[len-5]=='.'){
		return true;
	}
	return false;
}

bool isMP4(char* s){
	int len=strlen(s);
	//x.mp4
	if(len>=5 && s[len-1]=='4' && s[len-2]=='p' && s[len-3]=='m' && s[len-4]=='.'){
		return true;
	}
	return false;
}


/*
* reqStr - request String, verbose - log turn on/off
*/
char* requestCheck(char* reqStr,bool verbose){
	bool hasWWW=false;
	
	//SIZE_128=128
	//Supports a Max of 128 tokens in a string of 128 char size each
	char* reqTokens[SIZE_128];

	//allocate memory 
	for(int i=0;i<SIZE_128;i++){
		reqTokens[i]=(char*)malloc(SIZE_128*sizeof(char));
	}

	int tokenCount=tokenizeString(reqStr," ",reqTokens);

	char token1[SIZE_128];
	char token2[SIZE_128];
	char token3[SIZE_128];


	strcpy(token1,*(reqTokens+0));
	strcpy(token2,*(reqTokens+1));
	strcpy(token3,*(reqTokens+2));

	//check for www in name
	if(token2[0]=='/' && token2[1]=='w' && token2[2]=='w' && token2[3]=='w' && token2[4]=='/'){
		hasWWW=true;
	}

	//Remove '/' from fileName
	// Global -> char dest[128]={0};
	if(!hasWWW){
		strcpy(destFileName,"www");
		strcat(destFileName,token2);
	}else{
		strcpy(destFileName,token2+1);
	}

	strcpy(token2,destFileName);



	bool hasThreeTokensVal=(tokenCount==3);
	bool hasGetVal=hasGet(token1);
	bool isHtmlFileVal=isHtmlFile(token2);
	bool hasFileVal=hasFile(token2);
	int httpTypeVal=httpType(token3);

	//Print logs
	if(logs){
		printf("\n\nToken Count:%d",tokenCount);
		printf("\nToekn 1 :%s",token1);
		printf("\nToken 2 :%s",token2);
		printf("\nToken 3 :%s",token3);

		printf("\n");
		printf("\nHas Three Token :%d",hasThreeTokensVal);
		printf("\nHas Get  :%d",hasGetVal);
		printf("\nIs HTML File :%d",isHtmlFileVal);
		printf("\nHTTP Type:%d\n",httpTypeVal);
	}

	//Syntax check
	if(!hasThreeTokensVal || !hasGetVal){
		return error(400);
	}

	//Is HTTP 1
	if(httpTypeVal!=2){
		return error(505);
	}

	//Does File Exist
	if(!hasFileVal){
		return error(404);
	}

	//Has File
	if(hasFileVal){
		char ret[100]={0};
		strcpy(ret,error(200));
		bool isImg=isImage(token2);
		bool isVid=isMP4(token2);
		if(isImg || isVid){
			if(isImg){
				return "HTTP/2.0 200 OK\n-XI";
			}else{
				return "HTTP/2.0 200 OK\n-XV";
			}
		}
		return "HTTP/2.0 200 OK\n";
	}

	//Deallocate Memory
	for(int i=0;i<128;i++){
		free(reqTokens[i]);
	}

	return NULL;
}

int framesLeftToSend(){
	int ret=0;
	for(int i=0;i<mediaCounter;i++){
		if(mediaFileVec[i]->frameCounter<mediaFileVec[i]->totalFrames){
			return 1;
		}
	}
	return ret;
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

		if(strcmp(clientQuery,"\n**** Media Req Sent ****\n")==0){
			// All client media request recieved so now send them - No further reading required
			break;
		}


		if(logs){
			printf("\nRecevied Query:");
			printf("%s\n", clientQuery);
		}



		/********* Lets Get STATUS LINE + HEADER Lines ******/
		char* headers[H_SIZE_128];

		//allocate memory 
		for(int i=0;i<H_SIZE_128;i++){
			headers[i]=(char*)malloc(SIZE_128*sizeof(char));
		}

		//
		int headerCount=tokenizeString(clientQuery,"\r\n",headers);

		//No Response
		if(!headerCount){
			printf("\n**** No Header Recieved. Please check again ****\n");
			exit(-1);
		}

		/**
		 * Flag to detect Browser
		 * Broswer has many headers
		 *Terminal has only only one input header'GET <File> <HTTP/1.1>'
		*/
		
		bool isBrowser=(headerCount>1)?true:false;

		if(logs==true){
			printf("Header Count= %d\n",headerCount);

			printf("\t-----Start------\n");
			for(int i =0;i<headerCount;i++){
				printf("%s",headers[i]);
			}
			printf("\t-----END------\n");
		}
	
		char statusLine[SIZE_128];
		strcpy(statusLine,headers[0]);

		// PRINT
		// message-from-client: [client_ip], [client_port] 
		// [firstline-of-request]
		char serverResponse[1024] = { 0 };
		int retVal=sprintf(serverResponse,"message-from-client: %s %d \n%s",client_ip,client_port,clientQuery);
		if(logs){
			printf("%s\n",serverResponse);
		}

		char* requestCheckCodeStr = requestCheck(statusLine,logs);
		bool isHTML=false;
		bool isVID=false;
		bool isIMG=false;
		
		isHTML=(strcmp("HTTP/2.0 200 OK\n",requestCheckCodeStr)==0)?true:false;
		isVID=(strcmp("HTTP/2.0 200 OK\n-XV",requestCheckCodeStr)==0)?true:false;
		isIMG=(strcmp("HTTP/2.0 200 OK\n-XI",requestCheckCodeStr)==0)?true:false;

		if(logs){
			printf("Server Response: %s",requestCheckCodeStr);
		}

		char messageToClient[1024] = { 0 };
		if(strcmp(requestCheckCodeStr,"HTTP/2.0 200 OK\n-XV")==0|| strcmp(requestCheckCodeStr,"HTTP/2.0 200 OK\n-XI")==0){
			retVal=sprintf(messageToClient,"\nmessage-to-client: %s %d \n%s",client_ip,client_port,"HTTP/2.0 200 OK\n");
		}else{
			retVal=sprintf(messageToClient,"\nmessage-to-client: %s %d \n%s",client_ip,client_port,requestCheckCodeStr);
		}
		printf("%s\n",messageToClient);

		//Send Request Status
		//check if I have to send frames of Media Obj
		bool mediaGET=false;
		if(!isHTML && (isVID || isIMG)){
			mediaGET=true;
		}

		if(isHTML && !isVID && !isIMG){
			mediaGET=false;
			send(p_new_socket, requestCheckCodeStr, strlen(requestCheckCodeStr), 0);
		}
		
		//200 OK - if file exists - Send File
		if(strcmp(requestCheckCodeStr,error(200))==0 && !mediaGET){

			//send file in packets
			FILE *fp;
  			char *filename = destFileName;
  			char buffer[BUFFER_SIZE]={0};
			fp = fopen(filename, "r");

			fseek(fp, 0, SEEK_END); // seek to end of file
			long int fileSize = ftell(fp); // get current file pointer
			fseek(fp, 0, SEEK_SET); // seek back to beginning of file

			if(logs){
				printf("\t******** BLAH BLAH ->%ld ----",fileSize);
			}

			while(!feof(fp)) {
				
				fread(buffer, sizeof(buffer), 1, fp);
				if(logs){
					printf("%s",buffer);
				}
			
				int len=strlen(buffer);
				if(logs){
					printf("\n\nSending Line of Size:%ld\n ",sizeof(buffer));
					printf("buffer size %d\n",len);
				}
    			if (send(p_new_socket, buffer, sizeof(buffer), 0) == -1) {
      				perror("[-]Error in sending file");
      				exit(1);
    			}
				// sleep(1);
    			bzero(buffer, BUFFER_SIZE);
  			}
			char fileSentMsg[50]="\n*^^* File Sent Successfully *^^*\n";
			send(p_new_socket, fileSentMsg, sizeof(fileSentMsg), 0);

		}else if(mediaGET){

			//SAVE MEDIA REQS

			char imgNameTok[100]={0};

			strcpy(imgNameTok,strtok(statusLine+5, " "));
			strcpy(mediaFileVec[mediaCounter]->name,imgNameTok);

			//file size
			FILE *f_ptr;
			if(strlen(imgNameTok)>4 && imgNameTok[0]=='w' && imgNameTok[1]=='w' && imgNameTok[2]=='w' && imgNameTok[3]=='/'){
				//do nothing
			}else{
				char dest[100]={0};
				strcpy(dest,"www/");
				strcat(dest,imgNameTok);
				strcpy(imgNameTok,dest);
			}
			
			f_ptr = fopen(imgNameTok, "r");
			fseek(f_ptr, 0, SEEK_END);
			long int fileSize = ftell(f_ptr);
			fseek(f_ptr, 0, SEEK_SET);
			fclose(f_ptr);
			mediaFileVec[0]->size=fileSize;

			//set FrameCount
			mediaFileVec[mediaCounter]->totalFrames=(fileSize/HTTP_TWO_BUFFER)+1;

			mediaCounter++;
			if(logs){
				printf("media counter %d\n",mediaCounter);
			}
			//inject into a queue
			//serve the queu
			if(logs){
				printf("%s\n",imgNameTok);
			}
		}
	}


	//now server those requests


	while(framesLeftToSend()==1){
		for(int i=0;i<mediaCounter;i++){
			mediaFileVec[i]->frameCounter=mediaFileVec[i]->frameCounter+1;

			int totalFrames=mediaFileVec[i]->totalFrames;
			int framesCounter=mediaFileVec[i]->frameCounter;

			

			//If frames left to send;
			if(framesCounter%100==1 && framesCounter<=totalFrames){
				// printf("sending %s frame %d\n",mediaFileVec[i]->name,framesCounter);

				//send to client
				char sendToClient[1024] = { 0 };
				int retVal=sprintf(sendToClient,"Object-Frame: %s Frame_%d\n",mediaFileVec[i]->name,framesCounter);
				printf("%s",sendToClient);
				send(p_new_socket, sendToClient, sizeof(sendToClient), 0);


			}
			//increment frame count
		}
	}


	// for(int i=0;i<mediaCounter;i++){
	// 	char sendToClient[1024]={0};
	// 	strcpy(sendToClient,"Object-Frame: ");
	// 	int fileNameLength=strlen(mediaFileVec[i]->name);
	// 	strcpy(sendToClient+15,mediaFileVec[i]->name);


		

	// 	send(p_new_socket, closeMssg, strlen(closeMssg), 0);

	// }




	char closeMssg[1024]={0};
	strcpy(closeMssg,"**** terminate ****");
	send(p_new_socket, closeMssg, sizeof(closeMssg), 0);

	printf("close-client: %s, %d\n",client_ip,client_port);
	if(logs){
		printf("\tend of server-client\n");
	}
}



int main(int argc, char const* argv[])
{
	int server_fd, new_socket, valread;
	struct sockaddr_in address,clinetAddress;
	int opt = 1;
	int addrlen = sizeof(address);
	int port=PORT;

	for(int i=0;i<10;i++){
		mediaFileVec[i]=(mediaFile)malloc(10*sizeof(struct media));
		mediaFileVec[i]->size=-99;
		mediaFileVec[i]->frameCounter=0;
	}
	

	//PARAMS
	port=atoi(argv[1]);
	// port=PORT;
	if(logs){
		printf("PORT:%d",port);
	}

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
			= accept(server_fd, (struct sockaddr*)&clinetAddress,
			(socklen_t*)&clientSocketLen)) < 0){
			perror("accept");
			exit(EXIT_FAILURE);
		}

		char *client_ip = inet_ntoa(clinetAddress.sin_addr);
		int client_port = ntohs(clinetAddress.sin_port);

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
