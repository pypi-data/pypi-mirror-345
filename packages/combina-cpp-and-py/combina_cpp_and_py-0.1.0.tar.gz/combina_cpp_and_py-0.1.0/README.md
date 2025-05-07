# Combina c++ code and python code

<pre>
You can use this project to combine c++ code and python code in one file.
</pre>

## How to use

### 1. Install

```
pip install combina_cpp_and_py
```

### 2. Use

<pre>
Hypothesis that you have a cpp file named "test.cpp" and a python file named "test.py".
</pre>

```
import combina_cpp_and_py
with open('test.cpp', 'r') as f:
    cpp_code = f.read()
with open('test.py', 'r') as f:
    py_code = f.read()
new_code = combina_cpp_and_py.combine(cpp_code, py_code)
with open('result.cpp', 'w') as f:
    f.write(new_code)
with open('result.py', 'w') as f:
    f.write(py_code)
```



### 3. Result

<pre>
You will get a new cpp file named "result.cpp" and "result.py" which contains the combined c++ code and python code.
</pre>

```
#if false
r"""
#endif
{$cppcode}
#if false
"""
{$pythoncode}
#endif
```

## Explain

<pre>
The code will be combined in the following way:
1. The c++ code will be placed in the {$cppcode} block.
2. The python code will be placed in the {$pythoncode} block.
3. When run c++, the {$pythoncode} block will be ignored due to "#if false" and "#endif".
4. When run python, the {$cppcode} block will be ignored due to "#" and " r"""""" ".
</pre>