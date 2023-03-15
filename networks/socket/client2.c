// Client side C/C++ program to demonstrate Socket
// programming
#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdbool.h>
#include <stdlib.h>
#include <regex.h>

#define PORT 12000
#define BUFFER_SIZE 1024
//print console logs
#define logs false
#define HTTP_TWO_BUFFER 40960
regex_t rx;

int mediaCnt=0;

struct my_pair {
    long int start;
    long int end;
	char str[320];
};
typedef struct my_pair* pair;

char* getPort(char* url,char* s){
	char* backSlash=strstr(url,"/");
	char* colonSymbol=strstr(backSlash+1,":");
	char* lastBackslash=strstr(colonSymbol,"/");
	int len=strlen(colonSymbol)-strlen(lastBackslash);
	// char ret[100]={0};
	strncpy(s,colonSymbol+1,len-1);
	// return ret;
}

char* getFileName(char* url, char* s){
	char* backSlash=strstr(url,"/");
	char* colonSymbol=strstr(backSlash+1,":");
	char* lastBackslash=strstr(colonSymbol,"/");
	int len=strlen(lastBackslash);
	strncpy(s,lastBackslash+1,len-1);
    char arr[100]={0};
    strncpy(arr,s,len);
    arr[len-1]=0;
    return arr;
}


// char* url="http://localhost:12000/videoTest.html";
char* getIP(char* url, char* s){
	char* backSlash=strstr(url,"//");
	char* nameStartLoc=backSlash+2;
	char* nameEndLoc=strstr(nameStartLoc,":");
	int len=nameEndLoc-nameStartLoc;
	strncpy(s,nameStartLoc,len);
    char arr[100]={0};
    strncpy(arr,s,len);
    arr[len]=0;
    return arr;
}

// char* generateGETRequest(char* filename){
// 	char*  getRequest=(char*)malloc(420*sizeof(char));
//     strcpy(getRequest,"GET /");
//     strcpy(getRequest+5,filename);
// 	strcat(getRequest," HTTP/2.0");
//     if(logs){
//         printf("get Req -->%s<--",getRequest);
//     }
//     return getRequest;
// }

void writeBuffToFile(FILE *fp,char* buffer,int size){
	if(fp == NULL)
	{
    	printf("ERROR - Failed to open file for writing\n");
    	return exit(1);
	}

	// Write Buffer
	if(fwrite(buffer, 1, size, fp) != size)
	{
    	printf("ERROR - Failed to write %i bytes to file\n", size);
    	return exit(1);
	}

	// Close File
	fclose(fp);
	fp = NULL;
}


//NOT USED
//prints location of image (start, end)
void imgSearch(char* str, pair* locPairs){

	char* strStartLoc=str;

	while(strStartLoc!=NULL){
		char *srcBeginLoc = strstr(strStartLoc, "src=\"");
		int i=0;
		char *srcEndLoc = strstr(srcBeginLoc+6,".jpeg\"");
		int start=strStartLoc-srcBeginLoc;
		int end=strStartLoc-srcEndLoc;
		//print console logs
		if(logs){
			printf("first loc:%d last loc:%d",start,end);
		}

		// strStartLoc=srcEndLoc;

		// //Store Start,End location in Pair 
		// pair locPair;
		// locPair= (pair)malloc(sizeof(struct my_pair));
		// locPair->start=start;
		// locPair->end=end;
		
	}

	// return locPair;
}


void  searchVideos(char* str, pair* pairs){
	char* original=str;
	char* localStr=str;
	int lastPos=0;
	while(localStr!=NULL){
		//search for iframe tags
		char* iframTagLoc=strstr(localStr,"\t<iframe width=");
		if(iframTagLoc==NULL){
			break;
		}

		char fileName[300]={0};
		char* fileNameStartPos=(iframTagLoc+39);
		char* fileNameEndPos=strstr(fileNameStartPos,".mp4");
		int fileNameLen=(fileNameEndPos-fileNameStartPos)+strlen(".mp4");
		strncpy(fileName,fileNameStartPos,fileNameLen);
		fileName[fileNameLen]=0;
		if(logs){
			printf("---%s---\n",fileName);
		}
		

		//Store Start,End location in Pair 
	    pair locPair;
	    locPair= (pair)malloc(sizeof(struct my_pair));
	    strcpy(locPair->str,fileName);

		pairs[mediaCnt]=locPair;
		localStr=fileNameEndPos;
		mediaCnt++;

	}

}

void searchImages(char* str, pair* pairs){
	char* original=str;
	char* localStr=str;
	int lastPos=0;
	while(localStr!=NULL){
		//search for iframe tags
		char* iframTagLoc=strstr(localStr,"\t<img width=");
		if(iframTagLoc==NULL){
			break;
		}

		char fileName[300]={0};
		char* fileNameStartPos=(iframTagLoc+23);
		char* fileNameEndPos=strstr(fileNameStartPos,".jpeg");
		int fileNameLen=(fileNameEndPos-fileNameStartPos)+strlen(".jpeg");
		strncpy(fileName,fileNameStartPos,fileNameLen);
		fileName[fileNameLen]=0;
		
		if(logs){
			printf("---%s---",fileName);
		}
		

		//Store Start,End location in Pair 
	    pair locPair;
	    locPair= (pair)malloc(sizeof(struct my_pair));
	    strcpy(locPair->str,fileName);

		pairs[mediaCnt]=locPair;
		localStr=fileNameEndPos;
		mediaCnt++;

	}

}


void foo(char* str, pair* pairs){
	char* originalStr=str;
    char* localStr=str;
    long int lastPost=0;
	if(logs){
    	printf("inside multiImgSearchPair:\n\n");
	}
    int cnt=0;
    while(localStr!=NULL){
		char *srcBeginLoc = strstr(localStr, "src=\"");
		
        if(srcBeginLoc==NULL){
            //string completely parsed
            break;
        }

		int i=0;
		char *srcEndLoc = strstr(srcBeginLoc+6,".jpeg\"");

		int start=lastPost+(srcBeginLoc-localStr);
		int end=lastPost+(srcEndLoc-localStr);
		if(logs){
			printf("\nfirst loc:%d last loc:%d\n\n",start,end);
		}

        //Store Start,End location in Pair 
	    pair locPair;
	    locPair= (pair)malloc(sizeof(struct my_pair));
	    locPair->start=start;
	    locPair->end=end;

        /**
		 * Store image paths in array of 
         * SubStr Simulation
		**/

        char destFileName[128]={0};
        int imagePathLen=(end)-start;
        //src+5="image_path.jpeg"
        strncpy(destFileName,(str+(start+5)),imagePathLen);
        //Do Null Termination since strncpy doesn't
        destFileName[imagePathLen]=0;
        // printf("\n\nString: %s",destFileName);

        strcpy(locPair->str,destFileName);

        //Store pair in pair
        *(pairs+cnt)=locPair;
	    

        //Lets continue search
        cnt++;
        lastPost=end+1;
		localStr=srcEndLoc+1;
	}
}









void multiImgSearchPair(char* str, pair* pairs ){
    char* localStr=str;
    long int lastPost=0;
	if(logs){
    	printf("inside multiImgSearchPair:\n\n");
	}
    int cnt=0;
    while(localStr!=NULL){
		char *srcBeginLoc = strstr(localStr, "src=\"");

        if(srcBeginLoc==NULL){
            //string completely parsed
            break;
        }

		int i=0;
		char *srcEndLoc = strstr(srcBeginLoc+6,".jpeg\"");

		int start=lastPost+(srcBeginLoc-localStr);
		int end=lastPost+(srcEndLoc-localStr);
		if(logs){
			printf("\nfirst loc:%d last loc:%d\n\n",start,end);
		}

        //Store Start,End location in Pair 
	    pair locPair;
	    locPair= (pair)malloc(sizeof(struct my_pair));
	    locPair->start=start;
	    locPair->end=end;

        /**
		 * Store image paths in array of 
         * SubStr Simulation
		**/

        char destFileName[128]={0};
        int imagePathLen=(end)-start;
        //src+5="image_path.jpeg"
        strncpy(destFileName,(str+(start+5)),imagePathLen);
        //Do Null Termination since strncpy doesn't
        destFileName[imagePathLen]=0;
        // printf("\n\nString: %s",destFileName);

        strcpy(locPair->str,destFileName);

        //Store pair in pair
        *(pairs+cnt)=locPair;
	    

        //Lets continue search
        cnt++;
        lastPost=end+1;
		localStr=srcEndLoc+1;
	}
}

void multiVideoSearchPair(char* str, pair* pairs ){
    char* localStr=str;
    long int lastPost=0;
	if(logs){
    	printf("inside multiImgSearchPair:\n\n");
	}
    int cnt=0;
    while(localStr!=NULL){
		char *srcBeginLoc = strstr(localStr, "src=\"");
        if(srcBeginLoc==NULL){
            //string completely parsed
            break;
        }

		int i=0;
		char *srcEndLoc = strstr(srcBeginLoc+6,".mp4\"");

		int start=lastPost+(srcBeginLoc-localStr);
		int end=lastPost+(srcEndLoc-localStr);
		if(logs){
			printf("\nfirst loc:%d last loc:%d\n\n",start,end);
		}

        //Store Start,End location in Pair 
	    pair locPair;
	    locPair= (pair)malloc(sizeof(struct my_pair));
	    locPair->start=start;
	    locPair->end=end;

        /**
		 * Store image paths in array of 
         * SubStr Simulation
		**/

        char destFileName[128]={0};
        int imagePathLen=(end)-start;
        //src+5="image_path.jpeg"
        strncpy(destFileName,(str+(start+4)),imagePathLen);
        //Do Null Termination since strncpy doesn't
        destFileName[imagePathLen]=0;
        // printf("\n\nString: %s",destFileName);

        strcpy(locPair->str,destFileName);

        //Store pair in pair
        *(pairs+cnt)=locPair;
	    

        //Lets continue search
        cnt++;
        lastPost=end+1;
		localStr=srcEndLoc+1;
	}
}


char* generateGETRequest(char* filename){
	char  getRequest[300]={0};
    strcpy(getRequest,"GET /");
    strcpy(getRequest+5,filename);
	strcat(getRequest," HTTP/2.0");
    if(logs){
        printf("get Req -->%s<--",getRequest);
    }
    return getRequest;
}



pair imgSearchOld(char* str){
	char *srcBeginLoc = strstr(str, "src=\"");
	int i=0;
	char *srcEndLoc = strstr(srcBeginLoc+6,".jpeg\"");
	long int start=srcBeginLoc-str;
	long int end=srcEndLoc-str;
	printf("first loc:%ld last loc:%ld\n",start,end);

	//Store Start,End location in Pair 
	pair locPair;
	locPair= (pair)malloc(sizeof(struct my_pair));
	locPair->start=start;
	locPair->end=end;
	return locPair;
}


int main(int argc, char const* argv[])
{
	int sock = 0, valread, client_fd;
	struct sockaddr_in serv_addr;
	int port=PORT;

	
	// char* url="http://127.0.0.1:1234/picture.html";
	char* url=argv[1];
	printf("%s\n",url);
	char portStr[100]={0};

	char fileNameStr[100]={0};
	getPort(url,portStr);
	port=atoi(portStr);


	char ipAddr[100]={0};
	getIP(url,ipAddr);
	char* fileName=getFileName(url,fileNameStr);


	if(logs){
		printf("\nport str:%s fileName:%s\n",(portStr),(fileNameStr));
	}

	// port=atoi(portStr);

	if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		printf("\n Socket creation error \n");
		return -1;
	}

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_port = htons(port);

	// Convert IPv4 and IPv6 addresses from text to binary
	// form
	if (inet_pton(AF_INET, ipAddr, &serv_addr.sin_addr)
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

	int cnt=1;
	while(cnt>0){
		
		char query[1024];
		// fgets(query, sizeof(query), stdin);
		if(logs){
			printf("--->%s<---\n", generateGETRequest(fileNameStr));
		}
		strcpy(query, generateGETRequest(fileNameStr));
		//fgets includes the trailing "\n" so remove that
		query[strcspn(query,"\n\r")]=0;
		char serverResponse[1024] = { 0 };


		send(sock, query, strlen(query), 0);
		if(logs){
			printf("Server Response for Query #%d:",cnt);
		}
		
		bool isHTML=false;
		bool isVID=false;
		bool isIMG=false;

		//READ ONLY "HTTP/1.1 200 OK\n"
		valread = read(sock, serverResponse, 16);

		if(logs){		
			printf("server res->%s", serverResponse);
		}

		isHTML=(strcmp("HTTP/2.0 200 OK\n",serverResponse)==0)?true:false;
		isVID=(strcmp("HTTP/2.0 200 OK\n-XV",serverResponse)==0)?true:false;
		isIMG=(strcmp("HTTP/2.0 200 OK\n-XI",serverResponse)==0)?true:false;

		//if found a file then print it
		if(strcmp("HTTP/2.0 200 OK\n",serverResponse)==0){
			if(logs){
				printf("Inside Client\n");
			}



			char buffer[BUFFER_SIZE]={0};
			FILE *f_dst;
			while (1) {
				valread = read(sock, buffer, BUFFER_SIZE);
				// printf("Bytes Read = %d",valread);

				if(strcmp("\n*^^* File Sent Successfully *^^*\n",buffer)==0){
					// File reading completed
					break;
				}

    			// if (valread <= 0){
				// 	printf("VALread DOWN = %d",valread);
				// 	// valRead==0 -> EOF
     			// 	break;
    			// }
				if(logs){
					printf("%s",buffer);
				}

				//Write Buffer to File
				f_dst = fopen("index.html","wb");
				writeBuffToFile(f_dst,buffer,BUFFER_SIZE);

    			// fprintf(fp, "%s", buffer);
    			bzero(buffer, BUFFER_SIZE);
  			}
			fclose(f_dst);

			//NOW OPEN HTML FILE AND GET IMAGES
			//send file in packets
			FILE *fp;
  			char *filename = "index.html";
  			char fileBuffer[1024]={0};
			fp = fopen(filename, "rt");

			fseek(fp, 0, SEEK_END); // seek to end of file
			long int fileSize = ftell(fp); // get current file pointer
			fseek(fp, 0, SEEK_SET); // seek back to beginning of file

			// A DATA Structure to save image details for which i'll send the GET request later
			pair imageDetails[128];
			//allocate memory 
			for(int i=0;i<120;i++){
				imageDetails[i]=(pair)malloc(128*sizeof(struct my_pair));
			}

			int loopCount=0;
			while(!feof(fp) && loopCount==0) {
				loopCount++;
				
				fread(fileBuffer, sizeof(fileBuffer), 1, fp);


				//FINISHED COLLECTING ALL MEDIA HERE - Saved in imageDetails
				searchVideos(fileBuffer,imageDetails);
				searchImages(fileBuffer,imageDetails);

				// if(isVID==true){
				// }else  if(isIMG==true){
    			// 	multiImgSearchPair(fileBuffer,imageDetails);
				// }

			
				// sleep(1);
    			bzero(buffer, BUFFER_SIZE);
  			}

			//GET REQUESTS SAVED in 'imageDetails'. Now Send them to Server
			
			//SEND GET REQ FOR IMAGES TO SERVER 
				for(int i=0;i<mediaCnt;i++){
					char imagePath[300]={0};
					strcpy(imagePath,imageDetails[i]->str);
					if(logs){
						printf("Image Path %s:\n\n",imagePath);
					}

					char getRequest[1024]={0};
					strcpy(getRequest,generateGETRequest(imagePath));
					bool emptyReq=(strcmp("GET / HTTP/2.0",getRequest)==0);
					if(emptyReq){
						break;
					}

					//send get request
					send(sock,getRequest,sizeof(getRequest),0);
					if(logs){
						printf("Sent GET Request to Server:%s\n",getRequest);
					}
				}

				char mediaRequestSent[1024]="\n**** Media Req Sent ****\n";
				if(logs){
					printf("%s",mediaRequestSent);
				}
				send(sock,mediaRequestSent,sizeof(mediaRequestSent),0);

			if(logs){
				char fileRecievedMsg[1024]="\n**** File Recieved Successfully ****\n";
				printf("%s",fileRecievedMsg);
			}
			
		}
		fflush(stdin);
		cnt--;
	}

	char closeMssg[1024];
	strcpy(closeMssg,"**** terminate ****");
	
	char serverMsg[1024]={0};
	read(sock, serverMsg, sizeof(serverMsg));
	while (strcmp(serverMsg,closeMssg)!=0)
	{
		printf("%s",serverMsg);
		read(sock, serverMsg, sizeof(serverMsg));
		
	}

	if(logs){
		printf("\nTerminating\n");
	}	
	// closing the connected socket
	close(client_fd);
	return 0;
}
