# NOTE: only required for python3.7
brew install openblas
brew install llvm@11
echo 'setting env var now, but consider adding to path: export OPENBLAS="$(brew --prefix openblas)"'
export OPENBLAS="$(brew --prefix openblas)"
pip uninstall -y numpy
pip install cython==0.29.33 bind11==2.10.3 pythran==0.12.1
pip install --no-binary :all: --no-use-pep517 numpy scipy
pip install --no-use-pep517 scikit-learn
LLVM_CONFIG="/opt/homebrew/Cellar/llvm@11/11.1.0_4/bin/llvm-config" pip install llvmlite