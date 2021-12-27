cc=../../../llvm-project/release/bin/clang -std=c99
link=../../../llvm-project/release/bin/llvm-link

BC1=./inter1.bc
BC2=./inter2.bc
BC3=./inter3.bc
BC4=./inter4.bc
BC5=./inter5.bc
BC6=./inter6.bc
BC=./inter.bc

KLEE=../../../klee-float/include/klee
KEXEC=../../../klee-float/build/bin/klee
PRE-LIB-KLEE=-L ../../../klee-float/build/lib/
POST-LIB-KLEE=-lkleeRuntest

SOIDLIB=../../../soid/soidlib

symbolic:
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./car.c -o $(BC1)
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./intersection.c -o $(BC2)
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./lcar.c -o $(BC3)
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./learn.c -o $(BC4)
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./util.c -o $(BC5)
	$(cc) -Dsymbolic -I $(SOIDLIB) -I $(KLEE) -emit-llvm -c -g -O0 ./agent.c -o $(BC6)
	$(link) $(BC1) $(BC2) $(BC3) $(BC4) $(BC5) $(BC6) -o $(BC)
	$(KEXEC) -silent-klee-assume -write-smt2s $(BC)

clean:
	rm -f ./inter*.bc
	rm -rf ./klee-out-*
	rm -rf ./klee-last
