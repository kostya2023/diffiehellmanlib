import os
import sys
import subprocess
import shutil
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist

# Кастомная команда для сборки через CMake
class CMakeBuild(build_ext):
    def run(self):
        # Проверяем, установлен ли CMake
        if shutil.which("cmake") is None:
            raise RuntimeError("CMake is not installed. Please install CMake.")

        # Папка проекта (где находится CMakeLists.txt)
        project_dir = os.path.dirname(os.path.abspath(__file__))

        # Вызываем cmake . в папке проекта
        subprocess.run(["cmake", "."], cwd=project_dir, check=True)
        subprocess.run(["make"], cwd=project_dir, check=True)

        # Определяем имя библиотеки в зависимости от платформы
        if sys.platform == "win32":
            lib_name = "diffiehellmanlib.dll"
        elif sys.platform == "darwin":
            lib_name = "libdiffiehellmanlib.dylib"
        else:
            lib_name = "libdiffiehellmanlib.so"

        # Путь к собранной библиотеке
        lib_path = os.path.join(project_dir, lib_name)

        # Путь, куда копировать библиотеку
        dest_path = os.path.join(self.build_lib, "diffiehellmanlib")
        os.makedirs(dest_path, exist_ok=True)

        # Копируем библиотеку
        shutil.copy(lib_path, os.path.join(dest_path, lib_name))

        # Удаляем временные файлы (CMakeCache.txt, Makefile и т.д.)
        self.cleanup_temp_files(project_dir)

    def cleanup_temp_files(self, project_dir):
        """Удаляет временные файлы после сборки."""
        temp_files = [
            "CMakeCache.txt",
            "CMakeFiles",
            "cmake_install.cmake",
            "Makefile",
        ]
        for file_name in temp_files:
            file_path = os.path.join(project_dir, file_name)
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)

# Кастомная команда для sdist (чтобы не компилировать при сборке в архив)
class CustomSdist(sdist):
    def run(self):
        # Просто копируем исходники, без сборки
        super().run()

# Метаданные проекта
setup(
    name="diffiehellmanlib",
    version="4.0a0",
    author="Konstantin Gorshkov",
    author_email="kostya_gorshkov_06@vk.com",
    description="Diffie-Hellman key exchange implementation",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kostya2023/diffiehellmanlib",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C++",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
    ],
    packages=find_packages(),
    package_data={
        "diffiehellmanlib": ["src/*.cpp", "src/*.h", "CMakeLists.txt"],  # Включаем исходники в пакет
    },
    install_requires=["cryptography>=3.4"],
    python_requires=">=3.7",
    cmdclass={
        "build_ext": CMakeBuild,  # Используем кастомную сборку
        "sdist": CustomSdist,     # Используем кастомную команду для sdist
    },
)