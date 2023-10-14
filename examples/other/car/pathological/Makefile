cc=../../../deps/llvm-project/release/bin/clang -std=c99
opt=../../../deps/llvm-project/release/bin/opt
link=../../../deps/llvm-project/release/bin/llvm-link

BC1=./inter1.bc
BC2=./inter2.bc
BC3=./inter3.bc
BC4=./inter4.bc
BC5=./inter5.bc
BC6=./inter6.bc
BC=./inter.bc

KLEE=../../../deps/klee-float/include/klee
KEXEC=../../../deps/klee-float/build/bin/klee
PRE-LIB-KLEE=-L ../../../deps/klee-float/build/lib/
POST-LIB-KLEE=-lkleeRuntest

SOIDLIB=../../../soid/soidlib

symbolic:
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./variants/car.c -o - | $(opt) -mem2reg -simplifycfg -S -o $(BC1)
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./variants/intersection.c -o - | $(opt) -mem2reg -simplifycfg -S -o $(BC2)
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./variants/lcar.c -o - | $(opt) -mem2reg -simplifycfg -S -o $(BC3)
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./variants/learn.c -o - | $(opt) -mem2reg -simplifycfg -S -o $(BC4)
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./variants/util.c -o - | $(opt) -mem2reg -simplifycfg -S -o $(BC5)
ifndef SOID_QUERY
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./variants/agent.c.1 -o - | $(opt) -mem2reg -simplifycfg -S -o $(BC6)
else
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./variants/agent.$(SOID_QUERY).c -o - | $(opt) -mem2reg -simplifycfg -S -o $(BC6)
endif
	$(link) $(BC1) $(BC2) $(BC3) $(BC4) $(BC5) $(BC6) -o $(BC)
	$(KEXEC) -silent-klee-assume -write-smt2s -use-merge $(BC)

clean:
	rm -f ./inter*.bc
	rm -rf ./klee-out-*
	rm -rf ./klee-last
