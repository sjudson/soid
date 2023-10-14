cc=../../../../deps/llvm-project/release/bin/clang -std=c99
opt=../../../../deps/llvm-project/release/bin/opt

BC=./inter.bc

KLEE=../../../../deps/klee-float/include/klee
KEXEC=../../../../deps/klee-float/build/bin/klee
PRE-LIB-KLEE=-L ../../../../deps/klee-float/build/lib/
POST-LIB-KLEE=-lkleeRuntest

SOIDLIB=../../../../soid/soidlib

symbolic:
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./float.c -o $(BC)
	$(KEXEC) -silent-klee-assume -write-smt2s -use-merge $(BC)

clean:
	rm -f ./inter.bc
	rm -rf ./klee-out-*
	rm -rf ./klee-last
