import os
import subprocess

class CVSHandler():
    """ Handler of CVS (fir, mercurial...) directories, 
        The main purpose of this class is to cache external cvs command output, and determine the appropriate files to yield when navigating to a subdirectory of a project.
        This basically means that the external command is run once (ie git ls-files), cached, and when calling get_source_files on a subdirectory of the project root (ie project-root/subdir),
        filtering from all project files of is done here.
    """
    def __init__(self, cvs):
        self._files_cache = {}
        self.cvs = cvs

    def _get_cached_dir(self, directory):
        """ a directory is considered cached if it's the project root or a subdirectory of that project root.
            returns the project root dir, or None if the directory is not cached.
        """
        if directory in self._files_cache:
            return directory
        if os.path.dirname(directory) == directory:
            return None
        return self._get_cached_dir(os.path.dirname(directory))

    def get_source_files(self, directory):
        cached_dir = self._get_cached_dir(directory)
        if not cached_dir:
            try:
                # check if it's a tracked cvs dir, if yes, get the project root and the source files
                root_dir = self.cvs._get_root(directory)
                self._files_cache[root_dir] = self.cvs._get_tracked_files(root_dir)
            except Exception as e:
                # not a cvs tracked dir, save it to not issue that command again
                self._files_cache[directory] = []
            # the cached dir is the project root directory if it's a tracked directory
            cached_dir = self._get_cached_dir(directory)

        files = self._files_cache[cached_dir]
        # the passed directory argument is a subdirectory of the project root
        if directory != cached_dir:
            rel_dir = os.path.relpath(directory, cached_dir)
            files = [f[len(rel_dir)+1:] for f in files if f.startswith(rel_dir)]
        return files
 

class Git():
    @staticmethod
    def _get_root(directory):
        return run_command("cd %s && git rev-parse --show-toplevel" % directory).strip()
    @staticmethod
    def _get_tracked_files(directory):
        return run_command("cd %s && git ls-files && git ls-files --others --exclude-standard" % directory).strip().split('\n')

class Mercurial():
    @staticmethod
    def _get_root(directory):
        return run_command("cd %s && hg root" % directory).strip()
    @staticmethod
    def _get_tracked_files(directory):
        return run_command("cd %s && (hg status -marcu | cut -d' ' -f2)" % directory).strip().split('\n')

class DefaultDirHandler():
    """ The default directory handler uses the 'find' external program to return all the files inside a given directory up to MAX_depth depth (ie, if maxdepth=2, returns all files inside that dir, and all files in a subdir of that directory)"""

    def __init__(self):
        self._cache = {}
        self.MAX_DEPTH = 3

    def _walk_down(self, start_dir):
        try:
            out = run_command("find %s -maxdepth %s -type f -not -path '*/\.*'" % (start_dir, self.MAX_DEPTH))
        except subprocess.CalledProcessError as e:
            # Find returns a non 0 exit status if listing a directory fails (for example, permission denied), but still output all files in other dirs
            # ignore those failed directories.
            out = e.output.decode('utf-8')
        if not out:
            return []
        files = out.split('\n')
        return [os.path.relpath(f, start_dir) for f in files if f]

    def get_source_files(self, start_dir):
        if not start_dir in self._cache:
            self._cache[start_dir] = self._walk_down(start_dir)
        return self._cache[start_dir]

def run_command(string):
    ''' fork a process to execute the command string given as argument, returning the string written to STDOUT '''
    DEVNULL = open(os.devnull, 'wb')
    return subprocess.check_output(string, stderr=DEVNULL, shell=True).decode('utf-8')


git = CVSHandler(Git)
hg = CVSHandler(Mercurial)
default = DefaultDirHandler()

def get_source_files(directory):
    """ check first if the given directory is inside a git tracked project, if no, check with mercurial, if no, fallback to the default handler """
    files = git.get_source_files(directory)
    # if the returned files list is empty, it's considered not a tracked directory
    if files:
        return files
    files = hg.get_source_files(directory)
    if files:
        return files
    return default.get_source_files(directory)

