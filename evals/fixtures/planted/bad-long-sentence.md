# Summary

The stage reads the plan. It writes the research file.

When the stage finds a fact in the fixture project it writes the fact down with the file and the line number so that the judge can later compare the output of the old tree with the output of the new tree and see what changed.

The judge reads both files. It reports each lost fact.
