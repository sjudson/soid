# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.22

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /usr/src/soid/deps/klee

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /usr/src/soid/deps/klee/build

# Include any dependencies generated for this target.
include lib/Basic/CMakeFiles/kleeBasic.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include lib/Basic/CMakeFiles/kleeBasic.dir/compiler_depend.make

# Include the progress variables for this target.
include lib/Basic/CMakeFiles/kleeBasic.dir/progress.make

# Include the compile flags for this target's objects.
include lib/Basic/CMakeFiles/kleeBasic.dir/flags.make

lib/Basic/CMakeFiles/kleeBasic.dir/KTest.cpp.o: lib/Basic/CMakeFiles/kleeBasic.dir/flags.make
lib/Basic/CMakeFiles/kleeBasic.dir/KTest.cpp.o: ../lib/Basic/KTest.cpp
lib/Basic/CMakeFiles/kleeBasic.dir/KTest.cpp.o: lib/Basic/CMakeFiles/kleeBasic.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/usr/src/soid/deps/klee/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object lib/Basic/CMakeFiles/kleeBasic.dir/KTest.cpp.o"
	cd /usr/src/soid/deps/klee/build/lib/Basic && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT lib/Basic/CMakeFiles/kleeBasic.dir/KTest.cpp.o -MF CMakeFiles/kleeBasic.dir/KTest.cpp.o.d -o CMakeFiles/kleeBasic.dir/KTest.cpp.o -c /usr/src/soid/deps/klee/lib/Basic/KTest.cpp

lib/Basic/CMakeFiles/kleeBasic.dir/KTest.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/kleeBasic.dir/KTest.cpp.i"
	cd /usr/src/soid/deps/klee/build/lib/Basic && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /usr/src/soid/deps/klee/lib/Basic/KTest.cpp > CMakeFiles/kleeBasic.dir/KTest.cpp.i

lib/Basic/CMakeFiles/kleeBasic.dir/KTest.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/kleeBasic.dir/KTest.cpp.s"
	cd /usr/src/soid/deps/klee/build/lib/Basic && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /usr/src/soid/deps/klee/lib/Basic/KTest.cpp -o CMakeFiles/kleeBasic.dir/KTest.cpp.s

lib/Basic/CMakeFiles/kleeBasic.dir/Statistics.cpp.o: lib/Basic/CMakeFiles/kleeBasic.dir/flags.make
lib/Basic/CMakeFiles/kleeBasic.dir/Statistics.cpp.o: ../lib/Basic/Statistics.cpp
lib/Basic/CMakeFiles/kleeBasic.dir/Statistics.cpp.o: lib/Basic/CMakeFiles/kleeBasic.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/usr/src/soid/deps/klee/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object lib/Basic/CMakeFiles/kleeBasic.dir/Statistics.cpp.o"
	cd /usr/src/soid/deps/klee/build/lib/Basic && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT lib/Basic/CMakeFiles/kleeBasic.dir/Statistics.cpp.o -MF CMakeFiles/kleeBasic.dir/Statistics.cpp.o.d -o CMakeFiles/kleeBasic.dir/Statistics.cpp.o -c /usr/src/soid/deps/klee/lib/Basic/Statistics.cpp

lib/Basic/CMakeFiles/kleeBasic.dir/Statistics.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/kleeBasic.dir/Statistics.cpp.i"
	cd /usr/src/soid/deps/klee/build/lib/Basic && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /usr/src/soid/deps/klee/lib/Basic/Statistics.cpp > CMakeFiles/kleeBasic.dir/Statistics.cpp.i

lib/Basic/CMakeFiles/kleeBasic.dir/Statistics.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/kleeBasic.dir/Statistics.cpp.s"
	cd /usr/src/soid/deps/klee/build/lib/Basic && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /usr/src/soid/deps/klee/lib/Basic/Statistics.cpp -o CMakeFiles/kleeBasic.dir/Statistics.cpp.s

# Object files for target kleeBasic
kleeBasic_OBJECTS = \
"CMakeFiles/kleeBasic.dir/KTest.cpp.o" \
"CMakeFiles/kleeBasic.dir/Statistics.cpp.o"

# External object files for target kleeBasic
kleeBasic_EXTERNAL_OBJECTS =

lib/libkleeBasic.a: lib/Basic/CMakeFiles/kleeBasic.dir/KTest.cpp.o
lib/libkleeBasic.a: lib/Basic/CMakeFiles/kleeBasic.dir/Statistics.cpp.o
lib/libkleeBasic.a: lib/Basic/CMakeFiles/kleeBasic.dir/build.make
lib/libkleeBasic.a: lib/Basic/CMakeFiles/kleeBasic.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/usr/src/soid/deps/klee/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Linking CXX static library ../libkleeBasic.a"
	cd /usr/src/soid/deps/klee/build/lib/Basic && $(CMAKE_COMMAND) -P CMakeFiles/kleeBasic.dir/cmake_clean_target.cmake
	cd /usr/src/soid/deps/klee/build/lib/Basic && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/kleeBasic.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
lib/Basic/CMakeFiles/kleeBasic.dir/build: lib/libkleeBasic.a
.PHONY : lib/Basic/CMakeFiles/kleeBasic.dir/build

lib/Basic/CMakeFiles/kleeBasic.dir/clean:
	cd /usr/src/soid/deps/klee/build/lib/Basic && $(CMAKE_COMMAND) -P CMakeFiles/kleeBasic.dir/cmake_clean.cmake
.PHONY : lib/Basic/CMakeFiles/kleeBasic.dir/clean

lib/Basic/CMakeFiles/kleeBasic.dir/depend:
	cd /usr/src/soid/deps/klee/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /usr/src/soid/deps/klee /usr/src/soid/deps/klee/lib/Basic /usr/src/soid/deps/klee/build /usr/src/soid/deps/klee/build/lib/Basic /usr/src/soid/deps/klee/build/lib/Basic/CMakeFiles/kleeBasic.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : lib/Basic/CMakeFiles/kleeBasic.dir/depend

