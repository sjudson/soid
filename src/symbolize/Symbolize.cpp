#include "llvm/ADT/SCCIterator.h"
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
#include <map>
#include <toml++/toml.h>

using namespace llvm;


struct Location {
  int scc;
  std::string func;
  int bb;
  int instr;
};


struct Configuration {
  bool allow;                   // whether program variables are provided as allowlist or denylist
  std::string QueryFile;        // location of query IR

  std::set<std::string> E; // environmental variables
  std::set<std::string> S; // (input) state variables
  std::set<std::string> P; // program variables
  std::set<std::string> I; // all input variables
  std::set<std::string> V; // all variables
};
bool isin_set( std::string s, std::set<std::string> ss ) { return ss.find( s ) != ss.end(); }


struct Context {
  std::map<int, int> renamed;
  std::map<std::string, Location*> locations;
};
bool isin_map( std::string s, std::map<std::string, Location*> ms ) { return ms.find( s ) != ms.end(); }


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
  void parseError( int eno );
  void loadQuery( LLVMContext &Ctx );
  void transferGlobals( Module &M, Context *Ctx );
  void transferSymbolics( Module &M, Context *Ctx );
  void symbolize( Function &F );
  PreservedAnalyses run( Module &M, ModuleAnalysisManager &MAM );
};


void Symbolize::parseError( int eno ) {

  errs() << "\nInvalid configuration file.\n\t";
  switch( eno ) {
    case 0:
      errs() << "cannot parse toml\n";
      break;
    case 1:
      errs() << "cannot find constraintsFile entry\n";
      break;
    case 2:
      errs() << "cannot find environmental variable array\n";
      break;
    case 3:
      errs() << "cannot find state variable array\n";
      break;
    case 4:
      errs() << "cannot supply both an allow and a deny array of program variables\n";
      break;
    case 5:
      errs() << "must supply exactly one of an allow or a deny array of program variable\n";
      break;
    case 6:
      errs() << "unable to process environmental variable array: invalid type present\n";
      break;
    case 7:
      errs() << "unable to process state variable array: invalid type present\n";
      break;
    case 8:
      errs() << "unable to process program variable array: invalid type present\n";
      break;
    default:
      errs() << "\n";
  }

  exit( 1 );
}


void Symbolize::parseConfig() {

  toml::table tbl;

  try { tbl = toml::parse_file( Symbolize::ConfigFile ); }
  catch ( const toml::parse_error& err ) { Symbolize::parseError( 0 ); }

  std::optional<std::string> icf = tbl[ "headers" ][ "constraintsFile" ].value<std::string>();
  if ( !icf.has_value() ) { Symbolize::parseError( 1 ); }
  Symbolize::Config.QueryFile = *icf;

  toml::array *E, *S, *P;
  E = tbl[ "environmental" ][ "vars" ].as_array();
  if ( !E ) { Symbolize::parseError( 2 ); }
  S = tbl[ "state" ][ "vars" ].as_array();
  if ( !S ) { Symbolize::parseError( 3 ); }

  toml::array *allow = tbl[ "program" ][ "allow" ].as_array();
  toml::array *deny  = tbl[ "program" ][ "deny" ].as_array();

  if (  allow &&  deny ) { Symbolize::parseError( 4 ); }
  if ( !allow && !deny ) { Symbolize::parseError( 5 ); }
  Symbolize::Config.allow = ( allow ) ? ( ( P = allow ) && true ) : ( ( P = deny ) && false );

  std::string sel;
  for ( toml::node& elem : *E )
    { elem.visit( [&]( auto&& el ) noexcept { if constexpr ( toml::is_string<decltype(el)> ) {
                                                             Symbolize::Config.E.insert( el.get() );
                                                             Symbolize::Config.I.insert( el.get() );
                                                             Symbolize::Config.V.insert( el.get() ); }
                                              else { Symbolize::parseError( 6 ); } } ); }
  for ( toml::node& elem : *S )
    { elem.visit( [&]( auto&& el ) noexcept { if constexpr ( toml::is_string<decltype(el)> ) {
                                                             Symbolize::Config.S.insert( el.get() );
                                                             Symbolize::Config.I.insert( el.get() );
                                                             Symbolize::Config.V.insert( el.get() ); }
                                              else { Symbolize::parseError( 7 ); } } ); }
  for ( toml::node& elem : *P )
    { elem.visit( [&]( auto&& el ) noexcept { if constexpr ( toml::is_string<decltype(el)> ) {
                                                             Symbolize::Config.P.insert( el.get() );
                                                             Symbolize::Config.V.insert( el.get() ); }
                                              else { Symbolize::parseError( 8 ); } } ); }

  return;
}


void Symbolize::loadQuery( LLVMContext &Ctx ) { Symbolize::Query = parseIRFile( Symbolize::Config.QueryFile, Symbolize::Err, Ctx ); }


void Symbolize::transferGlobals( Module &M, Context *Ctx ) {

  std::string n;

  int in  = 0;
  int out = -1;
  bool placed;
  for ( GlobalVariable &g : Symbolize::Query->getGlobalList() ) {
    placed = false;

    while( !placed ) {
      out++;
      n = ".str" + ( ( out ) ? "." + std::to_string( out ) : "" );

      M.getOrInsertGlobal( n, g.getValueType(),
                           [&](){
                             GlobalVariable *ng = new GlobalVariable( M, g.getValueType(), g.isConstant(), GlobalValue::PrivateLinkage, g.getInitializer(), n );
                             ng->setUnnamedAddr( GlobalValue::UnnamedAddr::Global );
                             placed = true;
                             return ng;
                           });
    }
    Ctx->renamed[ in ] = out;
    in++;
  }

  return;
}


void Symbolize::transferSymbolics( Module &M, Context *Ctx ) {

  CallGraph cg = CallGraph( M );

  int si = 0;

  Function *F;
  for ( scc_iterator<CallGraph*> vs = scc_begin( &cg ), vse = scc_end( &cg ); vs != vse; ++vs ) {
    const std::vector<CallGraphNode*> &ns = *vs;

    for ( std::vector<CallGraphNode*>::const_iterator n = ns.begin(), ne = ns.end(); n != ne; ++n ) {
      F = (*n)->getFunction();

      if ( !F ) continue; // todo: explore implications

      //errs() << "\tFunction: " << F->getName() << "\n";
      //errs() << "\t\tnumber of arguments: " << F->arg_size() << "\n";

      DbgDeclareInst  *dbgDec;
      DbgValueInst    *dbgVal;
      DILocalVariable *dbgVar;

      Use *op;
      StringRef name;

      int bi = 0;
      int ii = 0;

      for ( BasicBlock &BB : *F ) {
        for ( Instruction &I : BB ) {

          dbgVar = nullptr;

          if ( dbgDec = dyn_cast<DbgDeclareInst>( &I ) ) dbgVar = dbgDec->getVariable();  // for higher optimization levels
          if ( dbgVal = dyn_cast<DbgValueInst>( &I ) )   dbgVar = dbgVal->getVariable();  // for lower optimization levels
          if ( !dbgVar ) continue;

          // todo: handle denylist case
          name = dbgVar->getName();
          if ( isin_set( name, Symbolize::Config.V ) ) {
            // if we already know of a location by the same name in the same SCC, error to prevent issues resolving loops
            // nb: there are cases that aren't ambiguous we fail on with this, we should make it more precise if possible
            if ( isin_map( name, Ctx->locations ) && Ctx->locations[ name ]->scc == si ) {
              errs() << "\nCannot resolve first declaration of " << name << ", ambiguous input to symbolize.\n\n";
              exit( 1 );
            }

            Ctx->locations[ name ] = new Location();
            Ctx->locations[ name ]->scc   = si;
            Ctx->locations[ name ]->func  = F->getName();
            Ctx->locations[ name ]->bb    = bi;
            Ctx->locations[ name ]->instr = ii;
          }

          //errs() << I << "\n\tname := " << name << "\n\tops  := ";

          /* GET INSTRUCTION OPERANDS */

          op = I.op_begin();
          while ( op ) {
            //if ( op != I.op_begin() ) errs() << " : ";

            Value *v = op->get();
            //v->printAsOperand( errs() );

            op = op->getNext();
          }
          //errs() << "\n\n";
          ii++;
        }
        bi++;
      }
    }
    si++;
  }
}


void Symbolize::symbolize( Function &F ) {}


PreservedAnalyses Symbolize::run( Module &M, ModuleAnalysisManager &MAM ) {
  parseConfig();
  loadQuery( M.getContext() );

  Context Ctx;

  transferGlobals( M, &Ctx );
  transferSymbolics( M, &Ctx );

  for ( Function &F : M ) symbolize( F );

  return PreservedAnalyses::none();
}



/****************************
 * LOAD PLUGIN INTO MANAGER *
 ****************************/


PassPluginLibraryInfo getSymbolizePluginInfo() {
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
