# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""#Processing module.

Processings are used to manipulate the config behavior when doing a manipulation
like merging, saving, loading, etc.

Each processing is a class that contains 5 methods that change the config
at different timings:

 * premerge: called before merging
 * postmerge: called after merging
 * endbuild: called at the end of the build or an update
   (via cliconfig.make_config or cliconfig.update_config)
 * postload: called after loading
 * presave: called before saving

To create quiclky a processing, you can use the functions
cliconfig.create_processing_value and cliconfig.create_processing_keep_property.
To make a more complex processing, you can inherit from cliconfig.Processing and
customize the methods you want among the five ones.

## Submodules

 * cliconfig.processing.base: Contains base class for processing.
 * cliconfig.processing.builtin: Contains the default processings.
 * cliconfig.processing.create: Contains support functions to create processing.
"""
