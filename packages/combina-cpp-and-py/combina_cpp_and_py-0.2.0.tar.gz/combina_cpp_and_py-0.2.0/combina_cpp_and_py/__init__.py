#if false
r"""
#endif

#include <string>
#include <iostream>

std::string combine(std::string cpp_code, std::string py_code, bool use_double=true) {
	if (cpp_code.find("\'\'\'") || cpp_code.find("\"\"\"")) std::cerr << "SyntaxWarning: the code may be wrong due to the \'\'\' or \"\"\" in cpp_code" << std::endl;
	if (py_code.find("#endif")) std::cerr << "SyntaxWarning: the code may be wrong due to \'#endif\' in py_code" << std::endl;
	if (use_double) return "#if false\nr\"\"\"\n#endif\n" + cpp_code + "\n#if false\n\"\"\"\n" + py_code + "\n#endif";
	return "#if false\nr\'\'\'\n#endif\n" + cpp_code + "\n#if false\n\'\'\'\n" + py_code + "\n#endif";
}

#if false
"""
from .write_cpp_combina_to_py import combina_cpp_and_py as combine
from .write_cpp_combina_to_py import main
#endif
