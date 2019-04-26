# miniHive

This is the material for a term project part of a database systems course taught at OTH Regensburg in the summer term of 2018. The students in this course built their own SQL-on-Hadoop engine as a term project in just 8 weeks. 

*miniHive* is written in Python and compiles SQL queries into MapReduce workflows. These are then executed on Hadoop.  *miniHive* performs generic query optimizations (selection and projection pushdown, or cost-based join reordering), as well as MapReduce-specific optimizations. 

The course was taught in English, using a flipped classroom model. The course material was mainly compiled from third-party teaching videos.

This repository contains a report on this course, as well as the material made available to the students for implementing *miniHive* milestones. 

For questions on *miniHive*, contact stefanie.scherzinger@oth-regensburg.de.
