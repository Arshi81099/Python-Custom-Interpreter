# Python-Custom-Interpreter

## Overview

This project is a basic interpreter written in Python. It supports tokenization, parsing, and execution of simple expressions and statements. The interpreter can handle variable declarations, assignments, arithmetic operations, comparisons, and printing values.

## Features

- **Tokenization:** Converts source code into tokens.
- **Parsing:** Parses tokens to generate an Abstract Syntax Tree (AST).
- **Evaluation:** Evaluates the AST and executes the statements.
- **Command-Line Interface (CLI):** Supports commands for tokenization, parsing, evaluation, and execution.

## Code Structure

The project consists of a single file:

- **`main.py`:** Main script to run the interpreter. It includes:
  - **Scanner:** Tokenizes the input source code.
  - **Parser:** Parses tokens and generates an Abstract Syntax Tree (AST).
  - **Interpreter:** Evaluates the AST and executes the statements.

## Usage

To use the interpreter, run the script with one of the following commands:

1. **Tokenize:** Print tokens from the source file.

    ```bash
    python main.py tokenize <filename>
    ```

2. **Parse:** Parse the source file and print the Abstract Syntax Tree.

    ```bash
    python main.py parse <filename>
    ```

3. **Evaluate:** Evaluate the expression from the source file and print the result.

    ```bash
    python main.py evaluate <filename>
    ```

4. **Run:** Parse and execute the statements from the source file.

    ```bash
    python main.py run <filename>
    ```

## Examples

Given a source file `example.txt` with the following content:

```text
var x = 10;
print x;
