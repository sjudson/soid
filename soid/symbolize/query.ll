; ModuleID = './query1.cpp'
source_filename = "./query1.cpp"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@.str = private unnamed_addr constant [8 x i8] c"started\00", align 1
@.str.1 = private unnamed_addr constant [6 x i8] c"start\00", align 1
@.str.2 = private unnamed_addr constant [6 x i8] c"close\00", align 1
@.str.3 = private unnamed_addr constant [5 x i8] c"heat\00", align 1
@.str.4 = private unnamed_addr constant [6 x i8] c"error\00", align 1

; Function Attrs: noinline norecurse uwtable
define dso_local i32 @main(i32, i8**) #0 !dbg !7 {
  %3 = alloca i32, align 4
  %4 = alloca i8**, align 8
  %5 = alloca i8, align 1
  %6 = alloca i8, align 1
  %7 = alloca i8, align 1
  %8 = alloca i8, align 1
  %9 = alloca i8, align 1
  store i32 %0, i32* %3, align 4
  call void @llvm.dbg.declare(metadata i32* %3, metadata !15, metadata !DIExpression()), !dbg !16
  store i8** %1, i8*** %4, align 8
  call void @llvm.dbg.declare(metadata i8*** %4, metadata !17, metadata !DIExpression()), !dbg !18
  call void @llvm.dbg.declare(metadata i8* %5, metadata !19, metadata !DIExpression()), !dbg !21
  call void @llvm.dbg.declare(metadata i8* %6, metadata !22, metadata !DIExpression()), !dbg !23
  call void @llvm.dbg.declare(metadata i8* %7, metadata !24, metadata !DIExpression()), !dbg !25
  call void @llvm.dbg.declare(metadata i8* %8, metadata !26, metadata !DIExpression()), !dbg !27
  call void @llvm.dbg.declare(metadata i8* %9, metadata !28, metadata !DIExpression()), !dbg !29
  call void @klee_make_symbolic(i8* %5, i64 1, i8* getelementptr inbounds ([8 x i8], [8 x i8]* @.str, i64 0, i64 0)), !dbg !30
  call void @klee_make_symbolic(i8* %6, i64 1, i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str.1, i64 0, i64 0)), !dbg !31
  call void @klee_make_symbolic(i8* %7, i64 1, i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str.2, i64 0, i64 0)), !dbg !32
  call void @klee_make_symbolic(i8* %8, i64 1, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @.str.3, i64 0, i64 0)), !dbg !33
  call void @klee_make_symbolic(i8* %9, i64 1, i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str.4, i64 0, i64 0)), !dbg !34
  %10 = load i8, i8* %9, align 1, !dbg !35
  %11 = trunc i8 %10 to i1, !dbg !35
  %12 = zext i1 %11 to i32, !dbg !35
  %13 = icmp eq i32 %12, 1, !dbg !36
  %14 = zext i1 %13 to i64, !dbg !35
  call void @klee_assume(i64 %14), !dbg !37
  ret i32 0, !dbg !38
}

; Function Attrs: nounwind readnone speculatable
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

declare dso_local void @klee_make_symbolic(i8*, i64, i8*) #2

declare dso_local void @klee_assume(i64) #2

attributes #0 = { noinline norecurse uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { nounwind readnone speculatable }
attributes #2 = { "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!3, !4, !5}
!llvm.ident = !{!6}

!0 = distinct !DICompileUnit(language: DW_LANG_C_plus_plus, file: !1, producer: "clang version 9.0.1-+20210312025454+c1a0a213378a-1~exp1~20210312140025.114 ", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, enums: !2, nameTableKind: None)
!1 = !DIFile(filename: "query1.cpp", directory: "/home/sjudson/Documents/work/yale/research/episacc/soid/examples/microwave/query")
!2 = !{}
!3 = !{i32 2, !"Dwarf Version", i32 4}
!4 = !{i32 2, !"Debug Info Version", i32 3}
!5 = !{i32 1, !"wchar_size", i32 4}
!6 = !{!"clang version 9.0.1-+20210312025454+c1a0a213378a-1~exp1~20210312140025.114 "}
!7 = distinct !DISubprogram(name: "main", scope: !8, file: !8, line: 3, type: !9, scopeLine: 3, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !2)
!8 = !DIFile(filename: "./query1.cpp", directory: "/home/sjudson/Documents/work/yale/research/episacc/soid/examples/microwave/query")
!9 = !DISubroutineType(types: !10)
!10 = !{!11, !11, !12}
!11 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!12 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !13, size: 64)
!13 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !14, size: 64)
!14 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!15 = !DILocalVariable(name: "argc", arg: 1, scope: !7, file: !8, line: 3, type: !11)
!16 = !DILocation(line: 3, column: 15, scope: !7)
!17 = !DILocalVariable(name: "argv", arg: 2, scope: !7, file: !8, line: 3, type: !12)
!18 = !DILocation(line: 3, column: 27, scope: !7)
!19 = !DILocalVariable(name: "started", scope: !7, file: !8, line: 5, type: !20)
!20 = !DIBasicType(name: "bool", size: 8, encoding: DW_ATE_boolean)
!21 = !DILocation(line: 5, column: 8, scope: !7)
!22 = !DILocalVariable(name: "start", scope: !7, file: !8, line: 5, type: !20)
!23 = !DILocation(line: 5, column: 17, scope: !7)
!24 = !DILocalVariable(name: "close", scope: !7, file: !8, line: 5, type: !20)
!25 = !DILocation(line: 5, column: 24, scope: !7)
!26 = !DILocalVariable(name: "heat", scope: !7, file: !8, line: 5, type: !20)
!27 = !DILocation(line: 5, column: 31, scope: !7)
!28 = !DILocalVariable(name: "error", scope: !7, file: !8, line: 5, type: !20)
!29 = !DILocation(line: 5, column: 37, scope: !7)
!30 = !DILocation(line: 7, column: 3, scope: !7)
!31 = !DILocation(line: 8, column: 3, scope: !7)
!32 = !DILocation(line: 9, column: 3, scope: !7)
!33 = !DILocation(line: 10, column: 3, scope: !7)
!34 = !DILocation(line: 11, column: 3, scope: !7)
!35 = !DILocation(line: 13, column: 16, scope: !7)
!36 = !DILocation(line: 13, column: 22, scope: !7)
!37 = !DILocation(line: 13, column: 3, scope: !7)
!38 = !DILocation(line: 14, column: 1, scope: !7)
