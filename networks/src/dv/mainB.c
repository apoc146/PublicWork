 #include <stdio.h>
 #include <stdlib.h>
 #include <stdbool.h>
 #include <string.h>
 #include <math.h>


// PARAMS
#define MAX_NODES 10
#define BUFFER_SIZE 1024
#define LINE_LEN 100
#define INF INT32_MAX
#define MAX_TRAFFIC_LINES 100

bool logs=false;

/* a rtpkt is the packet sent from one router to
   another*/
struct rtpkt {
  int sourceid;       /* id of sending router sending this pkt */
  int destid;         /* id of router to which pkt being sent 
						 (must be an directly connected neighbor) */
  int *mincost;    /* min cost to all the node  */
  };

// Node to store pckts used in send2neighbor function
struct s2nNODE {
  struct rtpkt* pckt;
  struct s2nNODE* next;
  int k;
};
typedef struct s2nNODE* s2nNode;


struct distance_table
{
	int **costs;     // the distance table of curr_node, costs[i][j] is the cost from node i to node j
};


/*****************************************************************
***************** NETWORK EMULATION CODE STARTS BELOW ***********
The code below emulates the layer 2 and below network environment:
  - emulates the transmission and delivery (with no loss and no
	corruption) between two physically connected nodes
  - calls the initializations routine rtinit once before
	beginning emulation for each node.

You should read and understand the code below. For Part A, you should fill all parts with annotation starting with "Todo". For Part B and Part C, you need to add additional routines for their features.
******************************************************************/

struct event {
   float evtime;           /* event time */
   int evtype;             /* event type code */
   int eventity;           /* entity (node) where event occurs */
   struct rtpkt *rtpktptr; /* ptr to packet (if any) assoc w/ this event */
   struct event *prev;
   struct event *next;
 };
struct event *evlist = NULL;   /* the event list */
struct distance_table *dts;
int **link_costs; /*This is a 2D matrix stroing the content defined in topo file*/
int num_nodes;

//my code
int **traffic;
int trafficLinesCount=0;
struct forwardingTable
{
  int *costToNodes; 
  int *nextHopToNodes;
};

struct forwardingTable *fts;

/* possible events: */
/*Note in this lab, we only have one event, namely FROM_LAYER2.It refer to that the packet will pop out from layer3, you can add more event to emulate other activity for other layers. Like FROM_LAYER3*/
#define  FROM_LAYER2     1

float clocktime = 0.000;


//prototype function here
void send2neighbor(struct rtpkt packet);


//My Global Vars
int k=0;
int kMax=10;
int *updatedNodes;


/**
 ***********************************************************************************
 ******** Linked List - Util Functions ******
 ***********************************************************************************
 **/


// Insert into List
s2nNode s2nInsert(s2nNode head,struct rtpkt* pckt){
  s2nNode temp = (s2nNode)malloc(sizeof(struct s2nNODE));
  temp->pckt=pckt;
  temp->next=NULL;

  //if empty list
  if(head==NULL){
	return temp;
  }

  //if atleast 1 node exists
  s2nNode cur=head;
  while(cur->next != NULL){
	cur=cur->next;
  }

  cur->next=temp;
  return head;
}

//Deallocates memory held by list nodes
s2nNode s2nListFree(s2nNode head){
  s2nNode tmp=head;
  while(tmp!=NULL){
	head=head->next;
	free(tmp);
	tmp=head;
  }
  return NULL;
}

//Len of s2n linked list
int s2nListLen(s2nNode head){
  s2nNode tmp=head;
  int res=0;
  while(tmp!=NULL){
	res++;
	tmp=tmp->next;
  }
  return res;
}

// For each node in list make 'send2neighbor' calls
void s2nListMakeCalls(s2nNode head){
  s2nNode cur=head;
  while(cur!=NULL){
	send2neighbor(*(cur->pckt));
	cur=cur->next;
  }
}

// Declare Global head to permit usage inside 'rtinit' & 'rtupdate'
s2nNode head=NULL;

//tells if a node is updated
bool isNodeUpdated(int idx){
	return (updatedNodes[idx]==true);
}

void setNodeAsUpdated(int idx){
	updatedNodes[idx]=true;
}

void setNodeAsNotUpdated(int idx){
	updatedNodes[idx]=false;
}



/* *
 **************************************************************************
 ***************************  Linked List Util End ************************
 **************************************************************************
 * */







/* *
 * ***************************************************
 * ************* Util Start ****************
 * ***************************************************
 * */

//Indicates neighbours : 1/0 - yes/no
int neighbour[MAX_NODES][MAX_NODES]={{0}}; 

void setNeighbours(int node_cnt){
  for(int i=0;i<node_cnt;i++){
	for(int j=0;j<node_cnt;j++){
	  neighbour[i][j]=(link_costs[i][j]==0 || link_costs[i][j]==-1)?0:1;
	}
  }
}

// Set a vec to value 'val'
void setVector(int vec[],int size,int val){
	for(int i=0;i<size;i++){
		vec[i]=val;
	}
}


// Returns true if i and j are neighbours
bool isNeighbour(int i, int j){
	// printf("NBR-%d\n",neighbour[i][j]);
  return (neighbour[i][j]==1)?true:false;
}

//Print a 2d vec 'arr' of size r*c
void print2DVec(int** arr,int r, int c){
  for(int i=0;i<r;i++){
	for(int j=0;j<c;j++){
	  printf("%d ",arr[i][j]);
	}
	printf("\n");
  }
}

void print1DVec(int* arr,int n){
  for(int i=0;i<n;i++){
	  printf("%d ",arr[i]);
  }
}

//Returns len of event List-'evlist'
int evListLen(struct event *evlist){
  int count=0;
  struct event* head=evlist;
  while(head!=NULL){
	count++;
	head=head->next;
  }
  return count;
}



/** Tokenize and Store 'ints' in a 1D Vector 'vec'**/
// str='1 -2 3' -> vec=[1,-2,3]
void storeTokenizeString(char* str,char* delim,int* vec){
	char* p = strtok(str, delim);
  int tokenCount=0;

	while (p!=NULL) {
	if(logs){
	  printf("%s ",p);
	}
	*(vec+tokenCount)=atoi(p);
	tokenCount++;
	p = strtok(NULL, delim);
	}
}

/** Tokenize and Store in a 2D Vector and return cnt too**/
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


// print dts in the required format
void printDTInfo(int k){
  printf("k=%d:\n",k);
  for(int ndIdx=0;ndIdx<num_nodes;ndIdx++){
	printf("node-%d:",ndIdx);
	print1DVec(dts[ndIdx].costs[ndIdx],num_nodes);
	printf("\n");
  }
  if(logs){
	printf("\n*********\n");
  }
  printf("\n");
}


//call this for nodes which is updated
void sendInfoToNeightbour(int nodeIdx,struct distance_table* dt){
	//send info to neightbour
	for(int nbrIdx=0; nbrIdx<num_nodes; nbrIdx++){
		if(isNeighbour(nodeIdx,nbrIdx) && dt->costs[nodeIdx][nbrIdx]!=-1){
			//send info now
			struct rtpkt* pckt = (struct rtpkt*)malloc(sizeof(struct rtpkt));
			pckt->sourceid=nodeIdx;
			pckt->destid=nbrIdx;
			pckt->mincost = (int *)malloc(num_nodes*sizeof(int));
			pckt->mincost=dt->costs[nodeIdx];
			send2neighbor(*pckt);
		}
	}
}

//should print slots
bool canPrintSlots(){
	if(k<5 || k%10==0){
		return true;
	}
	return false;
}


//route traffic - only prints stuff
void routeTraffic(int src,int dest, struct forwardingTable ft){
	int srcNode=src;
	int destNode=dest;
	struct forwardingTable nodeFt=ft;

	while(srcNode!=destNode){
		printf(">%d",nodeFt.nextHopToNodes[destNode]);
		srcNode=nodeFt.nextHopToNodes[destNode];
		nodeFt=fts[nodeFt.nextHopToNodes[destNode]];
	}
}

/* *
 * ***************************************************
 * ************* Util End ******************
 * ***************************************************
 * */



/************** EVENT HANDLINE ROUTINES **************/
/*  The next set of routines handle the event list   */
/*****************************************************/

 
void rtinit(struct distance_table *dt,struct forwardingTable *ft, int node, int *link_costs, int num_nodes)
{
	/* Todo: Please write the code here*/

	for(int i=0;i<num_nodes;i++){
	  for(int j=0;j<num_nodes;j++){
		dt->costs[i][j]=-1;
	  }
	}

	//update the DT and FT table for a given node 'node'
	for(int i=0;i<num_nodes;i++){
	  dt->costs[node][i]=link_costs[i];
	  ft->costToNodes[i]=link_costs[i];
	  ft->nextHopToNodes[i]=i;
	}


	//Send DTs to neighbours
	for(int i=0;i<num_nodes;i++){
	  if(isNeighbour(node,i)){
		struct rtpkt* pckt = (struct rtpkt*)malloc(sizeof(struct rtpkt));
		pckt->sourceid=node;
		pckt->destid=i;
		pckt->mincost = (int *)malloc(num_nodes*sizeof(int));
		pckt->mincost=dt->costs[node];
		if(logs){
			printf("sending to neighbour\n");
		}
		send2neighbor(*pckt);
	  }
	}

}

void rtupdate(struct distance_table *dt,struct forwardingTable* ft, struct rtpkt recv_pkt)
{
  // ------------ This would only be called for the neighbours ------ 
	
	// get vals 
	int srcID=recv_pkt.sourceid;
	int destID=recv_pkt.destid;
	int* recvPckMinCosts=recv_pkt.mincost;

	int currentNode=destID;
	int recvNode=srcID;
	int* currentNodeMinCosts=dt->costs[currentNode];

	dt->costs[srcID]=recvPckMinCosts;
	bool isUpdated=false;

	for(int i=0;i<num_nodes;i++){
		if(link_costs[destID][srcID]<0 || dt->costs[srcID][i]<0){
			//skip
			continue;
		}else if( dt->costs[destID][i]<0 ){
			isUpdated=true;
			dt->costs[destID][i] = link_costs[destID][srcID] + dt->costs[srcID][i];
			
			ft->costToNodes[i]=dt->costs[destID][i];
			ft->nextHopToNodes[i]=srcID;
		}else if( link_costs[destID][srcID]+dt->costs[srcID][i] < dt->costs[destID][i] ){
			//belman ford stuff here
			isUpdated=true;
			dt->costs[destID][i] = link_costs[destID][srcID] + dt->costs[srcID][i];
			
			ft->costToNodes[i] = dt->costs[destID][i];
			ft->nextHopToNodes[i]=srcID;
		}else if(((link_costs[destID][srcID]+dt->costs[srcID][i]) == dt->costs[destID][i]) && destID==i){
			ft->nextHopToNodes[i]=i;
			isUpdated=true;
		}else{
			//skip
			continue;
		}
	}
	
	if(isUpdated){
		setNodeAsUpdated(destID);
	}
}

void readTraffic(char* filePath){

	// //allocate memory to traffic 2D vec
	// traffic = (int **) malloc(MAX_TRAFFIC_LINES * sizeof(int *));
  	// for(int i=0;i<MAX_TRAFFIC_LINES;i++){
	// 	traffic[i]=(int*)malloc(3*sizeof(int));
	// }

	//read file data
	char data[MAX_NODES][MAX_NODES];
  	FILE *fp;
  	fp =fopen(filePath,"r");
  	char buffer[BUFFER_SIZE]={0};

  	while(!feof(fp)){
		fread(buffer, sizeof(buffer), 1, fp);
  	}

	//Declare Container for storing lines
	char* Lines[MAX_TRAFFIC_LINES];
	int LinesCount=MAX_TRAFFIC_LINES;
	for(int i=0;i<LinesCount;i++){
	//Just allocate memory here
		Lines[i]=(char*)malloc(LINE_LEN*sizeof(char));
	}

	//Now populate those lines
  	int lineCount=tokenizeString(buffer,"\n",Lines);
	trafficLinesCount=lineCount;
	if(logs){
		printf("Traffic Lines Count:%d\n",trafficLinesCount);
	}
	int nodeCount=lineCount;
  	traffic = (int **) malloc(lineCount * sizeof(int *));
  	for(int i=0;i<nodeCount;i++){
		traffic[i]=(int*)malloc(3*sizeof(int));
	}

	for(int i=0;i<lineCount;i++){
		char* line=Lines[i];
		storeTokenizeString(line," ",traffic[i]);
  	}
	if(logs){
		print2DVec(traffic,lineCount,3);
		printf("\n");
	}
}




void readFile(char *filePath){
  char data[MAX_NODES][MAX_NODES];
  FILE *fp;
  fp =fopen(filePath,"r");
  char buffer[BUFFER_SIZE]={0};

  while(!feof(fp)){
	fread(buffer, sizeof(buffer), 1, fp);
  }

  // Now Lets read lines

  //Declare Container for storing lines
  char* Lines[LINE_LEN];
  int LinesCount=11;
	for(int i=0;i<LinesCount;i++){
	//Just allocate memory here
		Lines[i]=(char*)malloc(LINE_LEN*sizeof(char));
	}

  //Now populate those lines
  int lineCount=tokenizeString(buffer,"\n",Lines);

  int nodeCount=lineCount;
  link_costs = (int **) malloc(2*nodeCount * sizeof(int *));
  for(int i=0;i<nodeCount;i++){
		link_costs[i]=(int*)malloc(nodeCount*sizeof(int));
	}

	num_nodes=nodeCount;
  

  //Now iterate lines and store the tokens - cost here in 'link_costs'
  for(int i=0;i<lineCount;i++){
	char* line=Lines[i];
	storeTokenizeString(line," ",link_costs[i]);
  }

	//set neighbours
	setNeighbours(num_nodes);

  if(logs){
	printf("the Link Cost Vector is:\n");
	print2DVec(link_costs,num_nodes,num_nodes);
  }
}

void main(int argc, char *argv[])
{
	struct event *eventptr;
	char filePath[128];
	char trafficFilePath[128];
	kMax=10;

	kMax = atoi(argv[1]);
	strcpy(filePath,argv[2]);
	strcpy(trafficFilePath,argv[3]);


	// //my code
	// char *filePath;
	// filePath="./topo_raj2.txt";
	// char* trafficFilePath;
	// trafficFilePath="./traffic_4.txt";

	readFile(filePath);
	readTraffic(trafficFilePath);

	int nodesUpdatedCount=0;
	//Tells if a node is updated or not
	updatedNodes = (int *)malloc(num_nodes * sizeof(int));
	dts = (struct distance_table *) malloc(num_nodes * sizeof(struct distance_table));
	fts = (struct forwardingTable *) malloc((num_nodes * sizeof(struct forwardingTable)));
	
	//now create dts for each node- allocate memory
	for(int i =0;i<num_nodes;i++){
		dts[i].costs=(int **) malloc(2*num_nodes* sizeof(int));
		//for each costs 2d vec : allocate memory
		for(int j=0;j<num_nodes;j++){
			dts[i].costs[j]=(int*)malloc(num_nodes * sizeof(int));
		}
	}

	setNeighbours(num_nodes);

	//now create fts for each node - allocate memory
	for(int i =0;i<num_nodes;i++){
		fts[i].costToNodes=(int *) malloc(num_nodes* sizeof(int));
		fts[i].nextHopToNodes=(int *) malloc(num_nodes * sizeof(int));
	}

	// printf("k:%d\n",k);
	k++;
	for (int i = 0; i < num_nodes; i++)
	{
		rtinit(&dts[i], &fts[i], i, link_costs[i], num_nodes);
	}

	// printf("\n");
	//log
	if(logs){
		for(int i=0;i<num_nodes;i++){
		printf("Print DTS %d\n",i);
		print2DVec(dts[i].costs,num_nodes,num_nodes);
		printf("\n");
		}
	}

	//check how many nodes are updated
	for(int i=0;i<num_nodes;i++){
		if(isNodeUpdated(i)==true){
			nodesUpdatedCount++;
		}
	}


	while (1) 
	{
		//logic to when print DTS k=[1,2,3,4,5,10,20....]
		if(true){
			printf("k=%d:\n",k);
		}

		while(1){
			eventptr = evlist;            /* get next event to simulate */
			if (eventptr==NULL)
				break;
			evlist = evlist->next;        /* remove this event from event list */
			if (evlist!=NULL)
				evlist->prev=NULL;
			clocktime = eventptr->evtime;    /* update time to next event time */
			if (eventptr->evtype == FROM_LAYER2 ){
				rtupdate(&dts[eventptr->eventity], &fts[eventptr->eventity], *(eventptr->rtpktptr));
			}else {
				printf("Panic: unknown event type\n"); exit(0);
			}
			
			if (eventptr->evtype == FROM_LAYER2 ){
				free(eventptr->rtpktptr);        /* free memory for packet, if any */
			} 
			free(eventptr);   
		}

		//now check if a node is updated and if yes send info to ngbrs
		for(int nodeId=0;nodeId<num_nodes;nodeId++){
			if(isNodeUpdated(nodeId)){
				sendInfoToNeightbour(nodeId,&dts[nodeId]);
			}
		}

		//routing stuff
		for (int i = 0; i < trafficLinesCount; i++)
  		{
			int src=traffic[i][0];
			int dest=traffic[i][1];
			int pcktCount=traffic[i][2];

   			printf("%d %d %d %d", src, dest, pcktCount, src);
    		routeTraffic(src, dest, fts[src]);
    		printf("\n");
  		} 


		// if(canPrintSlots()){
  		// 	for(int ndIdx=0;ndIdx<num_nodes;ndIdx++){
		// 		printf("node-%d:",ndIdx);
		// 		print1DVec(dts[ndIdx].costs[ndIdx],num_nodes);
		// 		printf("\n");
		// 	}
		// }

		k++;
	
		// updated nodes processed so resetting it
		nodesUpdatedCount=0;
		for(int nodeIdx=0;nodeIdx<num_nodes;nodeIdx++){
			if(isNodeUpdated(nodeIdx)){
				nodesUpdatedCount++;
				// update = 0
				setNodeAsNotUpdated(nodeIdx);
				
			}
		}

		
		if(k==kMax+1){
			goto terminate;
		}
	}
	terminate:
   		printf("\nSimulator terminated at t=%f, no packets in medium\n", clocktime);
}

/* jimsrand(): return a float in range [0,1].  The routine below is used to */
/* isolate all random number generation in one location.  We assume that the*/
/* system-supplied rand() function return an int in therange [0,mmm]        */
float jimsrand() 
{
  double mmm = 2147483647;   
  float x;                   
  x = rand()/mmm;            
  return(x);
}  



void insertevent(struct event *p)
{
   struct event *q,*qold;

   q = evlist;     /* q points to header of list in which p struct inserted */
   if (q==NULL) {   /* list is empty */
		evlist=p;
		p->next=NULL;
		p->prev=NULL;
		}
	 else {
		for (qold = q; q !=NULL && p->evtime > q->evtime; q=q->next)
			  qold=q; 
		if (q==NULL) {   /* end of list */
			 qold->next = p;
			 p->prev = qold;
			 p->next = NULL;
			 }
		   else if (q==evlist) { /* front of list */
			 p->next=evlist;
			 p->prev=NULL;
			 p->next->prev=p;
			 evlist = p;
			 }
		   else {     /* middle of list */
			 p->next=q;
			 p->prev=q->prev;
			 q->prev->next=p;
			 q->prev=p;
			 }
		 }
}

void printevlist()
{
  struct event *q;
  printf("--------------\nEvent List Follows:\n");
  for(q = evlist; q!=NULL; q=q->next) {
	printf("Event time: %f, type: %d entity: %d\n",q->evtime,q->evtype,q->eventity);
	}
  printf("--------------\n");
}


/************************** send update to neighbor (packet.destid)***************/
void send2neighbor(struct rtpkt packet)
{

  struct event *evptr, *q;
  float jimsrand(),lastime;
  int i;

  struct rtpkt *packet_copy = (struct rtpkt *)malloc(sizeof(struct rtpkt));
	packet_copy->sourceid = packet.sourceid;
	packet_copy->destid = packet.destid;
	packet_copy->mincost = (int *)malloc(num_nodes * sizeof(int));
	for (i = 0; i < num_nodes; i++)
	{
		packet_copy->mincost[i] = packet.mincost[i];
	}

	
 /* be nice: check if source and destination id's are reasonable */
 if (packet.sourceid<0 || packet.sourceid >num_nodes) {
   printf("WARNING: illegal source id in your packet, ignoring packet!\n");
   return;
   }
 if (packet.destid<0 || packet.destid > num_nodes) {
   printf("WARNING: illegal dest id in your packet, ignoring packet!\n");
   return;
   }
 if (packet.sourceid == packet.destid)  {
   printf("WARNING: source and destination id's the same, ignoring packet!\n");
   return;
   }


/* create future event for arrival of packet at the other side */
  evptr = (struct event *)malloc(sizeof(struct event));
  evptr->evtype =  FROM_LAYER2;   /* packet will pop out from layer3 */
  evptr->eventity = packet.destid; /* event occurs at other entity */
  evptr->rtpktptr = packet_copy;       /* save ptr to my copy of packet */

/* finally, compute the arrival time of packet at the other end.
   medium can not reorder, so make sure packet arrives between 1 and 10
   time units after the latest arrival time of packets
   currently in the medium on their way to the destination */
 lastime = clocktime;
 for (q=evlist; q!=NULL ; q = q->next) 
	if ( (q->evtype==FROM_LAYER2  && q->eventity==evptr->eventity) ) 
	  lastime = q->evtime;
 evptr->evtime =  lastime + 2.*jimsrand();
 insertevent(evptr);
} 

