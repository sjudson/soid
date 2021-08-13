cc=clang++-9 -std=c++11

BC=./inter.bc

KLEE=./klee/include/klee
KEXEC=./klee/build/bin/klee
PRE-LIB-KLEE=-L ./klee/build/lib/
POST-LIB-KLEE=-lkleeRuntest

mw:
	$(cc) -I $(KLEE) -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone ./src/microwave.cpp -o $(BC)
	$(KEXEC) -libc=uclibc -libcxx -silent-klee-assume --write-smt2s $(BC)
	$(cc) -I $(KLEE) $(PRE-LIB-KLEE) ./src/microwave.cpp -o ./run_tests $(POST-LIB-KLEE)
	chmod +x ./run_tests

clean:
	rm -f ./inter.bc
	rm -f ./run_tests
	rm -rf ./klee-out-*
	rm -rf ./klee-last
