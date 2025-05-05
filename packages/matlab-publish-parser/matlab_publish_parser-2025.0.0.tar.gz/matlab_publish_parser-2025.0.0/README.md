This package is used to parse the xml output of MATLAB publish, and
this way facilitate deriving more advanced documentation that contain
MATLAB code with matching output and figures.

# Usage

## MATLAB processing

Write the code that you want to create output from as a MATLAB publish
document.  The package will parse the code, and separate the different
cells.  The package will separate documentation, executed code, console
output and figures.

In MATLAB process the created file (in this case ``example.m``) using publish:
```
publish('example.m',...
        'format', 'xml',...
        'imageFormat', 'epsc',...
        'outputDir', 'gen/',...
        'catchError', false);  % Fail on thrown exception

```
This will produce the file ``gen/example.xml``

## Python Processing
Usage:

```
import matlab_publish_parser as mpp

mf = matlab_publish_parser.parse(Path('example.xml'))

print(mf.filename)  # The name of the processed file
print(mf.output_dir)  # Directory for generated files
for c in mf.cells:
  print(c.title)  # Title of cell
  print(c.code)  # Executed code in cell
  print(c.output)  # Console output from cell
  ...

```

Explore the object to figure out what has been extracted.