export AFL_SKIP_BIN_CHECK=1

if [ ! -d "fuzz" ]; then
   mkdir -p fuzz/in
   cp -rf ../test_aubios/* fuzz/in/
fi

cd fuzz
#afl-system-config

#enable debug for child process
#export AFL_DEBUG_CHILD=1

#enable crash exit code
export AFL_CRASH_EXITCODE=100

cp ../../../py_summary.xml ./
if [ "$?" != "0" ]; then
	echo "copy py_summary.xml fail, please check the configuration!!!!"
	exit 0
fi

export AFL_PL_HAVOC_NUM=512
afl-fuzz $1 $2 -t 2000 -i in/ -o out -m none -d -- python ../slicing.py  @@

