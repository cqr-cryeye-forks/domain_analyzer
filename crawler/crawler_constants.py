import pathlib
import re
from typing import Final

email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

FILE_EXTENSIONS = [
    '.rss', '.RSS', '.xsl', '.XSL', '.xml', '.XML', '.msi', '.MSI', '.vbs', '.VBS',
    '.db', '.DB', '.asc', '.ASC', '.js', '.JS', '.sql', '.SQL', '.rar', '.RAR',
    '.mdb', '.MDB', '.jar', '.JAR', '.mpg', '.MPG', '.sty', '.STY', '.dat', '.DAT',
    '.f', '.F', '.c', '.C', '.h', '.H', '.cnf', '.CNF', '.flv', '.FLV', '.wma', '.WMA',
    '.swf', '.SWF', '.py', '.PY', '.bz2', '.BZ2', '.7z', '.7Z', '.css', '.CSS',
    '.ico', '.ICO', '.avi', '.AVI', '.mkv', '.MKV', '.doc', '.DOC', '.ppt', '.PPT',
    '.pps', '.PPS', '.xls', '.XLS', '.docx', '.DOCX', '.pptx', '.PPTX', '.ppsx', '.PPSX',
    '.xlsx', '.XLSX', '.sxw', '.SXW', '.sxc', '.SXC', '.sxi', '.SXI', '.odt', '.ODT',
    '.ods', '.ODS', '.odg', '.ODG', '.odp', '.ODP', '.pdf', '.PDF', '.wpd', '.WPD',
    '.txt', '.TXT', '.gnumeric', '.GNUMERIC', '.csv', '.CSV', '.zip', '.ZIP',
    '.tar', '.TAR', '.gz', '.GZ', '.bz', '.BZ', '.bmp', '.BMP', '.jpg', '.JPG',
    '.jpeg', '.JPEG', '.png', '.PNG', '.gif', '.GIF', '.exe', '.EXE'
]

MAIN_DIR: Final[pathlib.Path] = pathlib.Path(__file__).parents[1]
