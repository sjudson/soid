cc=../../../deps/llvm-project/release/bin/clang -std=c99
opt=../../../deps/llvm-project/release/bin/opt
link=../../../deps/llvm-project/release/bin/llvm-link

BC1=./inter1.bc
BC2=./inter2.bc

BC=./inter.bc

KLEE=../../../deps/klee-float/include/klee
KEXEC=../../../deps/klee-float/build/bin/klee
PRE-LIB-KLEE=-L ../../../deps/klee-float/build/lib/
POST-LIB-KLEE=-lkleeRuntest

SOIDLIB=../../../soid/soidlib

run:
	gcc classify.c -Drun -lcgraph -lm -o classify

symbolic:
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./tree.c -o - | $(opt) -mem2reg -simplifycfg -S -o $(BC1)
ifndef SOID_QUERY
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./classify.c -o - | $(opt) -mem2reg -simplifycfg -S -o $(BC2)
else
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./variants/$(SOID_QUERY).cpp -o - | $(opt) -mem2reg -simplifycfg -S -o $(BC2)
endif
	$(link) $(BC1) $(BC2) -o $(BC)
	$(KEXEC) -libc=uclibc -silent-klee-assume --write-smt2s -use-merge $(BC)

clean:
	rm -f ./classify
	rm -f ./inter*.bc
	rm -rf ./klee-out-*
	rm -rf ./klee-last
