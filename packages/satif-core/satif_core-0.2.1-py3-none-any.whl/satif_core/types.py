from pathlib import Path
from typing import Dict, List, Union

# Basic Types
FilePath = Union[Path, str]

# Input/Output Specifications
Datasource = Union[FilePath, List[FilePath]]  # Path(s) to input file(s)
OutputData = Union[FilePath, Dict[str, FilePath]]  # Path(s) to output file(s)
WriteOutputFiles = List[Path]

SDIFPath = FilePath
