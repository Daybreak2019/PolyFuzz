/***********************************************************
 * Author: Wen Li
 * Date  : 9/01/2020
 * Describe: DbCore.h - memory database 
 * History:
   <1> 9/01/2020 , create
************************************************************/

#ifndef _DB_H_
#define _DB_H_ 
#include "macro.h"

enum DB_TYPE
{
    DB_TYPE_BEGIN=1,
    DB_TYPE_SEED=DB_TYPE_BEGIN,
    DB_TYPE_SEED_BLOCK,
    DB_TYPE_BR_VARIABLE,
    DB_TYPE_BR_VARIABLE_KEY,
    DB_TYPE_END
};

typedef struct tag_DbReq
{
    BYTE* pKeyCtx;
    DWORD dwKeyLen;
    DWORD dwDataType;
    DWORD dwDataId;
}DbReq;

typedef struct tag_DbAck
{
    BYTE* pDataAddr;
    DWORD dwDataId;
    DWORD dwRev;
}DbAck;


DWORD CreateDataByKey(DbReq* ptCreateReq, DbAck* pCreateAck);
DWORD QueryDataByKey(DbReq* ptQueryKey, DbAck* pQueryAck);


DWORD CreateDataNonKey(DbReq* ptCreateReq, DbAck* pCreateAck);
DWORD QueryDataByID(DbReq* ptQueryReq, DbAck* pQueryAck);


DWORD DeleteDataByID(DbReq* ptDelReq);
DWORD DbCreateTable(DWORD dwDataType, DWORD dwDataNum, DWORD dwDataLen, DWORD dwKeyLen);

DWORD QueryDataNum (DWORD dwDataType);
DWORD TableSize (DWORD dwDataType);


VOID DelDb ();
VOID InitDb (VOID *Addr);
VOID* GetDbAddr ();

#ifdef __cplusplus
}
#endif


#endif
