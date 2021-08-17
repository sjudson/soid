#include "llvm/IR/DebugInfoMetadata.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/PassManager.h"
#include "llvm/IRReader/IRReader.h"
#include "llvm/Pass.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/SourceMgr.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"


using namespace llvm;

static cl::opt<std::string> QF{ "qir", cl::desc( "Specify filename for query LLVM IR" ), cl::value_desc( "filename" ) };


void symbolize( Function &F, DomTreeNodeBase<BasicBlock> *Root ) {

  errs() << "Function: "<< F.getName() << "\n";
  errs() << "\tnumber of arguments: " << F.arg_size() << "\n";

  DbgDeclareInst  *dbgDec;
  DbgValueInst    *dbgVal;
  DILocalVariable *dbgVar;

  Use *op;
  StringRef n, vn;

  for (BasicBlock &BB : F) {
    for (Instruction &I : BB) {

      // GET DEBUG INFO FOR INSTRUCTION //
      dbgVar = nullptr;

      // for higher optimization levels
      if ( dbgDec = dyn_cast<DbgDeclareInst>( &I ) ) dbgVar = dbgDec->getVariable();

      // for lower optimization levels
      if ( dbgVal = dyn_cast<DbgValueInst>( &I ) ) dbgVar = dbgVal->getVariable();

      n = ( dbgVar ) ? dbgVar->getName() : "n/a";
      errs() << I << "\n\tname := " << n << "\n\tops  := ";

      op = I.op_begin();
      while ( op ) {
        if ( op != I.op_begin() ) errs() << " : ";

        Value *v = op->get();
        v->printAsOperand( errs(), true );

        op = op->getNext();
      }
      errs() << "\n\n";
    }
  }
}


struct Symbolize : PassInfoMixin<Symbolize> {
  static LLVMContext  Ctx;
  static SMDiagnostic Err;
  std::unique_ptr<Module> Query = nullptr;

  PreservedAnalyses run( Function &F, FunctionAnalysisManager &FAM );
  void loadQuery();
};


PreservedAnalyses Symbolize::run ( Function &F, FunctionAnalysisManager &FAM ) {
  // TODO: FIXUP
  QF = "./query.ll";
  if ( !Symbolize::Query ) loadQuery();

  DominatorTree *DT = &FAM.getResult<DominatorTreeAnalysis>( F );
  symbolize( F, DT->getRootNode() );

  return PreservedAnalyses::none();
}


void Symbolize::loadQuery() { Symbolize::Query = parseIRFile( QF, Symbolize::Err, Symbolize::Ctx ); }


/****************************
 * LOAD PLUGIN INTO MANAGER *
 ****************************/


llvm::PassPluginLibraryInfo getSymbolizePluginInfo() {
  return { LLVM_PLUGIN_API_VERSION, "Symbolize", LLVM_VERSION_STRING,
           []( PassBuilder &PB ) {
             PB.registerPipelineParsingCallback(
                []( StringRef Name, FunctionPassManager &FPM,
                    ArrayRef<PassBuilder::PipelineElement> ) {
                  if ( Name == "symbolize" ) {
                    FPM.addPass( Symbolize() );
                    return true;
                  }
                  return false;
                });
           }};
}


extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
  return getSymbolizePluginInfo();
}
