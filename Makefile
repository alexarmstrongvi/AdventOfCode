TARGET_EXE := $(target_exe)
MAIN_SRC   := $(main_src)

BUILD_DIR := ./build
SRC_DIRS  := $${AOC_PATH}/src
INC_DIRS  := $${AOC_PATH}/include

SRCS := $(MAIN_SRC) $(shell find $(SRC_DIRS) -name '*.c')
# OBJS := $(shell echo $(SRCS) | sed 's:.*/src/::')
OBJS := $(SRCS:%=$(BUILD_DIR)/%.o)
INC_FLAGS := $(addprefix -I,$(INC_DIRS))

CC = clang
CFLAGS = \
-Wall \
-Wextra \
-Wpedantic \
-Werror \
-Wno-unused-comparison \
-Wno-unused-value \
-Wno-unused-variable \
-std=c17 \
-g \
$(INC_FLAGS)

$(BUILD_DIR)/$(TARGET_EXE): $(OBJS)
	@echo "Compiling $@ to $(BUILD_DIR)"
	@$(CC) $(CFLAGS) $(OBJS) -o $@

$(BUILD_DIR)/%.c.o: %.c
	@echo "Compiling object files to $(BUILD_DIR)"
	@mkdir -p $(dir $@)
	@$(CC) $(CFLAGS) -c $< -o $@ 

clean: $(BUILD_DIR)
	rm -r $(BUILD_DIR)/*

