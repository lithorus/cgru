#!/bin/bash

# Get sources folder:
pushd .. > /dev/null
src=$PWD

# Setup CGRU:
cd ../..
source setup.sh

# Get distribution variables:
cd utilities
source ./getrevision.sh $src
[ -z "${DISTRIBUTIVE}" ] && source ./distribution.sh

# Go to initial folder:
popd > /dev/null

# Process options:
options=""
sql="REQUIRED"
gui="YES"
fermer="NO"
for arg in "$@"; do
	[ $arg == "--nosql" ] && sql="NO" && shift
	[ $arg == "--nogui" ] && gui="NO" && shift
	[ $arg == "--fermer" ] && fermer="YES" && shift
	[ $arg == "--debug" ] && debug=" -g" && shift
done

# Configure SQL:
export AF_POSTGRESQL=$sql

# Configure GUI:
export AF_GUI=$gui
export AF_FERMER=$fermer
export AF_QT_VER="5"

# Configure building
export AF_ADD_CFLAGS="-Waddress -Wbool-compare -Wbool-operation -Wcatch-value -Wformat -Wformat-overflow -Wformat-truncation -Wint-in-bool-context -Winit-self -Wlogical-not-parentheses -Wmaybe-uninitialized -Wmemset-elt-size -Wmemset-transposed-args -Wmisleading-indentation -Wmismatched-dealloc -Wmismatched-new-delete -Wmissing-attributes -Wnarrowing -Wpessimizing-move -Wrange-loop-construct -Wrestrict -Wreturn-type -Wsequence-point -Wsizeof-array-div -Wsizeof-pointer-div -Wsizeof-pointer-memaccess -Wstrict-aliasing -Wstrict-overflow=1 -Wswitch -Wtautological-compare -Wtrigraphs -Wuninitialized -Wunknown-pragmas -Wunused-function -Wvolatile-register-var -Wzero-length-bounds -Wcast-function-type -Wempty-body -Wenum-conversion -Wmissing-field-initializers -Wstring-compare -Wredundant-move -Wtype-limits -Wuninitialized -Warith-conversion -Wdangling-else -Wenum-compare -Winline"
export AF_ADD_CFLAGS="${AF_ADD_CFLAGS} -Wignored-qualifiers"
#export AF_ADD_CFLAGS="${AF_ADD_CFLAGS} -Wconversion"
export AF_ADD_CFLAGS="${AF_ADD_CFLAGS}${debug}"
export AF_ADD_LFLAGS="-lutil"
export AF_EXTRA_LIBS=""

echo "Building on '${DISTRIBUTIVE}'"
case ${DISTRIBUTIVE} in
    openSUSE)
        export AF_ADD_LFLAGS="$AF_ADD_LFLAGS -lpthread"
        ;;
    SUSE)
        export AF_ADD_LFLAGS="$AF_ADD_LFLAGS -lpthread -ldl"
        ;;
    Debian|Astra)
        export ADD_CMAKE_MODULE_PATH="$PWD"
        export AF_EXTRA_LIBS="pthread"
        ;;
    Gentoo)
	export AF_EXTRA_LIBS="pthread"
        ;;
    Ubuntu)
        export ADD_CMAKE_MODULE_PATH="$PWD"
        export AF_EXTRA_LIBS="pthread"
        ;;
    Mint)
        export ADD_CMAKE_MODULE_PATH="$PWD"
        export AF_EXTRA_LIBS="pthread"
        ;;
    Fedora)
        export AF_ADD_LFLAGS="$AF_ADD_LFLAGS -lpthread"
        ;;
    AltLinux)
        export ADD_CMAKE_MODULE_PATH="$PWD"
        export AF_EXTRA_LIBS="pthread"
        ;;
    CentOS)
        export ADD_CMAKE_MODULE_PATH="$PWD"
        export AF_EXTRA_LIBS="pthread"
		if [[ "$DISTRIBUTIVE_VERSION" < "7" ]]; then
			export AF_QT_VER="4"
		else
			export AF_ADD_CFLAGS="$AF_ADD_CFLAGS -std=c++11"
		fi
        ;;
    RedHat|Rocky)
        export AF_ADD_LFLAGS="$AF_ADD_LFLAGS -lpthread -ldl"
        ;;
    Mageia|ROSA)
        export AF_EXTRA_LIBS="pthread"
        ;;
    Arch|Manjaro)
        export AF_EXTRA_LIBS="pthread"
        ;;
    MacOSX)
        export AF_QT_VER="5"
        ;;
    *)
        echo "Warning: Untested system: '${DISTRIBUTIVE}'"
        ;;
esac

# Build:
cmake . && make $@
