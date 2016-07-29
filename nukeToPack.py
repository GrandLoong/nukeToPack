"""
Grand Loong (hoolongvfx@gmail.com)
vimeo: https://vimeo.com/loong
linkedin: https://www.linkedin.com/in/grandloong
update
    v1.01:
        remove print
        Optimized some code
    v1.02:
        add profile setting other folder
        add new function collect read Node file in Group
"""

import os
from os.path import join as joinpath
import re
import zipfile
import shutil
import threading
import time
import ConfigParser

import nuke


class NukeToPack:
    def __init__(self):
        script_dir = os.path.dirname(__file__)
        profile = joinpath(script_dir, 'profile.ini')
        nuke_file = nuke.Root().name()
        self.source_dir = os.path.dirname(nuke_file)
        if os.path.exists(profile):
            cf = ConfigParser.ConfigParser()
            cf.read(profile)
            self.source_dir = cf.get("root", "path")
        self.base_name = os.path.basename(nuke_file).split('.')[0]
        self.pack_dir = joinpath(self.source_dir, self.base_name)
        self.nuke_version = nuke.NUKE_VERSION_STRING
        if not os.path.exists(self.pack_dir):
            os.makedirs(self.pack_dir)
        self.pack_ = '[file dirname [value root.name]]/'

    def to_zip(self):
        dir_name = self.pack_dir
        zipfilename = joinpath(self.source_dir, '{0}.zip'.format(self.base_name))
        filelist = []
        if os.path.isfile(dir_name):
            filelist.append(dir_name)
        else:
            for root, dirs, files in os.walk(dir_name):
                for name in files:
                    filelist.append(os.path.join(root, name))

        zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED, True)
        prog_incr = 100.0 / len(filelist)
        for i, tar in enumerate(filelist):
            if self.task.isCancelled():
                nuke.executeInMainThread(nuke.message, args=('cancel',))
                return
            self.task.setProgress(int(i * prog_incr))
            arcname = tar[len(dir_name):]
            self.task.setMessage("compressed %s files.." % arcname)
            zf.write(tar, arcname)
        zf.close()
        time.sleep(2)

    @staticmethod
    def check_format(filepath):
        m = re.match(r'(.+)(%\d+d|#+)', filepath)
        return not bool(m)

    @staticmethod
    def unified_path_format(filepath):
        return filepath.replace('\\', '/')

    def convert(self):
        self.task = nuke.ProgressTask("NukeToPacking....")
        pack_dir = self.pack_dir + '/'
        pack_dir = self.unified_path_format(pack_dir)
        reads = [n for n in nuke.allNodes(recurseGroups=True) if n.Class() == 'Read']
        prog_incr = 100.0 / len(reads)
        for i, n in enumerate(reads):
            if self.task.isCancelled():
                nuke.executeInMainThread(nuke.message, args=('cancel',))
                return
            self.task.setProgress(int(i * prog_incr))

            file_ = n['file'].getValue()
            self.task.setMessage("Copy %s files.." % n.fullName())
            if self.check_format(file_):
                m = re.compile(r'(?P<root_dir>(\w:/))')
                match_ = m.match(file_)
                if match_:
                    old_file = file_
                    file_root = match_.groupdict()['root_dir']
                    file_ = file_.replace(file_root, pack_dir)
                    file_ = self.unified_path_format(file_)
                    new_dir = os.path.dirname(file_)
                    if not os.path.exists(new_dir):
                        os.makedirs(new_dir)
                    print old_file, new_dir,'single'
                    shutil.copy2(old_file, new_dir)
                    n['file'].setValue(file_.replace(pack_dir, self.pack_))
            else:
                dir_ = os.path.dirname(file_)
                for f in os.listdir(dir_):
                    seq_file_ = dir_ + "/" + f
                    m = re.compile(r'(?P<root_dir>(\w:/)(.+?/))')
                    match_ = m.match(seq_file_)
                    if match_:
                        old_file = seq_file_
                        file_root = match_.groupdict()['root_dir']
                        seq_file_ = seq_file_.replace(file_root, pack_dir)
                        seq_file_ = self.unified_path_format(seq_file_)
                        new_dir = os.path.dirname(seq_file_)
                        if not os.path.exists(new_dir):
                            os.makedirs(new_dir)
                        print old_file, new_dir
                        shutil.copy2(old_file, new_dir)
                m = re.compile(r'(?P<root_dir>(\w:/)(.+?/))')
                match_ = m.match(file_)
                if match_:
                    file_root = match_.groupdict()['root_dir']
                    n['file'].setValue(file_.replace(file_root, self.pack_))
        nuke.scriptSaveAs(joinpath(self.pack_dir, '{0}.nk'.format(self.base_name)))
        with open(joinpath(self.pack_dir, 'nuke2pack.info'), 'w') as f:
            f.write('Nuke: {0}'.format(self.nuke_version))
        self.to_zip()
        time.sleep(2)

    def run_to_pack(self):
        threading.Thread(None, self.convert).start()


def run():
    r = NukeToPack()
    r.run_to_pack()
