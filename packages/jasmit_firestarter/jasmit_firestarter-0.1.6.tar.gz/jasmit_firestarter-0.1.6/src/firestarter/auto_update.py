"""
auto_update.py
"""
import argparse
import config
import pathlib
import shutil
import sys
import run_shell_cmds as rsc


#  -----------------------------------------------------------------------------
def copy_files(source_dir, target_dir, file_names, file_mode):
    for file in file_names:
        source_file = source_dir + "/" + file
        target_file = target_dir + "/" + file

        msg = f'      {file}'

        try:
            shutil.copyfile(source_file, target_file)
        except FileNotFoundError:
            msg += ' - was not found in the source directory.'
            print(msg)
            continue

#         os.chmod(target_file, file_mode)
        print(f'{msg} successful.')


#  -----------------------------------------------------------------------------
def get_cmdline_args():
    parser = argparse.ArgumentParser(description="auto_update")

    parser.add_argument(
        "-a", "--application", required=True,
        help="""Application - The name of the application being
        updated. Must match the name know to GIT."""

    )

    parser.add_argument(
        "-e", "--environment", required=True,
        choices=['devl', 'test', 'prod'],
        help="Environment - devl, test, or prod"
    )

    args = parser.parse_args()
    return args


#  ----------------------------------------------------------------------------
def perform_github_clone(application_name):
    cmd = f"cd /tmp ; git clone https://github.com/jasmit35/{application_name}.git"
    rc, stdout, stderr = rsc.run_shell_cmds(cmd)
    sys.stdout.buffer.write(stdout)
    if rc:
        sys.stderr.buffer.write(stderr)
        sys.exit(rc)


#  ----------------------------------------------------------------------------
def prep_github_extract(application_name):
    tmp_path = pathlib.Path(f"/tmp/{application_name}")

    if not tmp_path.is_dir():
        perform_github_clone(application_name)

    else:
        print("A github clone alredy exist.\n")
        response = None
        while response not in ['y', 'n']:
            response = input("reuse (y/n))?")

        if response == 'n':
            shutil.rmtree(tmp_path)
            perform_github_clone(application_name)


#  -----------------------------------------------------------------------------
def process_asset(environment, cfg, asset):
    home = str(pathlib.Path.home())
    src_dir = cfg[f'{environment}.{asset}_assets.src_dir']
    trg_dir = home + cfg[f'{environment}.{asset}_assets.trg_dir']
    file_names = cfg[f'{environment}.{asset}_assets.file_names']
    file_mode = cfg[f'{environment}.{asset}_assets.file_mode']

    print(f'\n  Updating {asset} assets...')
    print(f'    Copying from {src_dir} to {trg_dir}')

    #  Test that the directories exists
    if not pathlib.Path(src_dir).is_dir():
        print(f'      Error!  The source directory "{src_dir}" \
does not exist!')
        return

    if not valid_target_directory(trg_dir):
        return

    copy_files(src_dir, trg_dir, file_names, file_mode)


#  -----------------------------------------------------------------------------
def valid_target_directory(target_dir):

    if pathlib.Path(target_dir).is_dir():
        return True

    else:
        print(f"The directory {target_dir} does not exist.\n")

        response = None
        while response not in ['y', 'n']:
            response = input("Would you like to create it (y/n)? ")

        if response == 'y':
            p = pathlib.Path(target_dir)
            p.mkdir(parents=True)
            return True
        else:
            return False


#  ----------------------------------------------------------------------------
def main():
    args = get_cmdline_args()
    application_name = args.application
    environment = args.environment

    prep_github_extract(application_name)

    if environment == 'devl':
        print("Processing complete for development environment.")
        sys.exit(0)

    cfg = config.Config(
        f'/tmp/{application_name}/{application_name}_au.cfg'
    )
    assets = cfg[f'{environment}.assets']
    for asset in assets:
        process_asset(environment, cfg, asset)

    sys.exit(0)


#  ----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
