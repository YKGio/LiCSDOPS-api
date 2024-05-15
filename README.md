# LiCSDOPS API

## Pre-requisites
### NVIDIA CUDA (Optional)
To use local GPU acceleration, please install the following components. If you don't have a CUDA-supported GPU, you can still run it directly on the CPU, but it will take longer to compute.
1. NVIDIA GPU Driver
    Please [download](https://www.nvidia.com/Download/index.aspx?lang=en-us) and install the appropriate driver for your operating system and GPU model
3. CUDA
    Download and install. See the [version list](https://developer.nvidia.com/cuda-toolkit-archive).
    Note: The latest CUDA 12.x version is currently not working. Please download the 11.x version.
5. cuDNN
    [Download](https://developer.nvidia.com/rdp/cudnn-download). Please note the CUDA version and OS installed in the previous step. After downloading, extract the archive and copy the three folders `bin/`, `include/`, and `lib/` and the LICENSE file to the `path/to/NVIDIA GPU Computing Toolkit/CUDA/v11.x/` directory.
6. Zlib
    + Linux
    ```bash
    sudo apt-get install zlib1g
    ```
    + Windows
    [Download](http://www.winimage.com/zLibDll/zlib123dllx64.zip)  and extract it to a directory of your choice, for example,`C:\zlib\`.
7. Add the following paths to the user variable`＄Path`
    + `path/to/NVIDIA GPU Computing Toolkit/CUDA/v11.x/bin`
    + `path/to/NVIDIA GPU Computing Toolkit/CUDA/v11.x/lib/x64`
    + `path/to/zlib/dll_x64`

    You can use the following PowerShell command to add the paths. Please note to modify `path\to` to the correct installation location (the default installation location is `"C:\Program Files"`) and modify `v11.x` to the version you installed.
    ```shell
    $oldPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    $newPaths = "path\to\NVIDIA GPU Computing Toolkit\CUDA\v11.x\bin", "path\to\NVIDIA GPU Computing Toolkit\CUDA\v11.x\lib\x64", "path\to\zlib\dll_x64"
    $newPath = ($newPaths + $oldPath.Split(';')) -join ';'
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    ```

### Microsoft C++ Build Tools
Windows users please [download](https://aka.ms/vs/17/release/vs_BuildTools.exe) and install.

Once the installation is complete, Visual Studio Installer will open. Please select the latest version of MSVC Build Tools and Windows SDK from the Individual Components page.

Please note that you need to select the installation based on your CPU architecture and Windows version. For example, Intel CPU Windows 11 users who installed in March 2023 should select the following components:

+ MSVC v143 - VS 2022 C++ x64/x86 Build Tools (latest)
+ Windows 11 SDK (10.0.22621.0)


### Python
Currently testing version 3.8.10. Versions that are too high or too low may not work.

## Installation
1. Clone the repo
    ```shell
    git clone https://github.com/NTHU-DLab-Cough-Team/LiCSDOPS-api.git
    ```

2. Python requirements
    ```shell
    cd LiCSDOPS-api
    pip install -r ./requirements.txt
    ```

6. Please download the model files from [here](https://drive.google.com/file/d/1Rz44H1ffns2a2FfRBWwuOVuy6viDXqz1/view?usp=sharing)  and extract them to the `path/to/LiCSDOPS-api/` directory. Please note to modify path/to to the installation location.

## Local Testing
1. Start local server
    ```shell
    invoke rundev
    ```
