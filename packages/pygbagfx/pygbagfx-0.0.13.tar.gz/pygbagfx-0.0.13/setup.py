from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import pathlib
import platform

root_dir = pathlib.Path(__file__).parent.absolute().relative_to(pathlib.Path.cwd().absolute())
src_dir = root_dir / 'src'
gbagfx_dir = src_dir / 'gbagfx'

includes = list(gbagfx_dir.glob('*.h')) + [gbagfx_dir / 'main.c']
sources = [src_dir / '_gbagfx.c'] + [f for f in list(gbagfx_dir.glob('*.c')) if f not in includes]

long_description = (root_dir / 'README.md').read_text(encoding='utf-8')
debug_c_args = {
    'unix': ['-Og', '-g', '-lpng'],
    'gcc': ['-Og', '-g', '-lpng'],
}
release_c_args = {
    'unix': ['-Os', '-s', '-lpng', '-ffunction-sections'],
    'gcc': ['-Os', '-s', '-lpng', '-ffunction-sections'],
    'msvc': ['/Os'],
    'mingw32': ['-Os', '-s', '-lpng'],
}
debug_l_args = {
}
release_l_args = {
    'unix': ['-s', '-Wl,--gc-sections'],
    'gcc': ['-s', '-Wl,--gc-sections'],
}
c_args = release_c_args
l_args = release_l_args

if platform.system() == 'Darwin':
    for tool in l_args:  # gc-sections not supported by llvm
        if '-Wl,--gc-sections' in l_args[tool]:
            l_args[tool].remove('-Wl,--gc-sections')

gbagfx_module = Extension(
    'pygbagfx._gbagfx',
    sources=list(map(str, sources)),
    depends=list(map(str, includes)),
    libraries=['png'],
    define_macros=[('NO_ASSERT', 1), ('NDEBUG', 1)])

class GbagfxExtBuilder(build_ext):
    def build_extensions(self):
        c = self.compiler.compiler_type
        if c not in c_args and c not in l_args:
            print('using unknown compiler: ' + c)
        if c in c_args:
            for e in self.extensions:
                e.extra_compile_args = c_args[c]
        if c in l_args:
            for e in self.extensions:
                e.extra_link_args = l_args[c]
        return build_ext.build_extensions(self)

setup(
    name='pygbagfx',
    author='RhenaudTheLukark',
    version='0.0.13',
    description='Python wrapper for gbagfx',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/RhenaudTheLukark/pygbagfx',
    python_requires='>=3',
    ext_modules=[gbagfx_module],
    cmdclass={'build_ext': GbagfxExtBuilder},
)
