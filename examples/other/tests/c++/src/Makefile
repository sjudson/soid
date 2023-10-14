cc=clang++-9 -std=c++14

BC=./inter.bc

KLEE=../../../klee/include/klee
KEXEC=../../../klee/build/bin/klee
PRE-LIB-KLEE=-L ../../../klee/build/lib/
POST-LIB-KLEE=-lkleeRuntest

SOIDLIB=../../../soid/soidlib

symbolic:
ifndef SOID_QUERY
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone ./microwave.cpp -o $(BC)
else
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone ./variants/$(SOID_QUERY).cpp -o $(BC)
endif
	$(KEXEC) -libc=uclibc -libcxx -silent-klee-assume --write-smt2s $(BC)

clean:
	rm -f ./inter.bc
	rm -rf ./klee-out-*
	rm -rf ./klee-last
