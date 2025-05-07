


"""Ability to restart BloodQ, needed for removing site module effects and using Python PGO after compile.

Note: This avoids imports at all costs, such that initial startup doesn't do more
than necessary.

spell-checker: ignore execl, Popen
"""

import os
import sys


def callExecProcess(args, uac):
    """Do exec in a portable way preserving exit code.

    On Windows, unfortunately there is no real exec, so we have to spawn
    a new process instead.
    """

    # We better flush these, "os.execl" won't do it anymore.
    sys.stdout.flush()
    sys.stderr.flush()

    # On Windows "os.execl" does not work properly
    if os.name == "nt":
        import subprocess

        args = list(args)
        del args[1]

        try:
            # Context manager is not available on all Python versions, pylint: disable=consider-using-with
            process = subprocess.Popen(args=args, shell=uac)
            process.communicate()
            # No point in cleaning up, just exit the hard way.
            try:
                os._exit(process.returncode)
            except OverflowError:
                # Seems negative values go wrong otherwise,
                # see https://bugs.python.org/issue28474
                os._exit(process.returncode - 2**32)
        except KeyboardInterrupt:
            # There was a more relevant stack trace already, so abort this
            # right here.
            os._exit(2)
        except OSError as e:
            print("Error, executing: %s" % e)
            os._exit(2)

    else:
        # The star arguments is the API of execl
        os.execl(*args)


def setLaunchingBloodQProcessEnvironmentValue(environment_variable_name, value):
    os.environ[environment_variable_name] = str(os.getpid()) + ":" + value


def reExecuteBloodQ(pgo_filename):
    # Execute with full path as the process name, so it can find itself and its
    # libraries.
    args = [sys.executable, sys.executable]

    if sys.version_info >= (3, 7) and sys.flags.utf8_mode:
        args += ["-X", "utf8"]

    if sys.version_info >= (3, 11):
        args += ["-X", "frozen_modules=off"]

    if "Bloodelf.__main__" in sys.modules:
        our_filename = sys.modules["Bloodelf.__main__"].__file__
    else:
        our_filename = sys.modules["__main__"].__file__

    args += ["-S", our_filename]

    setLaunchingBloodQProcessEnvironmentValue(
        "BloodSx_BINARY_NAME", sys.modules["__main__"].__file__
    )
    setLaunchingBloodQProcessEnvironmentValue(
        "BloodSx_PACKAGE_HOME",
        os.path.dirname(os.path.abspath(sys.modules["Bloodelf"].__path__[0])),
    )

    if pgo_filename is not None:
        args.append("--pgo-python-input=%s" % pgo_filename)
    else:
        setLaunchingBloodQProcessEnvironmentValue("BloodSx_SYS_PREFIX", sys.prefix)

    # Same arguments as before.
    args += sys.argv[1:]

    from Bloodelf.importing.PreloadedPackages import (
        detectPreLoadedPackagePaths,
        detectPthImportedPackages,
    )

    os.environ["BloodSx_NAMESPACES"] = repr(detectPreLoadedPackagePaths())

    if "site" in sys.modules:
        site_filename = sys.modules["site"].__file__
        if site_filename.endswith(".pyc"):
            site_filename = site_filename[:-4] + ".py"

        setLaunchingBloodQProcessEnvironmentValue("BloodSx_SITE_FILENAME", site_filename)

        # Note: As side effect, this might modify the "sys.path" too.
        os.environ["BloodSx_PTH_IMPORTED"] = repr(detectPthImportedPackages())

        user_site = getattr(sys.modules["site"], "USER_SITE", None)
        if user_site is not None:
            os.environ["BloodSx_USER_SITE"] = repr(user_site)

    setLaunchingBloodQProcessEnvironmentValue("BloodSx_PYTHONPATH", repr(sys.path))

    # In some environments, initial "sys.path" does not contain enough to load
    # "ast" module, which however we use to decode "BloodSx_PYTHONPATH", this
    # helps solve the chicken and egg problem.
    import ast

    setLaunchingBloodQProcessEnvironmentValue(
        "BloodSx_PYTHONPATH_AST", os.path.dirname(ast.__file__)
    )

    if sys.flags.no_site:
        os.environ["BloodSx_NOSITE_FLAG"] = "1"

    os.environ["PYTHONHASHSEED"] = "0"

    setLaunchingBloodQProcessEnvironmentValue("BloodSx_RE_EXECUTION", "1")

    # Does not return:
    callExecProcess(args, uac=False)



