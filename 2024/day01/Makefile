################################################################################
BUILD_DIR  := build_cpp
TARGET_EXE := $(target_exe)
MAIN_SRC   := $(main_src)
CXX_FLAGS  := $(cxx_flags)

SRC_DIRS   := $${AOC_PATH}/lib/cpp
INC_DIRS   := $${AOC_PATH}/lib/cpp

SRCS       := $(MAIN_SRC) $(shell find $(SRC_DIRS) -name '*.cpp')
OBJS       := $(SRCS:%=$(BUILD_DIR)/%.o)
INC_FLAGS  := $(addprefix -I,$(INC_DIRS))
FLAGS_TXT  := $(BUILD_DIR)/flags.txt

# CXX = clang++
CXX = /opt/homebrew/Cellar/gcc/15.1.0/bin/g++-15
CXXFLAGS = \
-Wall \
-Wextra \
-Wpedantic \
-Werror \
-Wno-unused-value \
-Wno-unused-variable \
-std=c++23 \
$(CXX_FLAGS) \
$(INC_FLAGS)

################################################################################
# all: $(TARGET_EXE)
# 	@echo "TARGET_EXE=$(TARGET_EXE)"
# 	@echo "MAIN_SRC=$(MAIN_SRC)"

# @echo "Compiling $^ to executable in $(BUILD_DIR)"
$(TARGET_EXE): $(OBJS) 
	@$(CXX) $(CXXFLAGS) $^ -o $@

# @echo "Compiling $^ to object files in $(BUILD_DIR)"
$(BUILD_DIR)/%.cpp.o: %.cpp $(FLAGS_TXT)
	@mkdir -p $(dir $@)
	@$(CXX) $(CXXFLAGS) -c $< -o $@ 

$(FLAGS_TXT): flags_tmp.txt
	@if [ ! -f $(FLAGS_TXT) ]; then \
		mv flags_tmp.txt $(FLAGS_TXT); \
	elif ! cmp -s "$(FLAGS_TXT)" flags_tmp.txt; then \
		echo "Compile flags updated. Recompiling"; \
		mv flags_tmp.txt $(FLAGS_TXT); \
	else \
		rm flags_tmp.txt; \
	fi

# Create a temporary flags file
flags_tmp.txt:
	@echo "$(CXXFLAGS)" > flags_tmp.txt

# Clean up build artifacts
clean: $(BUILD_DIR)
	rm -r $(BUILD_DIR)/*

