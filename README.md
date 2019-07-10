# SystemVerilog-Specific-Parser
This is a parser to SystemVerilog syntax , it's intended to parse data declarations and constraints , then convert them to a specific format which is suitable for our solver tool .A GUI-based parser and solver The parsing process starts from a modified subset of regular expressions and grammar rules that describe SystemVerilog syntax, then I use PyPEG (a parse tree generator) to generate the parse tree of the input SystemVerilog syntax. I use a modified subset of SystemVerilog grammar rules as I'm interested only in the data declaration and constraints parts in SystemVerilog. 

# GUI 
![](https://github.com/bit-zone/SystemVerilog-Specific-Parser/blob/master/GUI%20snapshot.png)


