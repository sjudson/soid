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

  Function     *F;
  BasicBlock   *BB;
  Instruction  *I;
  DILocalScope *S;
};

struct Var {
  Location        *loc;
  DILocalVariable *dbg;
  Value           *decl;
};

struct Configuration {
  bool allow;                // whether program variables are provided as allowlist or denylist
  std::string QueryFile;     // location of query IR

  std::set<std::string> E;   // environmental variables
  std::set<std::string> S;   // (input) state variables
  std::set<std::string> P;   // program variables
  std::set<std::string> I;   // all input variables
  std::set<std::string> V;   // all variables
};
bool isin_vars( std::string s, std::set<std::string> ss ) { return ss.find( s ) != ss.end(); }


struct Context {
  std::map<std::string, GlobalVariable*> renamed;
  std::map<std::string, Var*> is;
  std::map<std::string, Var*> ps;
};
bool is_found( std::string s, std::map<std::string, Var*> ms ) { return ms.find( s ) != ms.end(); }


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

  DbgDeclareInst* extractDeclare( Instruction &I );
  //DbgValueInst* extractValue( Instruction &I );
  DILocalVariable* extractDebug( Instruction &I );

  void findVariables( Module &M, Context *Ctx );

  void transferGlobals( Module &M, Context *Ctx );
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

  std::string name;

  int in  = 0;
  int out = -1;
  bool placed;

  Constant *c;

  for ( GlobalVariable &g : Symbolize::Query->getGlobalList() ) {
    placed = false;

    while( !placed ) {
      out++;
      name = ".str" + ( ( out ) ? "." + std::to_string( out ) : "" );

      c = M.getOrInsertGlobal( name, g.getValueType(),
                           [&](){
                             GlobalVariable *ng = new GlobalVariable( M, g.getValueType(), g.isConstant(), GlobalValue::PrivateLinkage, g.getInitializer(), name );
                             ng->setUnnamedAddr( GlobalValue::UnnamedAddr::Global );
                             placed = true;
                             return ng;
                           });
    }

    Ctx->renamed[ g.getName() ] = cast<GlobalVariable>( c );
    in++;
  }

  return;
}

DbgDeclareInst* Symbolize::extractDeclare( Instruction &I ) {
  if ( DbgDeclareInst *dbgDec = dyn_cast<DbgDeclareInst>( &I ) ) return dbgDec;
  return nullptr;
}

//DbgValueInst* Symbolize::extractValue( Instruction &I ) {
//  return ( DbgValueInst *dbgVal = dyn_cast<DbgValueInst>( &I ) ) ? dbgVal : nullptr;
//}

DILocalVariable* Symbolize::extractDebug( Instruction &I ) {
  // which of these exists depends on optimization level, at the moment we assume declare
  if ( DbgDeclareInst *dbgDec = extractDeclare( I ) ) return dbgDec->getVariable();
  //if ( DbgValueInst   *dbgVal = extractValue( I ) )   return dbgVal->getVariable();

  return nullptr;
}

void Symbolize::findVariables( Module &M, Context *Ctx ) {

  Function *F;
  CallGraph cg = CallGraph( M );

  DILocalVariable *dbgVar;

  std::string stream, name, ename;
  raw_string_ostream osn( stream );

  // this iterator goes in post order, which is the opposite direction to which we need, and
  // unforunately it isn't bidirectional, so we cannot just reverse it using the builtin C++
  // tooling to do that
  //
  // at first glance this seems not be a problem, as we just "evict" definitions named as an
  // input variable as we go back up the call graph
  //
  // however, we need to error if we cannot distinguish the first declaration of the variable,
  // which will happen if its first (i.e., in the iterator, last) appearance is in a SCC where
  // the same name has already appeared
  //
  // so we keep a map to the two most recent SCCs where we've seen the name, and at the end can
  // error if the same value is in both slots
  //
  // nb: there are cases that aren't ambiguous we fail on with this, should be made more precise
  std::map<std::string, std::pair<int, int>> last_seen;

  int si = 0;
  for ( scc_iterator<CallGraph*> vs = scc_begin( &cg ), vse = scc_end( &cg ); vs != vse; ++vs ) {
    const std::vector<CallGraphNode*> &ns = *vs;

    for ( std::vector<CallGraphNode*>::const_iterator n = ns.begin(), ne = ns.end(); n != ne; ++n ) {
      F = ( *n )->getFunction();

      if ( !F ) continue; // todo: explore why this is necessary

      for ( BasicBlock &BB : *F ) {
        for ( Instruction &I : BB ) {

          dbgVar = Symbolize::extractDebug( I );
          if ( !dbgVar ) continue;

          stream.clear(); osn << dbgVar->getName().str(); osn.flush();
          name.clear(); name = osn.str();

          last_seen[ name ] = ( last_seen.find( name ) != last_seen.end() )
            ? std::pair<int, int>( si, -1 )
            : std::pair<int, int>( si, last_seen[ name ].first );

          bool in_I = isin_vars( name, Symbolize::Config.I );
          bool in_P = isin_vars( name, Symbolize::Config.P );
          if ( in_I || ( Symbolize::Config.allow && in_P ) || ( !Symbolize::Config.allow && !in_P ) ) {

            stream.clear(); osn << name << "." << si << "." << dbgVar->getScope()->getName() << "\n"; osn.flush();
            ename.clear(); ename = osn.str();

            Ctx->ps[ ename ] = new Var();

            Ctx->ps[ ename ]->dbg  = dbgVar;
            Ctx->ps[ ename ]->decl = dyn_cast<Value>( &I );

            Ctx->ps[ ename ]->loc = new Location();
            Ctx->ps[ ename ]->loc->_scc = si;

            Ctx->ps[ ename ]->loc->F  = F;
            Ctx->ps[ ename ]->loc->BB = &BB;
            Ctx->ps[ ename ]->loc->I  = &I;
            Ctx->ps[ ename ]->loc->S  = dbgVar->getScope();

            if ( isin_vars( name, Symbolize::Config.I ) ) Ctx->is[ name ] = Ctx->ps[ ename ];
          }
        }
      }
    }
    si++;
  }

  // if we already know of a location by the same name in the same SCC, error to prevent issues resolving loops
  for ( auto const& ls : last_seen ) {
    if ( ls.second.first != ls.second.second ) continue;
    errs() << "\nCannot resolve first declaration of " << ls.first << ", ambiguous input to symbolize.\n\n";
    exit( 1 );
  }
}



void Symbolize::transferSymbolics( Module &M, Context *Ctx ) {

  StringRef fname;
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

  _klee_make_symbolic = M.getOrInsertFunction( "klee_make_symbolic", __klee_make_symbolic->getFunctionType(), __klee_make_symbolic->getAttributes() );
  klee_make_symbolic  = cast<Function>( _klee_make_symbolic.getCallee() );

  // todo: figure out if klee_assume may not exist (do we just e.g. force it with klee_assume( true ) in the header?)
  _klee_assume = M.getOrInsertFunction( "klee_assume", __klee_assume->getFunctionType(), __klee_assume->getAttributes() );
  klee_assume  = cast<Function>( _klee_assume.getCallee() );

  DbgDeclareInst  *dbgDec;
  DILocalVariable *dbgVar;
  AllocaInst *alloca;

  std::map<Value*, std::string> nmap;
  std::string stream, name;
  raw_string_ostream osn( stream );

  Value *vop, *nvop, *nvptr;

  for ( Function &F : *Symbolize::Query ) {
    for ( BasicBlock &BB : F ) {
      for ( Instruction &I : BB ) {
        if ( dbgDec = Symbolize::extractDeclare( I ) ) {

          alloca = dyn_cast<AllocaInst>( dbgDec->getAddress() ); // todo: handle error case

          dbgVar = Symbolize::extractDebug( I );
          stream.clear(); osn << dbgVar->getName().str(); osn.flush();
          name.clear(); name = osn.str();

          nmap[ dyn_cast<Value>( alloca ) ] = name;

          continue;
        }

        if ( !( CI = dyn_cast<CallInst>( &I ) ) ) continue;

        Function *called = CI->getCalledFunction();
        if ( !called ) continue; // todo: explore why this is necessary
        fname = called->getName();

        if ( ( make = ( fname != "klee_assume" ) ) && fname != "klee_make_symbolic" ) continue;

        if ( make ) {

          // TODO: FIGURE OUT HOW TO GET FROM
          // OPERAND -> METADATA -> NAME so that we can look it up
          //
          // I do need a instruction -> metadata map from the dbg declare I think...

          for ( auto const& x : nmap ) errs() << x.first << "|" << x.second << "\n";

          // map variable
          vop = I.getOperand( 0 );

          if ( namp.find( vop ) == nmap.end() ); // HANDLE ERROR CASE
          name.clear(); name = nmap[ vop ];

          if ( !is_found( name, Ctx->is ) );     // HANDLE ERROR CASE

          IRBuilder<> Builder( Ctx->is[ name ]->loc->I );

          nvop  = cast<Value>( Ctx->is[ name ]->loc->I );
          nvptr = Builder.CreateIntToPtr( nvop, vop->getType(), nvop->getName() + "_ptr" );

          // map size
          Value *nsop, *sop = I.getOperand( 1 );
          ConstantInt *cint = ConstantInt::get( M.getContext(), cast<ConstantInt>( sop )->getValue() );
          nsop = cast<Value>( cint );

          // map name
          // todo: handle case where name isn't a global variable
          Value *nnop, *nop = cast<GEPOperator>( I.getOperand( 2 ) )->getPointerOperand();
          GlobalVariable *nref = Ctx->renamed[ nop->getName() ];
          nnop = cast<Value>( nref );

          Builder.CreateCall( _klee_make_symbolic, { nvptr, nsop, nnop } );
        } else {
        }
      }
    }
  }
}


PreservedAnalyses Symbolize::run( Module &M, ModuleAnalysisManager &MAM ) {
  Symbolize::parseConfig();
  Symbolize::loadQuery( M.getContext() );

  Context Ctx;

  Symbolize::transferGlobals( M, &Ctx );     // transfer globals (e.g., symbolic names) from query to program
  Symbolize::findVariables( M, &Ctx );       // search program to find all program variable names + locations
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
