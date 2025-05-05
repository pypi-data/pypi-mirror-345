import datetime
import xml.etree.ElementTree as ET
import defusedxml.ElementTree as defused_ET
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Cell:
  id: int
  title: str | None = None
  text: ET.Element | None = None
  code: str | None = None
  output: str | None = None
  images: list = field(default_factory=list)

  def __init__(self, xml: ET.Element):
    self.id = int(xml.find("count").text)
    self.title = (
      xml.find("steptitle").text.strip() if xml.find("steptitle") is not None else None
    )
    self.code = (
      xml.find("mcode").text.strip() if xml.find("mcode") is not None else None
    )
    self.output = (
      xml.find("mcodeoutput").text.strip()
      if xml.find("mcodeoutput") is not None
      else None
    )
    self.text = xml.find("text")
    self.images = [image.get("src") for image in xml.findall("img")]

  def text_as_str(self) -> str:
    return (
      ET.tostring(self.text).decode("utf-8").strip()[6:-7]
      if self.text is not None
      else ""
    )

  def text_as_latex(self) -> str:
    return (
      "\n\n".join(p.text.strip() for p in self.text.findall("p"))
      if self.text is not None
      else ""
    )

  def __lt__(self, cell) -> bool:
    return self.id < cell.id


@dataclass
class MatlabFile:
  cells: list[Cell]
  date: datetime.datetime
  matlab_release: str
  matlab_version: str
  filename: str
  output_dir: Path

  def __init__(self, xml: ET.Element):
    self.cells = [Cell(cell) for cell in xml.findall(".//cell")]
    self.cells.sort()

    self.date = datetime.datetime.strptime(xml.find("date").text.strip(), "%Y-%m-%d")
    self.matlab_release = xml.find("release").text.strip()
    self.matlab_version = xml.find("version").text.strip()
    self.filename = xml.find("m-file").text.strip()
    fname = Path(xml.find("filename").text.strip())
    self.filename = Path(fname.name)
    gen_dir = Path(xml.find("outputdir").text.strip())
    if fname.parent in gen_dir.parents:
      gen_dir = Path(*gen_dir.parts[len(fname.parent.parts) :])
    self.output_dir = gen_dir

def parse(mfile: Path) -> MatlabFile:
  tree = defused_ET.parse(mfile)
  root = tree.getroot()
  return MatlabFile(root)
