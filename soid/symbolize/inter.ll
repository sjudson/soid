; ModuleID = './microwave.cpp'
source_filename = "./microwave.cpp"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: noinline nounwind uwtable
define dso_local zeroext i8 @_Z6decidePbbbbb(i8*, i1 zeroext, i1 zeroext, i1 zeroext, i1 zeroext) #0 !dbg !96 {
  %6 = alloca i8, align 1
  %7 = alloca i8*, align 8
  %8 = alloca i8, align 1
  %9 = alloca i8, align 1
  %10 = alloca i8, align 1
  %11 = alloca i8, align 1
  store i8* %0, i8** %7, align 8
  call void @llvm.dbg.declare(metadata i8** %7, metadata !102, metadata !DIExpression()), !dbg !103
  %12 = zext i1 %1 to i8
  store i8 %12, i8* %8, align 1
  call void @llvm.dbg.declare(metadata i8* %8, metadata !104, metadata !DIExpression()), !dbg !105
  %13 = zext i1 %2 to i8
  store i8 %13, i8* %9, align 1
  call void @llvm.dbg.declare(metadata i8* %9, metadata !106, metadata !DIExpression()), !dbg !107
  %14 = zext i1 %3 to i8
  store i8 %14, i8* %10, align 1
  call void @llvm.dbg.declare(metadata i8* %10, metadata !108, metadata !DIExpression()), !dbg !109
  %15 = zext i1 %4 to i8
  store i8 %15, i8* %11, align 1
  call void @llvm.dbg.declare(metadata i8* %11, metadata !110, metadata !DIExpression()), !dbg !111
  %16 = load i8, i8* %9, align 1, !dbg !112
  %17 = trunc i8 %16 to i1, !dbg !112
  br i1 %17, label %19, label %18, !dbg !114

18:                                               ; preds = %5
  store i8 3, i8* %6, align 1, !dbg !115
  br label %35, !dbg !115

19:                                               ; preds = %5
  %20 = load i8, i8* %11, align 1, !dbg !117
  %21 = trunc i8 %20 to i1, !dbg !117
  br i1 %21, label %22, label %23, !dbg !119

22:                                               ; preds = %19
  store i8 1, i8* %6, align 1, !dbg !120
  br label %35, !dbg !120

23:                                               ; preds = %19
  %24 = load i8, i8* %8, align 1, !dbg !122
  %25 = trunc i8 %24 to i1, !dbg !122
  br i1 %25, label %26, label %27, !dbg !124

26:                                               ; preds = %23
  store i8 4, i8* %6, align 1, !dbg !125
  br label %35, !dbg !125

27:                                               ; preds = %23
  %28 = load i8*, i8** %7, align 8, !dbg !127
  %29 = load i8, i8* %28, align 1, !dbg !129
  %30 = trunc i8 %29 to i1, !dbg !129
  br i1 %30, label %31, label %33, !dbg !130

31:                                               ; preds = %27
  %32 = load i8*, i8** %7, align 8, !dbg !131
  store i8 0, i8* %32, align 1, !dbg !133
  store i8 2, i8* %6, align 1, !dbg !134
  br label %35, !dbg !134

33:                                               ; preds = %27
  %34 = load i8*, i8** %7, align 8, !dbg !135
  store i8 1, i8* %34, align 1, !dbg !136
  store i8 0, i8* %6, align 1, !dbg !137
  br label %35, !dbg !137

35:                                               ; preds = %33, %31, %26, %22, %18
  %36 = load i8, i8* %6, align 1, !dbg !138
  ret i8 %36, !dbg !138
}

; Function Attrs: nounwind readnone speculatable
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

; Function Attrs: noinline norecurse nounwind uwtable
define dso_local i32 @main(i32, i8**) #2 !dbg !139 {
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = alloca i8**, align 8
  %6 = alloca i8, align 1
  %7 = alloca i8, align 1
  %8 = alloca i8, align 1
  %9 = alloca i8, align 1
  %10 = alloca i8, align 1
  %11 = alloca i32, align 4
  store i32 0, i32* %3, align 4
  store i32 %0, i32* %4, align 4
  call void @llvm.dbg.declare(metadata i32* %4, metadata !145, metadata !DIExpression()), !dbg !146
  store i8** %1, i8*** %5, align 8
  call void @llvm.dbg.declare(metadata i8*** %5, metadata !147, metadata !DIExpression()), !dbg !148
  call void @llvm.dbg.declare(metadata i8* %6, metadata !149, metadata !DIExpression()), !dbg !150
  call void @llvm.dbg.declare(metadata i8* %7, metadata !151, metadata !DIExpression()), !dbg !152
  call void @llvm.dbg.declare(metadata i8* %8, metadata !153, metadata !DIExpression()), !dbg !154
  call void @llvm.dbg.declare(metadata i8* %9, metadata !155, metadata !DIExpression()), !dbg !156
  call void @llvm.dbg.declare(metadata i8* %10, metadata !157, metadata !DIExpression()), !dbg !158
  call void @llvm.dbg.declare(metadata i32* %11, metadata !159, metadata !DIExpression()), !dbg !160
  %12 = load i8, i8* %7, align 1, !dbg !161
  %13 = trunc i8 %12 to i1, !dbg !161
  %14 = load i8, i8* %8, align 1, !dbg !162
  %15 = trunc i8 %14 to i1, !dbg !162
  %16 = load i8, i8* %9, align 1, !dbg !163
  %17 = trunc i8 %16 to i1, !dbg !163
  %18 = load i8, i8* %10, align 1, !dbg !164
  %19 = trunc i8 %18 to i1, !dbg !164
  %20 = call zeroext i8 @_Z6decidePbbbbb(i8* %6, i1 zeroext %13, i1 zeroext %15, i1 zeroext %17, i1 zeroext %19), !dbg !165
  %21 = zext i8 %20 to i32, !dbg !165
  store i32 %21, i32* %11, align 4, !dbg !166
  ret i32 0, !dbg !167
}

attributes #0 = { noinline nounwind uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { nounwind readnone speculatable }
attributes #2 = { noinline norecurse nounwind uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!92, !93, !94}
!llvm.ident = !{!95}

!0 = distinct !DICompileUnit(language: DW_LANG_C_plus_plus, file: !1, producer: "clang version 9.0.1-+20210312025454+c1a0a213378a-1~exp1~20210312140025.114 ", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, enums: !2, imports: !3, nameTableKind: None)
!1 = !DIFile(filename: "microwave.cpp", directory: "/home/sjudson/Documents/work/yale/research/episacc/soid/examples/microwave/src")
!2 = !{}
!3 = !{!4, !12, !16, !20, !24, !27, !29, !31, !33, !36, !39, !42, !45, !48, !50, !55, !59, !63, !67, !69, !71, !73, !75, !78, !81, !84, !87, !90}
!4 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !6, file: !11, line: 48)
!5 = !DINamespace(name: "std", scope: null)
!6 = !DIDerivedType(tag: DW_TAG_typedef, name: "int8_t", file: !7, line: 24, baseType: !8)
!7 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/stdint-intn.h", directory: "")
!8 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int8_t", file: !9, line: 36, baseType: !10)
!9 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/types.h", directory: "")
!10 = !DIBasicType(name: "signed char", size: 8, encoding: DW_ATE_signed_char)
!11 = !DIFile(filename: "/usr/bin/../lib/gcc/x86_64-linux-gnu/8/../../../../include/c++/8/cstdint", directory: "")
!12 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !13, file: !11, line: 49)
!13 = !DIDerivedType(tag: DW_TAG_typedef, name: "int16_t", file: !7, line: 25, baseType: !14)
!14 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int16_t", file: !9, line: 38, baseType: !15)
!15 = !DIBasicType(name: "short", size: 16, encoding: DW_ATE_signed)
!16 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !17, file: !11, line: 50)
!17 = !DIDerivedType(tag: DW_TAG_typedef, name: "int32_t", file: !7, line: 26, baseType: !18)
!18 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int32_t", file: !9, line: 40, baseType: !19)
!19 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!20 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !21, file: !11, line: 51)
!21 = !DIDerivedType(tag: DW_TAG_typedef, name: "int64_t", file: !7, line: 27, baseType: !22)
!22 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int64_t", file: !9, line: 43, baseType: !23)
!23 = !DIBasicType(name: "long int", size: 64, encoding: DW_ATE_signed)
!24 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !25, file: !11, line: 53)
!25 = !DIDerivedType(tag: DW_TAG_typedef, name: "int_fast8_t", file: !26, line: 58, baseType: !10)
!26 = !DIFile(filename: "/usr/include/stdint.h", directory: "")
!27 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !28, file: !11, line: 54)
!28 = !DIDerivedType(tag: DW_TAG_typedef, name: "int_fast16_t", file: !26, line: 60, baseType: !23)
!29 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !30, file: !11, line: 55)
!30 = !DIDerivedType(tag: DW_TAG_typedef, name: "int_fast32_t", file: !26, line: 61, baseType: !23)
!31 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !32, file: !11, line: 56)
!32 = !DIDerivedType(tag: DW_TAG_typedef, name: "int_fast64_t", file: !26, line: 62, baseType: !23)
!33 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !34, file: !11, line: 58)
!34 = !DIDerivedType(tag: DW_TAG_typedef, name: "int_least8_t", file: !26, line: 43, baseType: !35)
!35 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int_least8_t", file: !9, line: 51, baseType: !8)
!36 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !37, file: !11, line: 59)
!37 = !DIDerivedType(tag: DW_TAG_typedef, name: "int_least16_t", file: !26, line: 44, baseType: !38)
!38 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int_least16_t", file: !9, line: 53, baseType: !14)
!39 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !40, file: !11, line: 60)
!40 = !DIDerivedType(tag: DW_TAG_typedef, name: "int_least32_t", file: !26, line: 45, baseType: !41)
!41 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int_least32_t", file: !9, line: 55, baseType: !18)
!42 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !43, file: !11, line: 61)
!43 = !DIDerivedType(tag: DW_TAG_typedef, name: "int_least64_t", file: !26, line: 46, baseType: !44)
!44 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int_least64_t", file: !9, line: 57, baseType: !22)
!45 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !46, file: !11, line: 63)
!46 = !DIDerivedType(tag: DW_TAG_typedef, name: "intmax_t", file: !26, line: 101, baseType: !47)
!47 = !DIDerivedType(tag: DW_TAG_typedef, name: "__intmax_t", file: !9, line: 71, baseType: !23)
!48 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !49, file: !11, line: 64)
!49 = !DIDerivedType(tag: DW_TAG_typedef, name: "intptr_t", file: !26, line: 87, baseType: !23)
!50 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !51, file: !11, line: 66)
!51 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint8_t", file: !52, line: 24, baseType: !53)
!52 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/stdint-uintn.h", directory: "")
!53 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint8_t", file: !9, line: 37, baseType: !54)
!54 = !DIBasicType(name: "unsigned char", size: 8, encoding: DW_ATE_unsigned_char)
!55 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !56, file: !11, line: 67)
!56 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint16_t", file: !52, line: 25, baseType: !57)
!57 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint16_t", file: !9, line: 39, baseType: !58)
!58 = !DIBasicType(name: "unsigned short", size: 16, encoding: DW_ATE_unsigned)
!59 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !60, file: !11, line: 68)
!60 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint32_t", file: !52, line: 26, baseType: !61)
!61 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint32_t", file: !9, line: 41, baseType: !62)
!62 = !DIBasicType(name: "unsigned int", size: 32, encoding: DW_ATE_unsigned)
!63 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !64, file: !11, line: 69)
!64 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint64_t", file: !52, line: 27, baseType: !65)
!65 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint64_t", file: !9, line: 44, baseType: !66)
!66 = !DIBasicType(name: "long unsigned int", size: 64, encoding: DW_ATE_unsigned)
!67 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !68, file: !11, line: 71)
!68 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint_fast8_t", file: !26, line: 71, baseType: !54)
!69 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !70, file: !11, line: 72)
!70 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint_fast16_t", file: !26, line: 73, baseType: !66)
!71 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !72, file: !11, line: 73)
!72 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint_fast32_t", file: !26, line: 74, baseType: !66)
!73 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !74, file: !11, line: 74)
!74 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint_fast64_t", file: !26, line: 75, baseType: !66)
!75 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !76, file: !11, line: 76)
!76 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint_least8_t", file: !26, line: 49, baseType: !77)
!77 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint_least8_t", file: !9, line: 52, baseType: !53)
!78 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !79, file: !11, line: 77)
!79 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint_least16_t", file: !26, line: 50, baseType: !80)
!80 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint_least16_t", file: !9, line: 54, baseType: !57)
!81 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !82, file: !11, line: 78)
!82 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint_least32_t", file: !26, line: 51, baseType: !83)
!83 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint_least32_t", file: !9, line: 56, baseType: !61)
!84 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !85, file: !11, line: 79)
!85 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint_least64_t", file: !26, line: 52, baseType: !86)
!86 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint_least64_t", file: !9, line: 58, baseType: !65)
!87 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !88, file: !11, line: 81)
!88 = !DIDerivedType(tag: DW_TAG_typedef, name: "uintmax_t", file: !26, line: 102, baseType: !89)
!89 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uintmax_t", file: !9, line: 72, baseType: !66)
!90 = !DIImportedEntity(tag: DW_TAG_imported_declaration, scope: !5, entity: !91, file: !11, line: 82)
!91 = !DIDerivedType(tag: DW_TAG_typedef, name: "uintptr_t", file: !26, line: 90, baseType: !66)
!92 = !{i32 2, !"Dwarf Version", i32 4}
!93 = !{i32 2, !"Debug Info Version", i32 3}
!94 = !{i32 1, !"wchar_size", i32 4}
!95 = !{!"clang version 9.0.1-+20210312025454+c1a0a213378a-1~exp1~20210312140025.114 "}
!96 = distinct !DISubprogram(name: "decide", linkageName: "_Z6decidePbbbbb", scope: !97, file: !97, line: 15, type: !98, scopeLine: 15, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !2)
!97 = !DIFile(filename: "./microwave.cpp", directory: "/home/sjudson/Documents/work/yale/research/episacc/soid/examples/microwave/src")
!98 = !DISubroutineType(types: !99)
!99 = !{!51, !100, !101, !101, !101, !101}
!100 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !101, size: 64)
!101 = !DIBasicType(name: "bool", size: 8, encoding: DW_ATE_boolean)
!102 = !DILocalVariable(name: "started", arg: 1, scope: !96, file: !97, line: 15, type: !100)
!103 = !DILocation(line: 15, column: 23, scope: !96)
!104 = !DILocalVariable(name: "start", arg: 2, scope: !96, file: !97, line: 15, type: !101)
!105 = !DILocation(line: 15, column: 37, scope: !96)
!106 = !DILocalVariable(name: "close", arg: 3, scope: !96, file: !97, line: 15, type: !101)
!107 = !DILocation(line: 15, column: 49, scope: !96)
!108 = !DILocalVariable(name: "heat", arg: 4, scope: !96, file: !97, line: 15, type: !101)
!109 = !DILocation(line: 15, column: 61, scope: !96)
!110 = !DILocalVariable(name: "error", arg: 5, scope: !96, file: !97, line: 15, type: !101)
!111 = !DILocation(line: 15, column: 72, scope: !96)
!112 = !DILocation(line: 18, column: 9, scope: !113)
!113 = distinct !DILexicalBlock(scope: !96, file: !97, line: 18, column: 8)
!114 = !DILocation(line: 18, column: 8, scope: !96)
!115 = !DILocation(line: 18, column: 19, scope: !116)
!116 = distinct !DILexicalBlock(scope: !113, file: !97, line: 18, column: 17)
!117 = !DILocation(line: 21, column: 9, scope: !118)
!118 = distinct !DILexicalBlock(scope: !96, file: !97, line: 21, column: 9)
!119 = !DILocation(line: 21, column: 9, scope: !96)
!120 = !DILocation(line: 21, column: 19, scope: !121)
!121 = distinct !DILexicalBlock(scope: !118, file: !97, line: 21, column: 17)
!122 = !DILocation(line: 24, column: 9, scope: !123)
!123 = distinct !DILexicalBlock(scope: !96, file: !97, line: 24, column: 9)
!124 = !DILocation(line: 24, column: 9, scope: !96)
!125 = !DILocation(line: 24, column: 19, scope: !126)
!126 = distinct !DILexicalBlock(scope: !123, file: !97, line: 24, column: 17)
!127 = !DILocation(line: 27, column: 9, scope: !128)
!128 = distinct !DILexicalBlock(scope: !96, file: !97, line: 27, column: 8)
!129 = !DILocation(line: 27, column: 8, scope: !128)
!130 = !DILocation(line: 27, column: 8, scope: !96)
!131 = !DILocation(line: 28, column: 6, scope: !132)
!132 = distinct !DILexicalBlock(scope: !128, file: !97, line: 27, column: 19)
!133 = !DILocation(line: 28, column: 14, scope: !132)
!134 = !DILocation(line: 29, column: 5, scope: !132)
!135 = !DILocation(line: 33, column: 4, scope: !96)
!136 = !DILocation(line: 33, column: 12, scope: !96)
!137 = !DILocation(line: 34, column: 3, scope: !96)
!138 = !DILocation(line: 35, column: 1, scope: !96)
!139 = distinct !DISubprogram(name: "main", scope: !97, file: !97, line: 38, type: !140, scopeLine: 38, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !2)
!140 = !DISubroutineType(types: !141)
!141 = !{!19, !19, !142}
!142 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !143, size: 64)
!143 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !144, size: 64)
!144 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!145 = !DILocalVariable(name: "argc", arg: 1, scope: !139, file: !97, line: 38, type: !19)
!146 = !DILocation(line: 38, column: 15, scope: !139)
!147 = !DILocalVariable(name: "argv", arg: 2, scope: !139, file: !97, line: 38, type: !142)
!148 = !DILocation(line: 38, column: 27, scope: !139)
!149 = !DILocalVariable(name: "started", scope: !139, file: !97, line: 40, type: !101)
!150 = !DILocation(line: 40, column: 8, scope: !139)
!151 = !DILocalVariable(name: "start", scope: !139, file: !97, line: 40, type: !101)
!152 = !DILocation(line: 40, column: 17, scope: !139)
!153 = !DILocalVariable(name: "close", scope: !139, file: !97, line: 40, type: !101)
!154 = !DILocation(line: 40, column: 24, scope: !139)
!155 = !DILocalVariable(name: "heat", scope: !139, file: !97, line: 40, type: !101)
!156 = !DILocation(line: 40, column: 31, scope: !139)
!157 = !DILocalVariable(name: "error", scope: !139, file: !97, line: 40, type: !101)
!158 = !DILocation(line: 40, column: 37, scope: !139)
!159 = !DILocalVariable(name: "decision", scope: !139, file: !97, line: 41, type: !60)
!160 = !DILocation(line: 41, column: 12, scope: !139)
!161 = !DILocation(line: 43, column: 32, scope: !139)
!162 = !DILocation(line: 43, column: 39, scope: !139)
!163 = !DILocation(line: 43, column: 46, scope: !139)
!164 = !DILocation(line: 43, column: 52, scope: !139)
!165 = !DILocation(line: 43, column: 14, scope: !139)
!166 = !DILocation(line: 43, column: 12, scope: !139)
!167 = !DILocation(line: 45, column: 3, scope: !139)
