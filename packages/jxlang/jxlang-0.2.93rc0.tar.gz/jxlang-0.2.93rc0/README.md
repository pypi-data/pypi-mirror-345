# JxLang 0.2.6 -> 0.2.9

A lightweight custom programming language designed for simplicity and interactive scripting. Built with Python, `jxlang` provides a REPL environment and supports basic programming constructs, including variables, loops, functions, and library imports.

## Installation

Install `jxlang` via PyPI:

```bash
pip install jxlang
```

## Update Content
<ul>
<li>Optimized string definition.</li>
<li>Support adding, deleting and modifying elements in the list.</li>
<li>Solved some known underlying logic problems.</li>
<li>Preparing for supporting '.jl' code documents, pre support one-time running of written code.</li>
</ul>

## Features

- **Single-Line Comments**: `#` stands for single-line comments.
- **Variable Declaration**: Use `let` to declare variables.
- **Loops**: `for` loops with range-based iteration.
- **I/O Operations**: `enter()` for input, `say()` for output.
- **Library Imports**: Import Python libraries via `cite`.
- **List/Table Structures**: Create lists (`table(...)`).
- **Exit Session**: `endend()` for exiting current session.
- **REPL Support**: Interactive shell for quick testing.

## Quick Examples

### 1. Variable Declaration and Printing
```python
let x: 5
say(x + 3)  # Output: 8
# You can use double quotation marks or single quotation marks when assigning strings to variable names
let a: "hello"
say(a)      # hello
let a: 'hello'
say(a)      # hello
```

### 2. Loop
```python
(i -> 1 && 5).for(say(i))
# Output: 1 2 3 4 5
```

### 3. Function Definition (Not open for users now)


### 4. Input and Output
```python
let name: enter()  # User enters "Alice"
say("Hello, " + name)  # Output: Hello, Alice
```

### 5. Import a Python Library
```python
cite math
say(math.sqrt(25))  # Output: 5.0
cite numpy
let a: numpy.array([1,2,3])
say(a)              # Output: [1,2,3]
```
<p>* JxLang can calls Python Libraries only if you installed in your python environment.</p>

### 6. List and Table
```python
let lst: table(1, 2, 3)
say(lst[0])       # Output: 1
say(lst)          # Output: [1,2,3]
let tbl = table(1, 2; 3, 4)
say(tbl)          # Output: [[1, 2], [3, 4]]
push 1 -> lst     # Add 1 to the bottom of the list
say(lst)          # [1,2,3,1]
push tbl -> lst
say(lst)          # [1,2,3,1,[[1,2],[3,4]]]
out 1 -> lst      # Remove 1 from the list but leave it in memory
say(lst)          # [2,3,[[1,2],[3,4]]]
# Outlist can display the deleted list elements
say(lst.outlist)  # [1,1]
throw 2 -> lst    # Deleting 2 from the list cannot be restored
say(lst)          # [3,[[1,2],[3,4]]]
let lst[0]: 2     # Replace the element with index 0 in the list with 2
say(lst)          # [2,[[1,2],[3,4]]]
```
<p>* JxLang splits into n-plus-1-dimensional lists by n semicolons.</p>

## Using the REPL

Start the interactive environment by running:
```bash
jxlang
```

Example REPL session:
```
jxlang> say(42)
42
jxlang> endend(0)  # you can use numbers from 0 to 9 for endend()
Exiting with code 0
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.  
For major changes, open an issue first to discuss your ideas.

## License

This project is licensed under the Apache License.

---

Happy coding! 🚀