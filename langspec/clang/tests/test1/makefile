
CC = afl-cc 
LD = afl-cc 

SOURCE_PATH  = source
INCLUDE_PATH = include
OBJ_PATH     = obj

CFLAGS       = -O2 -g -I$(INCLUDE_PATH) -emit-llvm
LD_CFLAGS    = -flto -lxFuzztrace -lshmQueue

SOURCE_FILES = $(wildcard $(SOURCE_PATH)/*.c)
OBJ_FILES    = $(addprefix $(OBJ_PATH)/, $(addsuffix .o,$(notdir $(basename $(SOURCE_FILES)))))

TARGET = demo

.PHONY:all clean

all: $(TARGET)

$(TARGET): $(OBJ_FILES)
	$(LD) -o $@ $^ $(LD_CFLAGS)
	
$(OBJ_PATH)/%.o: $(SOURCE_PATH)/%.c
	@if [ ! -d $(OBJ_PATH) ];then mkdir $(OBJ_PATH); fi
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -rf $(OBJ_PATH) $(TARGET)
	rm branch_vars.bv cmp_statistic.info 
