#include <iostream>
#include <vector>
#include <string>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <fstream>
#include <filesystem>


void fill_configurations(std::vector<std::string>& configurations) {
    for (std::string l : {" -luby ", " -no-luby"}) {
        for (std::string r : {" -rnd-init ", " -no-rnd-init"}) {
            for (double gc_frac_val = 0.1; gc_frac_val < 1; gc_frac_val += 0.1) {
                auto gc_frac = " -gc-frac=" + std::to_string(gc_frac_val);
                for (int rinc_val = 2; rinc_val < 10; rinc_val += 1) {
                    auto rinc = " -rinc=" + std::to_string(rinc_val);
                    for (double step_size_val = 0.1; step_size_val < 1; step_size_val += 0.1) {
                        auto step_size = " -step-size=" + std::to_string(step_size_val);
                        for (double step_size_dec_val = 0.1; step_size_dec_val < 1; step_size_dec_val += 0.1) {
                            auto step_size_dec = " -step-size-dec=" + std::to_string(step_size_dec_val);
                            for (double min_step_size_val = 0.1; min_step_size_val < 1; min_step_size_val += 0.1) {
                                auto min_step_size = " -min-step-size=" + std::to_string(min_step_size_val);
                                for (double rnd_freq_val = 0.1; rnd_freq_val < 1; rnd_freq_val += 0.1) {
                                    auto rnd_freq = " -rnd-freq=" + std::to_string(rnd_freq_val);
                                    for (std::string ccmin_mode : {" -ccmin-mode=0", " -ccmin-mode=1", " -ccmin-mode=2"}) {
                                        for (int rfirst_val = 1; rinc_val < 1000; rinc_val += 25) {
                                            auto rfirst = " -rfirst=" + std::to_string(rfirst_val);
                                            for (std::string phase_saving : {" -phase-saving=0", " -phase-saving=1", " -phase-saving=2"}) {
                                                for (std::string pre : {" -pre", " -no-pre"}) {
                                                    for (std::string el : {" -elim", " -no-elim"}) {
                                                        for (std::string rchk : {" -rcheck", " -no-rcheck"}) {
                                                            for (double simp_gc_frac_val = 0.1; simp_gc_frac_val < 1; simp_gc_frac_val += 0.1) {
                                                                auto simp_gc_frac = " -simp-gc-frac=" + std::to_string(simp_gc_frac_val);
                                                                for (int sub_lim_val = -1; sub_lim_val < 1001; sub_lim_val += 1) {
                                                                    auto sub_lim = " -sub-lim=" + std::to_string(sub_lim_val);
                                                                    for (int cl_lim_val = -1; cl_lim_val < 21; cl_lim_val += 1) {
                                                                        auto cl_lim = " -cl-lim=" + std::to_string(cl_lim_val);
                                                                        for (int grow_val = 0; grow_val < 2; grow_val += 1) {
                                                                            auto grow = " -grow=" + std::to_string(grow_val);

                                                                            auto config = l + r + gc_frac + rinc + step_size +
                                                                                step_size_dec + min_step_size + rnd_freq + ccmin_mode +
                                                                                rnd_freq + rfirst + phase_saving + pre + el + rchk +
                                                                                simp_gc_frac + sub_lim + cl_lim + grow;
                                                                            configurations.push_back(config);
                                                                            if (configurations.size() > 25) return;//this line should be removed; it is now there only for testing purposes
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

int main(int argc, char* argv[]) {

    std::string base_cmd = argv[1]; // e.g., "./maplesat"
    std::string directory_path = argv[2];// e.g., "/media/sf_shared/"

    std::vector<std::string> configurations;//e.g.,  = {"-rfirst=10 ","-rfirst=10 -rinc=3", "-rfirst=1 -rinc=3"};

    fill_configurations(configurations);

    auto input_dir = directory_path + "input_files/";
    auto output_dir = directory_path + "output_files/";

    if (!std::filesystem::exists(directory_path)) {
        std::cerr << "directory path does not exist!" << std::endl;
        return 1;
    }

    std::vector<std::string> files;
    for (const auto& entry : std::filesystem::directory_iterator(input_dir)) {
        if (std::filesystem::is_regular_file(entry.path())) {
            files.push_back(entry.path().string());
        }
    }



    int idx = 0;
    for (auto file : files) {
        for (const auto& config : configurations) {
            idx++;
            std::string command = base_cmd + " " + config + " " + file;

            pid_t pid = fork();

            if (pid == 0) {
                // child process
                // generate a unique output filename based on the configuration
                std::string output_file = output_dir + "output_" + std::to_string(idx) + ".txt";

                std::ofstream outfile(output_file.c_str());
                if (outfile.is_open()) {
                    outfile << "id: " << idx << "\n";
                    outfile << "File: " << file << "\n";
                    outfile << "Config: " << config << "\n";
                    outfile.close();
                }
                else {
                    std::cerr << "Failed to open output file: " << output_file << std::endl;
                    exit(1);
                }

                // redirect stdout and stderr of the child process to the output file
                freopen(output_file.c_str(), "a", stdout);
                freopen(output_file.c_str(), "a", stderr);
                system(command.c_str());
                exit(0);
            }
            else if (pid < 0) {
                std::cerr << "Fork failed!" << std::endl;
                return 1;
            }
        }
    }

    for (auto file : files) {
        // wait for all child processes to finish
        for (size_t i = 0; i < configurations.size(); ++i) {
            wait(NULL);
        }
    }

    std::cout << "Done." << std::endl;

    return 0;
}

