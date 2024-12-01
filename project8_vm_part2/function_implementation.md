## Bootstrap code
- normmal procedure :
    1. The program set `SP` to 256 and call `Sys.init` (takes no arguments)
    2. In `Sys.init` (which initiate the OS) the program call for a `Main.main` function that is the entry point of our program
- Implementation :
    - If only one VM file is given to the translator : only translate this VM file
    - If a directory is passed : get all the files ending by `.vm`
        - If there is a `Sys.vm` file : translate it first

## Implemetation
- Pb = when a function is called several times (undefined) how to know where should it return ?

ex : the `FibonacciElement` 
- In `Sys.vm`, the function `Sys.init` calls `Main.fibonacci` > should create a label `Sys.init$ret.1` on which `Main.fibonacci` should return when done
- In `Main.vm`, the function `Main.fibonacci` calls itself recursively > pb solved we just need `Main.fibonnaci$ret.i` labels and conditionnal branching
