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

#include <optional>
#include <iostream>
#include <string>
#include <vector>
#include <toml++/toml.h>

using namespace llvm;


struct Configuration {
  bool allow;            // whether program variables are provided as allowlist or denylist
  std::string QueryFile; // location of query IR

  std::vector<std::string> env; // environmental variables
  std::vector<std::string> ist; // (input) state variables
  std::vector<std::string> prg; // program variables
};


struct Symbolize : PassInfoMixin<Symbolize> {
  // since we can't take cmdline args with the new pass manager
  // we will need to hardcode in the location of the query code
  //
  // this should not be a problem since it'll be produced by an
  // automated pipeline...
  std::string ConfigFile = "../query.config.toml";
  Configuration Config;

  SMDiagnostic Err;
  std::unique_ptr<Module> Query;

  void parseConfig();
  void loadQuery( LLVMContext &Ctx );
  void transferGlobals( Module &M );
  void symbolize( Function &F );
  PreservedAnalyses run( llvm::Module &M, llvm::ModuleAnalysisManager &MAM );
};


void Symbolize::parseConfig() {

  toml::table tbl;

  try { tbl = toml::parse_file( Symbolize::ConfigFile ); }
  catch ( const toml::parse_error& err ) {
    std::cerr << "Unable to parse configuration file:\n" << err << "\n";
    exit( 1 );
  }

  std::optional<std::string> icf = tbl[ "headers" ][ "inputConstraintsFile" ].value<std::string>();
  // todo: error if not present
  Symbolize::Config.QueryFile = *icf;

  toml::array *env, *ist, *prg;
  env = tbl[ "environmental" ][ "vars" ].as_array();
  if ( !env ) {} // todo: error
  ist = tbl[ "state" ][ "vars" ].as_array();
  if ( !ist ) {} // todo: error

  toml::array *allow = tbl[ "program" ][ "allow" ].as_array();
  toml::array *deny  = tbl[ "program" ][ "deny" ].as_array();

  if (  allow &&  deny ) {} // todo: error
  if ( !allow && !deny ) {} // todo: error
  Symbolize::Config.allow = ( allow ) ? ( ( prg = allow ) && true ) : ( ( prg = deny ) && false );

  // todo: handle bad types
  for ( toml::node& elem : *env )
    { elem.visit( [&]( auto&& el ) noexcept { if constexpr ( toml::is_string<decltype(el)> ) Symbolize::Config.env.push_back( el.get() ); } ); };
  for ( toml::node& elem : *ist )
    { elem.visit( [&]( auto&& el ) noexcept { if constexpr ( toml::is_string<decltype(el)> ) Symbolize::Config.ist.push_back( el.get() ); } ); };
  for ( toml::node& elem : *prg )
    { elem.visit( [&]( auto&& el ) noexcept { if constexpr ( toml::is_string<decltype(el)> ) Symbolize::Config.prg.push_back( el.get() ); } ); };

  return;
}


void Symbolize::loadQuery( LLVMContext &Ctx ) { Symbolize::Query = parseIRFile( Symbolize::Config.QueryFile, Symbolize::Err, Ctx ); }


void Symbolize::transferGlobals( Module &M ) {

  std::string n;

  std::string type_str1, type_str2;
  raw_string_ostream rso1(type_str1);
  raw_string_ostream rso2(type_str2);

  // todo: name sure no name clashes if preexisting anonymous global strings
  int mark = 0;
  for ( GlobalVariable &g : Symbolize::Query->getGlobalList() ) {
    n = ".str" + ( ( mark++ ) ? "." + std::to_string( mark ) : "" );
    M.getOrInsertGlobal( n, g.getValueType(),
                         [&](){
                           GlobalVariable *ng = new GlobalVariable( M, g.getValueType(), g.isConstant(), GlobalValue::PrivateLinkage, g.getInitializer(), n );
                           ng->setUnnamedAddr( GlobalValue::UnnamedAddr::Global );
                           return ng;
                         });
  }

  return;
}


void Symbolize::symbolize( Function &F ) {

  //errs() << "Function: " << F.getName() << "\n";
  //errs() << "\tnumber of arguments: " << F.arg_size() << "\n";

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
      //errs() << I << "\n\tname := " << n << "\n\tops  := ";

      /* GET INSTRUCTION OPERANDS */

      op = I.op_begin();
      while ( op ) {
        //if ( op != I.op_begin() ) errs() << " : ";

        Value *v = op->get();
        //v->printAsOperand( errs(), true );

        op = op->getNext();
      }
      //errs() << "\n\n";
    }
  }
}


PreservedAnalyses Symbolize::run( llvm::Module &M, llvm::ModuleAnalysisManager &MAM ) {
  parseConfig();
  loadQuery( M.getContext() );

  transferGlobals( M );

  for ( Function &F : M ) symbolize( F );

  return PreservedAnalyses::none();
}



/****************************
 * LOAD PLUGIN INTO MANAGER *
 ****************************/


llvm::PassPluginLibraryInfo getSymbolizePluginInfo() {
  return { LLVM_PLUGIN_API_VERSION, "Symbolize", LLVM_VERSION_STRING,
           []( PassBuilder &PB ) {
             PB.registerPipelineParsingCallback(
                 []( StringRef Name, ModulePassManager &MPM,
                    ArrayRef<PassBuilder::PipelineElement> ) {
                  if ( Name == "symbolize" ) {
                    MPM.addPass( Symbolize() );
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
