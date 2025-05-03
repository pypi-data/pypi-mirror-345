#include <stdio.h>
#include "pthread.h"


int main(long long u){
    pthread_t threadId = u;
    pthread_cancel(threadId);
    pthread_join(threadId, NULL);
    return 0;
}
