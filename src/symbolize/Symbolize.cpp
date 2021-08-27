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
  int _scc;

  Function *F;
  BasicBlock *BB;
  Instruction *I;
  DILocalScope *S;
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
bool isin_vars( std::string s, std::set<std::string> ss ) { return ss.find( s ) != ss.end(); }


struct Context {
  std::map<int, int> renamed;
  std::map<std::string, Location*> ilocs;
  std::map<std::string, Location*> plocs;
};
bool isin_locs( std::string s, std::map<std::string, Location*> ms ) { return ms.find( s ) != ms.end(); }


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
  void findVariables( Module &M, Context *Ctx );
  void transferSymbolics( Module &M, Context *Ctx );
  void symbolizeProgram( Module &M, Context *Ctx );
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


void Symbolize::findVariables( Module &M, Context *Ctx ) {

  CallGraph cg = CallGraph( M );

  int si = 0;

  Function *F;
  for ( scc_iterator<CallGraph*> vs = scc_begin( &cg ), vse = scc_end( &cg ); vs != vse; ++vs ) {
    const std::vector<CallGraphNode*> &ns = *vs;

    for ( std::vector<CallGraphNode*>::const_iterator n = ns.begin(), ne = ns.end(); n != ne; ++n ) {
      F = (*n)->getFunction();

      if ( !F ) continue; // todo: explore why this is necessary

      //errs() << "\tFunction: " << F->getName() << "\n";
      //errs() << "\t\tnumber of arguments: " << F->arg_size() << "\n";

      DbgDeclareInst  *dbgDec;
      DbgValueInst    *dbgVal;
      DILocalVariable *dbgVar;

      Use *op;
      StringRef name;
      std::string sname;

      for ( BasicBlock &BB : *F ) {
        for ( Instruction &I : BB ) {

          dbgVar = nullptr;

          // which of these exists depends on optimization level
          if ( dbgDec = dyn_cast<DbgDeclareInst>( &I ) ) dbgVar = dbgDec->getVariable();
          if ( dbgVal = dyn_cast<DbgValueInst>( &I ) )   dbgVar = dbgVal->getVariable();
          if ( !dbgVar ) continue;

          name = dbgVar->getName();

          // handle input vars
          if ( isin_vars( name, Symbolize::Config.I ) ) {
            // if we already know of a location by the same name in the same SCC, error to prevent issues resolving loops
            // nb: there are cases that aren't ambiguous we fail on with this, we should make it more precise if possible
            if ( isin_locs( name, Ctx->ilocs ) && Ctx->ilocs[ name ]->_scc == si ) {
              errs() << "\nCannot resolve first declaration of " << name << ", ambiguous input to symbolize.\n\n";
              exit( 1 );
            }

            Ctx->ilocs[ name ] = new Location();
            Ctx->ilocs[ name ]->_scc = si;

            Ctx->ilocs[ name ]->F  = F;
            Ctx->ilocs[ name ]->BB = &BB;
            Ctx->ilocs[ name ]->I  = &I;
            Ctx->ilocs[ name ]->S  = dbgVar->getScope();
          }

          // handle program vars
          int mark = 0;
          bool in_vars = isin_vars( name, Symbolize::Config.P );
          if ( ( Symbolize::Config.allow && in_vars ) || ( !Symbolize::Config.allow && !in_vars ) ) {

            while ( true ) {
              sname = name.str() + std::to_string( mark );
              if ( isin_locs( name, Ctx->plocs ) ) { mark++; continue; }

              Ctx->plocs[ sname ] = new Location();
              Ctx->plocs[ sname ]->_scc = -1;

              Ctx->plocs[ sname ]->F  = F;
              Ctx->plocs[ sname ]->BB = &BB;
              Ctx->plocs[ sname ]->I  = &I;
              Ctx->plocs[ sname ]->S  = dbgVar->getScope();
              break;
            }
          }
        }
      }
    }
    si++;
  }
}


void Symbolize::transferSymbolics( Module &M, Context *Ctx ) {

  StringRef name;
  bool make;

  CallInst *CI;

  Function *__klee_make_symbolic = Symbolize::Query->getFunction( "klee_make_symbolic" );
  Function *__klee_assume        = Symbolize::Query->getFunction( "klee_assume" );

  if ( !__klee_make_symbolic ) {
    errs() << "Cannot find any symbolic variables in query file.\n\n";
    exit( 1 );
  }

  FunctionCallee _klee_make_symbolic, _klee_assume;
  Function *klee_make_symbolic, *klee_assume;

  _klee_make_symbolic = M.getOrInsertFunction( "klee_make_symbolic", _klee_make_symbolic->getFunctionType(), _klee_make_symbolic->getAttributes() );
  klee_make_symbolic  = dyn_cast<Function>( _klee_make_symbolic.getCallee() );

  if ( __klee_assume ) {
    _klee_assume = M.getOrInsertFunction( "klee_assume", _klee_assume->getFunctionType(), _klee_assume->getAttributes() );
    klee_assume  = dyn_cast<Function>( _klee_assume.getCallee() );
  }

  for ( Function &F : *Symbolize::Query ) {
    for ( BasicBlock &BB : F ) {
      for ( Instruction &I : BB ) {
        if ( !( CI = dyn_cast<CallInst>( &I ) ) ) continue;

        Function *called = CI->getCalledFunction();
        if ( !called ) continue; // todo: explore why this is necessary
        name = called->getName();

        if ( make = ( name != "klee_assume" ) && name != "klee_make_symbolic" ) continue;

        if ( make ) {





        } else {




        }
      }
    }
  }
}


/*
//errs() << I << "\n\tname := " << name << "\n\tops  := ";


op = I.op_begin();
while ( op ) {
//if ( op != I.op_begin() ) errs() << " : ";

Value *v = op->get();
//v->printAsOperand( errs() );

op = op->getNext();
}
//errs() << "\n\n";
*/


PreservedAnalyses Symbolize::run( Module &M, ModuleAnalysisManager &MAM ) {
  Symbolize::parseConfig();
  Symbolize::loadQuery( M.getContext() );

  Context Ctx;

  Symbolize::transferGlobals( M, &Ctx );
  Symbolize::findVariables( M, &Ctx );
  Symbolize::transferSymbolics( M, &Ctx );

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
