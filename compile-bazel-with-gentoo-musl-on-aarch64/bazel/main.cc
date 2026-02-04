#include "source/exe/main_common.h"

// Minimal version symbols
extern "C" const char* build_scm_revision() { return "0"; }
extern "C" const char* build_scm_status()   { return "Unknown"; }

int main(int argc, char** argv) {
    return Envoy::MainCommon::main(argc, argv);
}

