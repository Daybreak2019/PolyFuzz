
export AFL_SKIP_BIN_CHECK=1

cd Python
if [ ! -d "fuzz" ]; then
    mkdir -p fuzz/in
    cp ../tests/* fuzz/in/
    cp ../char.pat fuzz/
    cp ../stru.pat fuzz/
fi

cd fuzz

afl-system-config

#pilot fuzzing: max path length
export AFL_BB_NUM=1024

#enable debug for child process
export AFL_DEBUG_CHILD=1

#enable crash exit code 
export AFL_CRASH_EXITCODE=100

cp ../py_summary.xml ./
afl-fuzz $1 $2 -i in/ -o out -m none -d -- python ../Demo.py  @@

