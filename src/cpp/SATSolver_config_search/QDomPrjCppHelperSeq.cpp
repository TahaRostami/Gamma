#include <iostream>
#include <vector>
#include <string>
#include <cstdlib>

int main() {

    std::vector<std::string> files = { "/media/sf_shaed/qdom_10_5_theorem_row_col_naive.cnf" };
    std::vector<std::string> configurations = {"-rfirst=10 ","-rfirst=10 -rinc=3"};

    // For each file, loop through each configuration and execute the command-line application in the background
    for (auto file : files)
    {
        for (const auto& config : configurations) {
            std::string command = "./maplesat " + config + " " + file;
            system((command + " &").c_str());
        }
    }
    std::cout << "Executed all configurations." << std::endl;

    return 0;
}