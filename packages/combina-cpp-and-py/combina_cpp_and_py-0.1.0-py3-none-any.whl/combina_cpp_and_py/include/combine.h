#if false
r"""
#endif

#include <string>

std::string combine(std::string cpp_code, std::string py_code, bool use_double=true) {
	if (use_double) return "#if false\nr\"\"\"\n#endif\n" + cpp_code + "\n#if false\n\"\"\"\n" + py_code + "\n#endif";
	return "#if false\nr\'\'\'\n#endif\n" + cpp_code + "\n#if false\n\'\'\'\n" + py_code + "\n#endif";
}

#if false
"""
from .write_cpp_combina_to_py import combina_cpp_and_py as combine
from .write_cpp_combina_to_py import main
#endif