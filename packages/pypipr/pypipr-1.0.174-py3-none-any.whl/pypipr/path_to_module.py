import os

from pypipr.dirname import dirname


def path_to_module(path, indeks=0):
    """
    Mengubah absolute path file menjadi path modul relatif terhadap cwd (current working directory),
    dengan opsi untuk memangkas bagian akhir path berdasarkan indeks.

    Parameter:
        abs_path (str): Path absolut menuju file.
        indeks (int):
            - 0 => hasil lengkap hingga file (tanpa ekstensi),
            - -1 => tanpa nama file, hanya foldernya,
            - -2 => dua folder di atasnya, dst.

    Returns:
        str: Path bergaya modul Python (dipisah dengan ".")
    """
    path = dirname(path, abs_path=False, indeks=indeks)
    return path.replace(os.sep, ".")

    cwd = os.getcwd()
    rel_path = os.path.relpath(abs_path, cwd)
    rel_path_no_ext = os.path.splitext(rel_path)[0]

    parts = rel_path_no_ext.split(os.sep)

    if indeks < 0:
        parts = parts[: len(parts) + indeks]

    return ".".join(parts)
