"""
This module contains functions for generating molcas job scripts
"""

import os
import stat
import sys
import inspect
from .extractor import read_elec_orb, read_rasscf_orb, read_completion,\
                       check_single_aniso
import hpc_suite as hpc
from hpc_suite.generate_job import parse_hostname


def gen_submission(project_name,
                   input_name=None, output_name=None, err_name=None,
                   molcas_module=None, molcas_path=None,
                   memory=None, disk=None, scratch=None, in_scratch=None,
                   hpc_args=[]):
    """
    Create submission script for a single molcas calculation.

    Parameters
    ----------
        project_name : str
            Molcas project name
        input_name : str, optional
            Name of molcas input file, default is project_name + .input
        output_name : str, optional
            Name of molcas output file, default is project_name + .out
        err_name : str, optional
            Name of molcas error file, default is project_name + .err
        molcas_module : str, default "apps/gcc/openmolcas/latest" (CSF)
            Path to molcas module for module load command
        molcas_path : str, default "/opt/OpenMolcas-21.06-hyperion" (Cerberus)
            Path to molcas executables
        memory : int, optional
            Amount of memory given to molcas in MB
        disk : int, optional
            Amount of disk given to molcas in MB
        scratch : str, optional
            Path to the scratch directory
        in_scratch : bool, optional
            Flag to indicate if Molcas is run entirely in scratch
        hpc_args : list
            List of unparsed extra arguments known to the parser of hpc_suite's
            generate_job programme

    Returns
    -------
        None
    """

    args = hpc.read_args(['generate_job'] + hpc_args)

    if args.profile == 'read_hostname':
        machine = parse_hostname()
    else:
        machine = args.profile

    supported_machines = [
        "cerberus",
        "medusa",
        "csf3",
        "csf4",
        "gadi"
    ]

    if machine not in supported_machines:
        sys.exit("Error: Unsupported machine")
    
    default_mod = {
        "cerberus": None,
        "medusa": None,
        "csf3": "chiltongroup/openmolcas/24.06",
        "csf4": "chiltongroup/openmolcas/23.02",
        "gadi": "chiltongroup/openmolcas/24.06"
    }

    default_path = {
        "cerberus": "/opt/OpenMolcas-21.06-hyperion",
        "medusa": "/opt/OpenMolcas-30jun21",
        "csf3": None,
        "csf4": None,
        "gadi": None
    }
    default_mem = {
        "cerberus": {
            None: 30000
        },
        "medusa": {
            None: 30000
        },
        "csf3": {
            None: 4000 * args.omp,
            "high_mem": 16000 * args.omp
        },
        "csf4": {
            None: 4000 * args.omp
        },
        "gadi": {
            None: 3500 * args.omp,
            "normal":3500 * args.omp,
            "normalbw":3500 * args.omp,
            "hugemem":30000 * args.omp,
            "hugemembw":36000 * args.omp,
        },
    }

    default_disk = {
        "cerberus": 20000,
        "medusa": 20000,
        "csf3": 200000,
        "csf4": 200000,
        "gadi": 200000,
    }

    default_scratch = {
        "cerberus": r"$CurrDir/scratch",
        "medusa": r"$CurrDir/scratch",
        "csf3": r"/scratch/$USER/$MOLCAS_PROJECT",
        "csf4": r"/scratch/$USER/$MOLCAS_PROJECT",
        "gadi": r"/scratch/ls80/$USER/$MOLCAS_PROJECT"
    }

    default_in_scratch = {
        "cerberus": True,
        "medusa": True,
        "csf3": False,
        "csf4": False,
        "gadi": False,
    }

    # Fetch defaults if not set explicitly
    if molcas_module is None and molcas_path is None:
        molcas_module = default_mod[machine]
        molcas_path = default_path[machine]

    # check if requested molcas version is valid
    if molcas_module is None and molcas_path is None:
        sys.exit("Error: No Molcas version specified!")
    elif molcas_module and molcas_path:
        sys.exit("Error: Ambiguous Molcas version specified!")

    memory = default_mem[machine][args.node_type] \
        if memory is None else memory
    disk = default_disk[machine] if disk is None else disk
    scratch = default_scratch[machine] if scratch is None else scratch
    in_scratch = default_in_scratch[machine] \
        if in_scratch is None else in_scratch

    # Set environmental variables

    if molcas_path:  # add MOLCAS variable to env
        args.env_vars['MOLCAS'] = molcas_path

    args.env_vars["MOLCAS_PROJECT"] = project_name
    args.env_vars["MOLCAS_MEM"] = str(memory)
    args.env_vars["MOLCAS_DISK"] = str(disk)
    args.env_vars["MOLCAS_PRINT"] = str(2)
    args.env_vars["MOLCAS_MOLDEN"] = "ON"
    args.env_vars["CurrDir"] = r"$(pwd -P)"
    args.env_vars["WorkDir"] = scratch

    # Set molcas module
    if molcas_module:
        args.modules.append(molcas_module)

    # Set job, input, output and error names
    args.job_name = project_name if args.job_name is None else args.job_name
    input_name = '$MOLCAS_PROJECT.input' if input_name is None else input_name
    output_name = '$MOLCAS_PROJECT.out' if output_name is None else output_name
    err_name = '$MOLCAS_PROJECT.err' if err_name is None else err_name

    if in_scratch:
        input_name = '/'.join(["$CurrDir", input_name])
        output_name = '/'.join(["$CurrDir", output_name])
        err_name = '/'.join(["$CurrDir", err_name])

    # Define call to pymolcas
    pymolcas_args = "{} 2>> {} 1>> {}".format(
        input_name, err_name, output_name
    )

    body_mkdir = "mkdir -p $WorkDir"
    body_cd = "cd $WorkDir" if in_scratch else ""

    # Define Body
    body = ("if [ -f $MOLCAS/bin/pymolcas ]; then\n"
            "    $MOLCAS/bin/pymolcas {pymolcas_args}\n"
            "elif [ -f $MOLCAS/pymolcas ]; then\n"
            "    $MOLCAS/pymolcas {pymolcas_args}\n"
            "elif [ -f $MOLCAS/Tools/pymolcas/pymolcas_ ]; then\n"
            "    $MOLCAS/Tools/pymolcas/pymolcas_ {pymolcas_args}\n"
            "else\n"
            '    echo "Warning: Using system-wide pymolcas installation!"\n'
            "    pymolcas {pymolcas_args}\n"
            "fi\n").format(pymolcas_args=pymolcas_args)

    args.body = '\n'.join([body_mkdir, body_cd, body])
    # Generate job submission script
    hpc.generate_job_func(args)


def gen_submission_csf_array(input_name, output_name, n_jobs, orbital,
                             dir_list_file='dir_list.txt',
                             remove_output=True, extractor='',
                             submit_file="submit.sh",
                             molcas_module="apps/gcc/openmolcas/latest",
                             job_name="", project_name="", memory=4000,
                             disk=20000, extra=[], verbose=True):
    """
    Create submission script for a job array of molcas calculations using
    the Computational Shared Facility (CSF). The user must supply a file
    containing the directory of each individual calculation (dir_list_file).
    This script assumes that each molcas input/output file has the same name,
    e.g. Dy.in, as given by the input(output)_name variable.
    Each calculation will be run entirely in scratch. The user must provide
    an extractor command to extract the data they require from the .output
    file, which is (by default) deleted if the calculation is successful.


    Parameters
    ----------
        input_name : str
            Name of molcas input file
        output_name : str
            Name of molcas output file
        n_jobs: int
            Number of jobs in the job array
        orbital: str {"3d", "4f"}
            Orbitals used to define active space purity when checking for
            successful calculation
        dir_list_file : str, default "dir_list.txt"
            Filename containing all array folders
        remove_output : bool, default True
            If True, delete output file if calculation is successful
        extractor : str, default ''
            Extractor commands to be run after molcas calculation finishes
        submit_file : str, default 'submit.sh'
            Name of submission script .sh file
        molcas_module : str, default ''
            Path to molcas module for csf module load command
        job_name : str, optional
            CSF job name, default is head of `input_name`
        project_name : str, optional
            Molcas project name, default is head of `input_name`
        memory : int, default 4000
            Amount of memory given to molcas in MB
        disk : int, default 20000
            Amount of disk given to molcas in MB
        extra : list, optional
            Extra keywords/commands to run at end of script
                n.b. These are run in the submission directory
        verbose : bool, default True
            If True, print information on jobscript to screen

    Returns
    -------
        None
    """

    input_head = os.path.splitext(input_name)[0]

    if not job_name:
        job_name = "{}".format(input_head)

    if not project_name:
        project_name = "{}".format(input_head)

    err_name = "{}.err".format(os.path.splitext(output_name)[0])

    # Check at least 1 job supplied
    assert n_jobs > 0, print("Fewer than 1 job specified, or n_jobs argument missing") # noqa

    # Make script to check molcas calculations were successful
    check_script_name = "check_molcas.py"
    _gen_check_script(check_script_name, happy_landing=True)

    jid = r"${JOB_ID}"
    stid = r"${SGE_TASK_ID}"
    subdir = r"${SUBDIR}"

    pymolcas_call = "pymolcas -clean {}/{} 2>> {}/{} 1>>{}/{}".format(
        subdir, input_name, subdir, err_name, subdir, output_name
    )

    # Make jobscript
    with open(submit_file, "w") as f:

        f.write("#!/bin/bash --login\n")
        f.write("#$ -N {}\n".format(job_name))
        f.write("#$ -cwd\n")
        f.write("#$ -V\n")
        f.write("#$ -t 1-{:d}\n\n".format(n_jobs))
        f.write("\n")
        f.write("module load {}\n".format(molcas_module))
        f.write("\n")

        f.write('SUBDIR=`sed -n "{}p" {}`\n'.format(stid, dir_list_file))
        f.write("export MOLCAS_WORKDIR=/scratch/$USER/temp_{}_{}\n".format(
            jid, stid
        ))
        f.write("mkdir -p $MOLCAS_WORKDIR\n")
        # Run molcas in scratch to avoid extra files
        f.write("cd $MOLCAS_WORKDIR\n\n")
        f.write("export MOLCAS_PROJECT={}\n".format(project_name))
        f.write("\n")

        f.write("export MOLCAS_MEM={:d}\n".format(memory))
        f.write("export MOLCAS_PRINT=2\n")
        f.write("export MOLCAS_DISK={:d}\n".format(disk))
        f.write("export MOLCAS_MOLDEN=OFF\n")
        f.write("\n")

        f.write("if [ -f $MOLCAS/bin/pymolcas ]; then\n")
        f.write("    $MOLCAS/bin/{}\n".format(pymolcas_call))
        f.write("else\n")
        f.write("    {}\n".format(pymolcas_call))
        f.write("fi\n")

        f.write("\n")

        # Move to SUBDIR (where .in and .out are stored)
        f.write("cd $SUBDIR\n")

        # Check for successful termination of molcas calculation
        f.write('python $SGE_O_WORKDIR/{} {} {} > check.txt\n'.format(
            check_script_name,
            output_name,
            orbital
            )
        )

        # Attempt to carry out extraction of properties
        f.write("\n")
        f.write(extractor)
        f.write("\n\n")

        # If job has failed, echo directory to failed list
        f.write('if grep -q "FAIL" check.txt; then\n')
        f.write(' echo $SUBDIR >> $SGE_O_WORKDIR/dir_list_failed.txt\n')
        # If successful delete .o* and .e* SGE files, and optionally .out file
        f.write("else\n")
        f.write(" rm $SGE_O_WORKDIR/{}.e{}.{}\n".format(job_name, jid, stid))
        f.write(" rm $SGE_O_WORKDIR/{}.o{}.{}\n".format(job_name, jid, stid))
        if remove_output:
            f.write(" rm {} {} check.txt\n".format(output_name, err_name))
        f.write("fi\n\n")

        # Return to submission directory in case extra args are provided
        f.write("cd $SGE_O_WORKDIR\n")

        # Additional arguments
        if extra:
            f.write("\n")
            for e in extra:
                f.write("{}\n".format(e))

        f.write("exit")

    # Make job script executable
    st = os.stat(submit_file)
    os.chmod(submit_file, st.st_mode | stat.S_IEXEC)

    if verbose:
        print('Submit this job with:\n')
        print('qsub {}\n'.format(submit_file))

    return


def gen_submission_condor(input_name, output_name, orbital,
                          molcas_module='OpenMolcas/18.09',
                          condor_script="submit_condor.txt",
                          molcas_script="condor_molcas.sh",
                          extra_input_files=[], extra_output_files=[],
                          dir_list_file='dir_list.txt', aws=False,
                          extractor='', remove_output=True, verbose=True):
    """
    Creates a set of files ready to submit to UoM's condor pool, and optionally
    burst to amazon webservices.  The user must supply a file
    containing the directory of each individual calculation (dir_list_file).
    This script assumes that each molcas input/output file has the same name,
    e.g. Dy.in, as given by the input(output)_name variable.
    The user must provide an extractor command to extract the data
    they require from the .output file, which is (by default) deleted/empty
    if the calculation is successful.

    Parameters
    ----------
        input_name : str
            Name of molcas input file
        output_name : str
            Name of molcas output file
        orbital : str
            Orbitals to check for in active space "3d" or "4f"
        molcas_module : str, default "OpenMolcas/18.09"
            Path to molcas module for condor module load command
        condor_script : str, default "submit_condor.txt"
            Name of condor submission script
        molcas_script : str, default "condor_molcas.sh"
            Name of molcas jobscript
        extra_input_files : list, optional
            Path(s) to extra input files
        extra_output_files: list, optional
            Name(s) of extra output files
        dir_list_file : str, default "dir_list.txt"
            Filename containing all array directories
        aws : bool, default False
            If True, enables condor bursting to Amazon Web Services (AWS)
        extractor : str, optional
            Extractor commands to be run after molcas calculation finishes
        remove_output : bool, default True
            If True, delete .output file if calculation is successful
        verbose : bool, default True
            If True, print information on jobscript to screen

    Returns
    -------
        None
    """

    # Generate submit_dag file
    dag_file = 'submit.dag'
    _gen_submit_dag(dag_file, condor_script, 'postprocess_condor.sh')

    # Create script to check for successful completion of molcas
    check_script_name = "check_molcas.py"
    _gen_check_script(check_script_name)

    # Generate condor submission script
    _gen_condor_subscript(condor_script, input_name, output_name,
                          check_script_name, dir_list_file, molcas_script,
                          aws=aws, extra_input_files=extra_input_files,
                          extra_output_files=extra_output_files)

    # Generate postprocessing script
    _gen_postprocess('postprocess_condor.sh')

    # Create script to run each molcas calculation in job
    _gen_molcas_shell_condor(
        molcas_script, molcas_module, aws, input_name, output_name,
        check_script_name, orbital, extractor, remove_output
    )

    if verbose:
        print('Submit this job to Condor with:\n')
        print('condor_submit_dag {}\n'.format(dag_file))

    return


def _gen_condor_subscript(condor_script, input_name, output_name,
                          check_script_name, dir_list_file, molcas_script,
                          aws=False, extra_input_files=[],
                          extra_output_files=[]):

    """
    Create condor submission script

    Parameters
    ----------
        condor_script : str
            Name of condor submission script
        input_name : str
            Name of molcas input file
        output_name : str
            Name of molcas output file
        check_script_name : str
            Name of molcas checking script from `_gen_check_script`
        dir_list_file : str
            Filename containing all array directories
        molcas_script : str
            Name of molcas jobscript
        aws : bool, default False
            If True enables condor bursting to Amazon Web Services (AWS)
        extra_input_files : list
            Path(s) of additional input files
        extra_output_files : list
            Names of additional output files

    Returns
    -------
        None
    """

    # Find absolute path of current directory
    submit_dir = os.getcwd()

    # Write condor submission script
    # This submits all of the individual jobs to condor
    with open(condor_script, "w") as f:

        f.write('Universe = vanilla\n')
        f.write("{}{}".format(
            'Requirements = ( Target.Opsys == "LINUX"',
            '&& Target.Arch == "X86_64" && HAS_OPENMOLCAS_18_09=?=True'
            )
        )
        if aws:
            f.write(
                ' && HAS_PYTHON_3_7 =?= True)'
            )
        else:
            f.write(
                ' && HAS_PYTHON_3_6 =?= True)'
            )

        f.write(' && (Target.TotalCpus =!= UNDEFINED)\n')
        f.write('Log = condor.log\n')
        f.write('Output = condor.out\n')
        f.write('Error = condor.error\n')
        f.write('Request_Disk = 20000000\n')
        f.write('Request_Memory = 16000\n')

        if aws:
            f.write('+MayUseAWS=true\n')

        f.write('Notification = Never\n')
        f.write('Should_Transfer_Files = Yes\n')
        f.write('When_To_Transfer_Output = ON_EXIT\n')

        # Molcas script file for individual calculation
        f.write('Executable = {}\n'.format(molcas_script))
        f.write('Arguments = $(initial_dir)\n')

        # Input files
        f.write('transfer_input_files = {}, {}'.format(
            input_name,
            "{}/{}".format(submit_dir, check_script_name)
            )
        )
        for extra in extra_input_files:
            f.write(', {}'.format(extra))
        f.write('\n')

        # Output files
        f.write('transfer_output_files = {}, failed.txt'.format(output_name))
        for extra in extra_output_files:
            f.write(', {}'.format(extra))
        f.write('\n')
        output_remap = 'failed.txt=$(initial_dir)/failed.txt.$(Process)'
        f.write('transfer_output_remaps = "{}"\n'.format(output_remap))

        f.write('Transfer_Executable = True\n')
        # set initial_dir variable
        f.write('Queue initial_dir from {}\n'.format(dir_list_file))

    return


def _gen_molcas_shell_condor(script_name, molcas_module, aws,
                             input_name, output_name, check_script_name,
                             orbital, extractor, remove_output):
    """
    Create molcas execution script for condor pool

    Parameters
    ----------
        script_name : str
            Name of final shell script
        molcas_module : str
            Condor module name for molcas
        aws : bool
            If True use amazon webservices (different python version)
        input_name : str
            Name of molcas input file
        output_name : str
            Name of molcas output file
        check_script_name : str
            Name of molcas checking script from `_gen_check_script`
        orbital : str {"3d", "4f"}
            Orbitals to check for in active space
        extractor : str
            bash commands for extraction of data from molcas output file
        remove_output : bool
            If True, delete .output file if calculation is successful

    Returns
    -------
        None
    """

    if aws:
        python_module = "anaconda/python37"
    else:
        python_module = "anaconda/python36"

    # Generate the molcas shell script
    # This runs the individual molcas calculations
    with open(script_name, "w") as f:

        f.write('#!/bin/bash --login\n')

        f.write('\n')

        f.write('# !!! Do not run this file manually !!!\n')
        f.write('# This file is run automatically by condor \n')
        f.write('# on the execute side and takes a path as argument\n')
        f.write('# !!! Do not run this file manually !!!\n')

        f.write('\n')

        f.write('module load {}\n'.format(molcas_module))
        f.write('module load {}\n'.format(python_module))

        f.write('export MOLCAS_WORKDIR=$(pwd -P)\n')
        f.write('export MOLCAS_MEM=16000\n')
        f.write('export MOLCAS_DISK=20000\n')

        f.write('\n')

        f.write("if [ -f $MOLCAS/bin/pymolcas ]; then\n")
        f.write("  $MOLCAS/bin/pymolcas {} >> {}\n".format(
            input_name, output_name
        ))
        f.write("else \n")
        f.write("  pymolcas {} >> {}\n".format(input_name, output_name))
        f.write("fi\n")
        f.write('\n')

        # Add user supplied extractor code
        f.write(extractor)

        f.write('\n\n')

        f.write('python {} {} {} > check.txt\n\n'.format(
            check_script_name,
            output_name,
            orbital
            )
        )

        # If failed, then echo submit node input file location to failed.txt
        # this is then collected by condor in post-processing step
        f.write("if grep -q 'FAIL' check.txt; then\n")
        # Send file location to failed.txt, later appended
        # to dir_list_failed.txt
        f.write(' echo $1 >> failed.txt\n')
        # Delete molcas output if successful to avoid excess disk usage
        f.write("else\n")
        f.write(" touch failed.txt\n")
        if remove_output:
            f.write(" rm {}\n".format(output_name))
            f.write(" touch {}\n".format(output_name))
        f.write('fi\n')

        st = os.stat(script_name)
        os.chmod(script_name, st.st_mode | stat.S_IEXEC)

    return


def _gen_postprocess(post_proc_script):

    """
    Creates a postprocessing file which appends all failed.txt files to a
    single new file called dir_list_failed.txt

    Parameters
    ----------
        post_proc_script : str
            Name of post processing script

    Returns
    -------
        None
    """

    with open(post_proc_script, "w") as f:

        f.write('#!/bin/bash\n\n')
        f.write('cat failed.txt* > dir_list_failed.txt\n')
        f.write('rm failed.txt*\n')
        f.write('exit 0')

    st = os.stat(post_proc_script)
    os.chmod(post_proc_script, st.st_mode | stat.S_IEXEC)

    return


def _gen_submit_dag(dag_file, condor_script, post_proc_script):

    """
    Creates a submit.dag file that tells Condor to run condor shell script
    and once all jobs in that are finished, run the post-processing script

    See
    http://ri.itservices.manchester.ac.uk/htccondor/jobs/postprocessing/

    Parameters
    ----------
        dag_file : str
            name of submit.dag file
        condor_script : str
            name of condor script file
        post_proc_script : str
            name of post processing script file

    Returns
    -------
        None
    """

    with open(dag_file, "w") as f:

        f.write('job A {}\n'.format(condor_script))
        f.write('script post A ./{}\n\n\n'.format(post_proc_script))

    return


def _gen_check_script(f_name, happy_landing=False):
    """
    Creates a small python script using `molcas_suite.extractor` which checks
    for successful completion of the molcas calculation

    Parameters
    ----------
        f_name : str
            Name of extractor file
        happy_landing : bool, default False
            If True, check for happy landing in output file

    Returns
    -------
        None
    """

    with open(f_name, 'w') as f:
        f.write('#! /usr/bin/env python3\n\n')
        f.write('import numpy as np\n')
        f.write('import sys\n\n\n')
        f.write(inspect.getsource(read_elec_orb))
        f.write('\n\n')
        f.write(inspect.getsource(read_completion))
        f.write('\n\n')
        f.write(inspect.getsource(read_rasscf_orb))
        f.write('\n\n')
        f.write(inspect.getsource(check_single_aniso))
        f.write('\n\n')
        f.write('if __name__ == "__main__":\n')
        f.write('    f_molcas = sys.argv[1]\n')
        f.write('    orb = sys.argv[2]\n')
        f.write('\n')
        f.write('    if read_rasscf_orb(f_molcas, orb) == 1:\n')
        f.write('        print("FAIL - no convergence")\n')
        f.write('        exit()\n')
        f.write('    elif read_rasscf_orb(f_molcas, orb) == 2:\n')
        f.write('        print("FAIL - active space")\n')
        f.write('        exit()\n')
        f.write('    elif not check_single_aniso(f_molcas):\n')
        f.write('        print("FAIL - no single_aniso")\n')
        f.write('        exit()\n')
        if happy_landing:
            f.write('    elif not read_completion(f_molcas):\n')
            f.write('        print("FAIL - no happy landing")\n')
            f.write('        exit()\n')
        f.write('    else:\n')
        f.write('        print("SUCCESS")\n')

    st = os.stat(f_name)
    os.chmod(f_name, st.st_mode | stat.S_IEXEC)

    return
