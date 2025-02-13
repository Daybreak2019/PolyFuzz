export AFL_SKIP_BIN_CHECK=1

if [ ! -f "./tests/test-1" ]; then
	python gen_tests.py
fi

if [ ! -d "fuzz" ]; then
   mkdir -p fuzz/in
   cp ./tests/* fuzz/in/
fi

cd fuzz
afl-system-config

#enable debug for child process
#export AFL_DEBUG_CHILD=1

#enable crash exit code
export AFL_CRASH_EXITCODE=100

cp ../../py_summary.xml ./
if [ "$?" != "0" ]; then
	echo "copy py_summary.xml fail, please check the configuration!!!!"
	exit 0
fi
afl-fuzz $1 $2 -i in/ -o out -t 5000 -m none -d -- python ../op_mem.py  @@

