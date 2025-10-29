# GitHub Issues to Create

This file contains suggested issues to create on GitHub to attract contributors and guide development.

## 🚀 Feature Requests (Good for New Contributors)

### Issue: Add Z80 CPU Support
**Title:** `feat: Add Z80 CPU support`

**Description:**
```markdown
## Feature Request: Z80 CPU Support

The assembler currently supports 65C02, 6800, and 8086. Adding Z80 support would expand its capabilities significantly.

### Implementation Details
- Create `compiler/cpu_profiles/z80/` directory
- Implement `z80_profile.py` with Z80-specific logic
- Create `opcodes_z80.py` with complete Z80 instruction set
- Add Z80 to `SUPPORTED_CPUS` in `main.py`
- Create comprehensive tests

### Resources
- [Z80 Instruction Set Reference](https://www.zilog.com/docs/z80/z80cpu_um.pdf)
- Look at existing CPU profiles for implementation patterns
- The `assembler.md` documentation has detailed instructions

### Difficulty: Medium
### Estimated Time: 2-3 weeks
### Skills: Python, Assembly Language, CPU Architecture

This is a great first contribution as it follows established patterns!
```

### Issue: ARM Cortex-M Support
**Title:** `feat: Add ARM Cortex-M CPU support`

**Description:**
```markdown
## Feature Request: ARM Cortex-M Support

Add support for ARM Cortex-M microcontrollers, starting with Cortex-M0+.

### Scope
- Thumb-2 instruction subset
- Basic ARM assembly directives
- Memory-mapped I/O support

### Why This Matters
ARM Cortex-M processors power billions of devices worldwide. This would make the assembler useful for modern embedded development.

### Difficulty: Hard
### Skills: ARM Assembly, Embedded Systems
```

### Issue: Macro System Implementation
**Title:** `feat: Implement assembly macro system`

**Description:**
```markdown
## Feature Request: Assembly Macros

Implement a macro system to reduce code duplication and improve maintainability.

### Requirements
- Define macros with parameters
- Macro expansion during assembly
- Nested macro support
- Error reporting for macro issues

### Example Usage
```assembly
.MACRO PUSH_REGS reg1, reg2
    PHA
    TXA
    PHA
    TYA
    PHA
.ENDM

; Usage
PUSH_REGS A, X
```

### Difficulty: Medium-High
### Skills: Parser Extensions, Symbol Table Management
```

### Issue: Conditional Assembly
**Title:** `feat: Add conditional assembly directives`

**Description:**
```markdown
## Feature Request: Conditional Assembly

Add IF/ELSE/ENDIF directives for conditional compilation.

### Requirements
- `IFDEF` / `IFNDEF` for symbol checking
- `IF` with expressions
- Nested conditionals
- Proper error handling

### Use Cases
- Platform-specific code
- Debug vs release builds
- Feature toggles

### Difficulty: Medium
### Skills: Parser Extensions, Expression Evaluation
```

## 🐛 Bug Fixes (Good for Quick Wins)

### Issue: Improve Error Messages
**Title:** `enhancement: Improve error message clarity and suggestions`

**Description:**
```markdown
## Enhancement: Better Error Messages

The assembler provides good error detection but could give more helpful suggestions.

### Current Issues
- Some error messages are technical rather than user-friendly
- Missing suggestions for common mistakes
- Could provide "did you mean?" hints

### Examples to Improve
- Unknown instruction suggestions
- Addressing mode hints
- Label naming conventions

### Difficulty: Easy
### Skills: Error Handling, User Experience
```

### Issue: Performance Optimization
**Title:** `perf: Optimize assembly performance for large files`

**Description:**
```markdown
## Performance: Optimize for Large Assembly Files

Current implementation is fine for small programs but could be optimized for larger projects.

### Areas to Optimize
- Symbol table lookups
- Expression evaluation
- Memory usage during assembly

### Benchmarking
Create performance tests and measure improvements.

### Difficulty: Medium
### Skills: Algorithm Optimization, Profiling
```

## 📚 Documentation & Testing

### Issue: Add More Examples
**Title:** `docs: Add comprehensive assembly examples`

**Description:**
```markdown
## Documentation: More Assembly Examples

The `examples/` directory has basic programs. Add more comprehensive examples.

### Suggested Examples
- Complete programs for each CPU
- Library routines
- Common algorithms
- Hardware interfacing

### Difficulty: Easy
### Skills: Assembly Programming
```

### Issue: Web Interface
**Title:** `feat: Add web-based interface`

**Description:**
```markdown
## Feature Request: Web Interface

Create a web-based interface for the assembler using WebAssembly or similar.

### Implementation Ideas
- Compile Python to WebAssembly
- REST API with web frontend
- Online assembler tool

### Difficulty: Hard
### Skills: Web Development, WebAssembly
```

## 🎯 Good First Issues

### Issue: Code Cleanup
**Title:** `chore: Code cleanup and consistency improvements`

**Description:**
```markdown
## Code Quality: Cleanup and Consistency

Improve code quality, consistency, and maintainability.

### Tasks
- Consistent docstring formatting
- Remove unused imports
- Standardize variable naming
- Add missing type hints
- Improve comments

### Difficulty: Easy
### Skills: Code Review, Python Best Practices
```

### Issue: Test Coverage
**Title:** `test: Improve test coverage`

**Description:**
```markdown
## Testing: Increase Test Coverage

Add tests for uncovered code paths and edge cases.

### Focus Areas
- Error conditions
- Edge cases in expression parsing
- CPU-specific validation
- Integration tests

### Difficulty: Easy-Medium
### Skills: Unit Testing, Python
```

## 📋 Issue Creation Instructions

1. Go to the Issues tab on GitHub
2. Click "New Issue"
3. Copy the title and description from above
4. Add appropriate labels:
   - `enhancement` for features
   - `bug` for bugs
   - `documentation` for docs
   - `good first issue` for beginner-friendly
   - `help wanted` for contributions needed
5. Add the CPU target as a label (e.g., `z80`, `arm`, `macro`)

## 🎉 Community Building

After creating issues, post about the project on:
- Reddit (r/programming, r/embedded, r/asm)
- Hacker News
- Twitter/LinkedIn
- Assembly language forums
- Embedded systems communities

Mention that it's a great project for learning CPU architecture and compiler design!