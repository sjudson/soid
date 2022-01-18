cc=../../../llvm-project/release/bin/clang -std=c99

BC=./inter.bc

KLEE=../../../klee-float/include/klee
KEXEC=../../../klee-float/build/bin/klee
PRE-LIB-KLEE=-L ../../../klee-float/build/lib/
POST-LIB-KLEE=-lkleeRuntest

SOIDLIB=../../../soid/soidlib

symbolic:
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./bikes.c -o $(BC)
	$(KEXEC) -silent-klee-assume -write-smt2s $(BC)

clean:
	rm -f ./inter.bc
	rm -rf ./klee-out-*
	rm -rf ./klee-last
