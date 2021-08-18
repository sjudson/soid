#include "llvm/IR/DebugInfoMetadata.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/PassManager.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IRReader/IRReader.h"
#include "llvm/Pass.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/SourceMgr.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"

using namespace llvm;


void symbolize( Function &F, DomTreeNodeBase<BasicBlock> *Root ) {

  errs() << "Function: "<< F.getName() << "\n";
  errs() << "\tnumber of arguments: " << F.arg_size() << "\n";

  DbgDeclareInst  *dbgDec;
  DbgValueInst    *dbgVal;
  DILocalVariable *dbgVar;

  Use *op;
  StringRef n;

  for (BasicBlock &BB : F) {
    for (Instruction &I : BB) {

      /* GET DEBUG INFO FOR INSTRUCTION */

      dbgVar = nullptr;

      // for higher optimization levels
      if ( dbgDec = dyn_cast<DbgDeclareInst>( &I ) ) dbgVar = dbgDec->getVariable();

      // for lower optimization levels
      if ( dbgVal = dyn_cast<DbgValueInst>( &I ) ) dbgVar = dbgVal->getVariable();

      n = ( dbgVar ) ? dbgVar->getName() : "n/a";
      errs() << I << "\n\tname := " << n << "\n\tops  := ";

      /* GET INSTRUCTION OPERANDS */

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
  SMDiagnostic Err;
  std::unique_ptr<Module> Query = nullptr;

  // since we can't take cmdline args with the new pass manager
  // we will need to hardcode in the location of the query code
  //
  // this should not be a problem since it'll be produced by an
  // automated pipeline...
  std::string QueryFile = "../query.ll";

  PreservedAnalyses run( Function &F, FunctionAnalysisManager &FAM );
  void loadQuery( LLVMContext &Ctx );
};


PreservedAnalyses Symbolize::run ( Function &F, FunctionAnalysisManager &FAM ) {
  if ( !Symbolize::Query ) loadQuery( F.getContext() );

  DominatorTree *DT = &FAM.getResult<DominatorTreeAnalysis>( F );
  symbolize( F, DT->getRootNode() );

  return PreservedAnalyses::none();
}


void Symbolize::loadQuery( LLVMContext &Ctx ) { Symbolize::Query = parseIRFile( Symbolize::QueryFile, Symbolize::Err, Ctx ); }


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
