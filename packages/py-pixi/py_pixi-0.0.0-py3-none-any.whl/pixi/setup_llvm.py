
import os
import shutil
from shutil import ignore_patterns
from .logger import setup_logger

logger = setup_logger('pixi')
here = os.path.abspath(os.path.dirname(__file__))

class SetupLLVM:
    def __init__(self, **kwargs) -> None:
        self.llvm_dir = kwargs["llvm_dir"]
        self.cores= kwargs["cores"]

    def setup(self) -> None:
        """set up the transform and other files requried to covert IR to standard yaml
        for furhter analysis
        """
        logger.info("Setting up LLVM environment...")
        
        # Build LLVM project
        self._build_llvm()
        
        logger.info(f"setting up analysis extractor mechanics in {self.llvm_dir}")
        #creating the transform directory
        os.makedirs(f"{self.llvm_dir}/llvm/lib/Transforms/pixi_extractor", exist_ok=True)
        #copying the llvm instruction extractor files
        shutil.copytree(f"{here}/constants/llvm_transform_src/",
                        f"{self.llvm_dir}/llvm/lib/Transforms/pixi_extractor/", 
                        dirs_exist_ok=True, ignore=ignore_patterns("*.py", "*md"))
        logger.info("Analysis extractor mechanics setup complete")
        logger.info("LLVM environment setup complete")
        
        #check if the instcruction extractor files is appended in cmake or we append it.
        transformer_cmake_flag = False
        with open(f"{self.llvm_dir}/llvm/lib/Transforms/CMakeLists.txt", "r") as f:
            lines = f.readlines()

        """
        [NOTE]
        The below cmake file is for the cmake outside the Transformer/ directory in the llvm
        directory.
        """

        if "pixi_extractor" in "".join(lines):
            logger.info("pixi_extractor is already in CMakeLists.txt")
            transformer_cmake_flag = True

        #apppending the instruction extractor files in cmake in not present
        if not transformer_cmake_flag:
            with open(f"{self.llvm_dir}/llvm/lib/Transforms/CMakeLists.txt", "a") as f:
                f.write("\nadd_subdirectory(pixi_extractor)\n")
            logger.info("pixi_extractor added to CMakeLists.txt")
            
    def _build_llvm(self) -> None:
        """Build the LLVM project with CMake and Ninja
        """
        import subprocess
        import sys
        from pathlib import Path
        
        logger.info("Building LLVM project...")
        
        # Create build directory if it doesn't exist
        build_dir = Path(f"{self.llvm_dir}/build")
        build_dir.mkdir(exist_ok=True)
        
        # Configure LLVM with CMake
        logger.info("Configuring LLVM with CMake...")
        cmake_cmd = [
            "cmake", 
            "-G", "Ninja", 
            "-DCMAKE_BUILD_TYPE=Debug",
            "-DLLVM_ENABLE_PROJECTS=clang",
            "../llvm"
        ]
        
        try:
            # Use subprocess.Popen to stream output in real-time
            process = subprocess.Popen(
                cmake_cmd,
                cwd=str(build_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Print output in real-time
            for line in process.stdout:
                line = line.strip()
                logger.info(f"CMake: {line}")
                
            process.wait()
            if process.returncode != 0:
                logger.error("CMake configuration failed")
                sys.exit(1)
                
            # Build LLVM with Ninja
            logger.info("Building LLVM with Ninja (this may take a while)...")
            # Determine number of CPU cores for parallel build
            num_cores = self.cores #multiprocessing.cpu_count()
            logger.info(f"Using {num_cores} CPU cores for parallel build")
            
            # Build just the tools we need instead of the entire project
            ninja_cmd = ["ninja", f"-j{num_cores}"]
            
            process = subprocess.Popen(
                ninja_cmd,
                cwd=str(build_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Print output in real-time with progress indication
            for line in process.stdout:
                line = line.strip()
                if line.startswith('[') and ']' in line:
                    # This is a build progress line
                    logger.info(f"Build: {line}")
                    
            process.wait()
            if process.returncode != 0:
                logger.error("LLVM build failed")
                sys.exit(1)
                
            logger.info("LLVM build completed successfully")
            
        except Exception as e:
            logger.error(f"Error building LLVM: {str(e)}")
            sys.exit(1)
