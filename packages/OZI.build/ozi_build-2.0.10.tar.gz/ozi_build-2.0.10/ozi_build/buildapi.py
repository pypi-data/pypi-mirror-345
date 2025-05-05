"""PEP-517 compliant buildsystem API"""

import logging
import os
import re
import shutil
import subprocess
import sysconfig
import tarfile
import tempfile
from gzip import GzipFile
from pathlib import Path

from wheel.wheelfile import WheelFile

from ._pyc_wheel import convert_wheel
from ._util import GET_CHECK
from ._util import _write_wheel_file
from ._util import cd
from ._util import install_files_path
from ._util import meson
from ._util import meson_configure
from .config import Config
from .metadata import get_python_bin
from .pep425tags import get_platform_tag

log = logging.getLogger(__name__)


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def get_requires_for_build_wheel(config_settings=None):
    """Returns a list of requirements for building, as strings"""
    return Config().get('dependencies', [])


# For now, we require all dependencies to build either a wheel or an sdist.
get_requires_for_build_sdist = get_requires_for_build_wheel


def check_is_pure(installed):
    variables = sysconfig.get_config_vars()
    suffix = variables.get('EXT_SUFFIX') or variables.get('SO') or variables.get('.so')
    # msys2's python3 has "-cpython-36m.dll", we have to be clever
    split = suffix.rsplit('.', 1)
    suffix = split.pop(-1)

    for installpath in installed.values():
        if "site-packages" in installpath or "dist-packages" in installpath:
            if installpath.split('.')[-1] == suffix:
                return False

    return True


def prepare_metadata_for_build_wheel(
    metadata_directory, config_settings=None, builddir=None, config=None
):
    """Creates {metadata_directory}/foo-1.2.dist-info"""
    if not builddir:
        builddir = tempfile.TemporaryDirectory().name
        meson_configure(builddir)
    if not config:
        config = Config(builddir)

    dist_info = Path(
        metadata_directory,
        '{}-{}.dist-info'.format(
            normalize(config['name']).replace('-', '_'), config['version']
        ),
    )
    dist_info.mkdir(exist_ok=True)

    is_pure = check_is_pure(config.installed)
    with (dist_info / 'WHEEL').open('w') as f:
        _write_wheel_file(f, False, is_pure)

    with (dist_info / 'METADATA').open('w') as f:
        f.write(config.get_metadata())

    for i in config.get('license-files'):
        with (dist_info / i).open('w') as fw:
            with Path(i).open('r') as fr:
                fw.write(fr.read())

    if config.get('entry-points') or config.get('scripts') or config.get('gui-scripts'):
        res = ''
        console_scripts = {'console_scripts': config.get('scripts', {})}
        gui_scripts = {'gui_scripts': config.get('gui-scripts', {})}
        entry_points = config.get('entry-points', {})
        entry_points.update(console_scripts)
        entry_points.update(gui_scripts)
        for group_name in sorted(entry_points):
            group = entry_points[group_name]
            if len(group) != 0:
                res += '[{}]\n'.format(group_name)
                for entrypoint, module in group.items():
                    res += '{} = {}\n'.format(entrypoint, module)
                res += '\n'
        with (dist_info / 'entry_points.txt').open('w') as f:
            f.write(res)

    return dist_info.name


def get_abi(python):
    return subprocess.check_output([python, '-c', GET_CHECK]).decode('utf-8').strip('\n')


class WheelBuilder:
    def __init__(self):
        self.wheel_zip = None  # type: ignore
        self.builddir = tempfile.TemporaryDirectory()
        self.installdir = tempfile.TemporaryDirectory()

    def build(self, wheel_directory, config_settings, metadata_dir):
        config = Config()
        argv_meson_options = config_settings.get('meson-options', '').split(' ')
        meson_options = (
            argv_meson_options if not config.meson_options else config.meson_options
        )
        args = [
            self.builddir.name,
            '--prefix',
            self.installdir.name,
        ] + list(filter(None, meson_options))
        meson_configure(*args)
        config.builddir = self.builddir.name
        if config['version'] == '%OZIBUILDVERSION%':
            config['version'] = Path(os.getcwd()).name.split('-')[1]
        metadata_dir = prepare_metadata_for_build_wheel(
            wheel_directory, builddir=self.builddir.name, config=config
        )

        is_pure = check_is_pure(config.installed)
        platform_tag = config.platforms or 'any' if is_pure else get_platform_tag()
        python = get_python_bin(config)
        if not is_pure:
            abi = get_abi(python)
        else:
            abi = config.pure_python_abi or get_abi(python)
        target_fp = wheel_directory / '{}-{}-{}-{}.whl'.format(
            normalize(config['name']).replace('-', '_'),
            config['version'],
            abi,
            platform_tag,
        )

        self.wheel_zip: WheelFile = WheelFile(str(target_fp), 'w')
        for f in os.listdir(str(wheel_directory / metadata_dir)):
            self.wheel_zip.write(
                str(wheel_directory / metadata_dir / f),
                arcname=str(Path(metadata_dir) / f),
            )
        shutil.rmtree(Path(wheel_directory) / metadata_dir)

        # Make sure everything is built
        meson('install', '-C', self.builddir.name)
        self.pack_files(config)
        self.wheel_zip.close()
        optimize, *_ = [
            i.get('value', -1)
            for i in config.options
            if i.get('name', '') == 'python.bytecompile'
        ]
        convert_wheel(Path(target_fp), optimize=optimize, **config.pyc_wheel)
        return target_fp.name

    def pack_files(self, config):
        for _, installpath in config.installed.items():
            if "site-packages" in installpath:
                installpath = install_files_path(installpath, 'site-packages')
                self.wheel_zip.write_files(installpath)
                break
            elif "dist-packages" in installpath:
                installpath = install_files_path(installpath, 'dist-packages')
                self.wheel_zip.write_files(installpath)
                break


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """Builds a wheel, places it in wheel_directory"""
    return WheelBuilder().build(Path(wheel_directory), config_settings, metadata_directory)


def adjust_name(info: tarfile.TarInfo) -> tarfile.TarInfo:
    info.name = normalize(info.name).replace('-', '_')
    return info


def add_name(config, pyproject):
    text = pyproject.read_text()
    maybe_comment = re.search(r'\[project\](.*)\n', text)
    maybe_comment = maybe_comment.group(1) if maybe_comment else ""
    pyproject.write_text(
        text.replace(
            '[project]\n',
            '[project]{}\nname="{}"\n'.format(
                maybe_comment,
                config["name"],
            ),
        )
    )


def add_version(config, pyproject):
    text = pyproject.read_text()
    maybe_comment = re.search(r'\[project\](.*)\n', text)
    maybe_comment = maybe_comment.group(1) if maybe_comment else ""
    maybe_version = re.search(r'\[project\](?:(?:.*)\n)*(\s*version\s*=.*)', text)
    if maybe_version:
        pyproject.write_text(
            text.replace('[project]\n', '[project]{}\n'.format(maybe_comment)).replace(
                maybe_version.group(1), 'version = "{}"'.format(config["version"])
            )
        )
    else:
        pyproject.write_text(
            text.replace(
                '[project]\n',
                '[project]{}\nversion="{}"\n'.format(
                    maybe_comment,
                    config["version"],
                ),
            )
        )


def build_sdist(sdist_directory, config_settings=None):
    """Builds an sdist, places it in sdist_directory"""
    distdir = Path(sdist_directory)
    with tempfile.TemporaryDirectory() as builddir:
        with tempfile.TemporaryDirectory() as installdir:
            config = Config()
            argv_meson_options = list(
                filter(None, config_settings.get('meson-options', '').split(' '))
            )
            meson_options = (
                argv_meson_options if not config.meson_options else config.meson_options
            )
            args = [builddir, '--prefix', installdir] + meson_options
            meson(*args, builddir=builddir)
            config.builddir = builddir
            argv_dist_options = list(
                filter(None, config_settings.get('meson-dist-options', '').split(' '))
            )
            meson_options = (
                argv_dist_options
                if not config.meson_dist_options
                else config.meson_dist_options
            )
            dist_args = ['dist', '--no-tests', '-C', builddir] + meson_options
            meson(*dist_args)
            tf_dir = '{}-{}'.format(config['name'], config['version'])
            mesondistfilename = '%s.tar.xz' % tf_dir
            mesondisttar = tarfile.open(Path(builddir) / 'meson-dist' / mesondistfilename)
            for entry in mesondisttar:
                # GOOD: Check that entry is safe
                if os.path.isabs(entry.name) or ".." in entry.name:
                    raise ValueError("Illegal tar archive entry")
                mesondisttar.extract(entry, installdir)
            # OZI uses setuptools_scm to create PKG-INFO
            pkg_info = config.get_metadata()
            distfilename = '{}-{}.tar.gz'.format(
                normalize(config['name']).replace('-', '_'), config['version']
            )
            target = distdir / distfilename
            source_date_epoch = os.environ.get('SOURCE_DATE_EPOCH', '')
            mtime = int(source_date_epoch) if source_date_epoch else None
            with GzipFile(str(target), mode='wb', mtime=mtime) as gz:
                with cd(installdir):
                    with tarfile.TarFile(
                        str(target),
                        mode='w',
                        fileobj=gz,
                        format=tarfile.PAX_FORMAT,
                    ) as tf:
                        root = Path(installdir) / tf_dir
                        add_version(config, root / 'pyproject.toml')
                        if not config.name_provided:
                            add_name(config, root / 'pyproject.toml')
                        tf.add(
                            tf_dir,
                            arcname='{}-{}'.format(
                                normalize(config['name']).replace('-', '_'),
                                config['version'],
                            ),
                            recursive=True,
                        )
                        pkginfo_path = root / 'PKG-INFO'
                        if not pkginfo_path.exists():
                            with open(pkginfo_path, mode='w') as fpkginfo:
                                fpkginfo.write(pkg_info)
                                fpkginfo.flush()
                                tf.add(
                                    Path(tf_dir) / 'PKG-INFO',
                                    arcname=Path(
                                        '{}-{}'.format(
                                            normalize(config['name']).replace('-', '_'),
                                            config['version'],
                                        )
                                    )
                                    / 'PKG-INFO',
                                )
    return target.name
