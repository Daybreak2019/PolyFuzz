#include "list.h"

VOID ListInsert (List *L, VOID *N)
{
    LNode *LN = (LNode *) malloc (sizeof (LNode));
    assert (LN != NULL);

    LN->Data = N;
    LN->Nxt  = NULL;
    LN->Pre  = NULL;
    
    if (L->Header == NULL)
    {
        L->Header = LN;
        L->Tail   = LN;
    }
    else
    {
        L->Tail->Nxt = LN;
        LN->Pre = L->Tail;
        
        L->Tail = LN;
    }

    L->NodeNum++;

    return;
}


VOID ListRemove (List *L, LNode *N)
{
    if (L->NodeNum == 0)
    {
        return;
    }
    
    if (L->NodeNum == 1)
    {
        if (L->Header != N)
        {
            return;
        }
        
        L->Header = NULL;
        L->Tail   = NULL;

        free (N);
    }
    else
    {
        if (L->Header == N)
        {
            L->Header = L->Header->Nxt;
            free (N);
        }
        else
        {
            LNode *Ln = L->Header;
            while (Ln != N && Ln != NULL)
            {
                if (Ln->Nxt == N)
                {
                    break;
                }

                Ln = Ln->Nxt;
            }

            if (Ln == NULL)
            {
                return;
            }

            if (L->Tail == N)
            {
                L->Tail = Ln;
                Ln->Nxt = NULL;
            }
            else
            {
                Ln->Nxt = N->Nxt;
            }

            free (N);
        }         
    }

    L->NodeNum--;
    return;
}


VOID ListDel (List *L, DelData Del)
{
    if (L->NodeNum == 0)
    {
        return;
    }
    
    LNode *N = L->Header;
    LNode *Nxt;
    
    while (N != NULL)
    {
        Nxt = N->Nxt;

        if (Del)
        {
            Del (N->Data);
        }

        free (N);
        N = Nxt;
        L->NodeNum--;
    }

    L->Header = NULL;
    L->Tail   = NULL;
    L->NodeNum = 0;

    if (L->HeapAlloc == HEAP_ALLOC)
    {
        free (L);
    }
    
    return;
}

VOID ListVisit (List *L, ProcData Proc)
{
    if (L->NodeNum == 0)
    {
        return;
    }

    LNode *N = L->Header;
    while (N != NULL)
    {
        if (Proc)
        {
            Proc (N->Data);
        }

        N = N->Nxt;
    }

    return;
}


BOOL IsInList (List *L, CompData Proc, VOID *Data)
{
    if (L->NodeNum == 0)
    {
        return FALSE;
    }

    LNode *N = L->Header;
    while (N != NULL)
    {
        if (Proc (N->Data, Data) == TRUE)
        {
            return TRUE;
        }

        N = N->Nxt;
    }

    return FALSE;
}


VOID* ListSearch (List *L, CompData Proc, VOID *Data)
{
    if (L->NodeNum == 0)
    {
        return NULL;
    }

    LNode *N = L->Header;
    while (N != NULL)
    {
        if (Proc (N->Data, Data) == TRUE)
        {
            return N->Data;
        }

        N = N->Nxt;
    }

    return NULL;
}


List* ListAllot ()
{
    List *L = (List *) malloc (sizeof (List));
    assert (L != NULL);
    
    L->Header  = NULL;
    L->Tail    = NULL;
    L->NodeNum = 0;
    L->HeapAlloc = HEAP_ALLOC;
    
    return L;
}


