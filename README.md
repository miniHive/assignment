[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# miniHive

This is the material for a term project part of a database systems course taught at [OTH Regensburg](https://www.oth-regensburg.de/en/faculties/computer-science-and-mathematics.html) in the summer term of 2018. The students in this course built their own SQL-on-Hadoop engine as a term project in just 8 weeks.

*miniHive* is written in Python and compiles SQL queries into MapReduce workflows. These are then executed on Hadoop (e.g. on Cloudera'QuickStarts VM).  *miniHive* performs generic query optimizations (selection and projection pushdown, or cost-based join reordering), as well as MapReduce-specific optimizations.

The course was taught in English, using a flipped classroom model. The course material was mainly compiled from third-party teaching videos.

This repository contains a report on this course, as well as the material made available to the students for implementing *miniHive* milestones.

For questions on *miniHive*, contact stefanie.scherzinger@uni-passau.de.

## Citation
To refer to this material in a publication, please use this BibTeX entry:
```BibTeX
@article{miniHive,
  author    = {Stefanie Scherzinger},
  title     = {Build your own SQL-on-Hadoop Query Engine: {A} Report on a Term Project
               in a Master-level Database Course},
  journal   = {{SIGMOD} Rec.},
  volume    = {48},
  number    = {2},
  pages     = {33--38},
  year      = {2019},
  note      = {Supplementary material available at \url{https://github.com/miniHive/assignment}.},
  url       = {https://doi.org/10.1145/3377330.3377336},
  doi       = {10.1145/3377330.3377336},
}
```

## License
This work is licensed under the [Apache 2.0 License](./LICENSE.txt).

