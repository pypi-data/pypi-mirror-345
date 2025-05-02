========================
 datapipe Documentation
========================

**Version**: |version|

`datapipe` is a pipeline subsystem of the *Data Processing and Preservation
System* (DPPS). It is responsible for processing raw data into science-ready
data products.


.. toctree::
    :maxdepth: 1
    :caption: Contents:
    :hidden:

    installation
    user-guide
    reference
    changelog


Components
==========

This package contains all of the tools and dependencies needed to run the data
processing pipeline workflows that can run on the *DPPS Workload Management
System*. Most of the functionality in `datapipe` is provided by the packages
listed below, which are developed and maintained by CTAO:

`ctapipe <https://ctapipe.readthedocs.io/en/latest/>`_
    provides the core framework for command-line tools, data models and formats
    for reading and writing event data products at data levels DL0-DL2, and
    algorithms and tools for processing events from simulations and
    observations.

`pyeventio <https://github.com/cta-observatory/pyeventio>`_
    provides low-level access to simulation data, and enables `ctapipe`_ to
    read CTAO simulations via it's ``SimTelEventSource``.

`pyirf <https://cta-observatory.github.io/pyirf/>`_
    provides low-level functionality for generating and manipulating IRFs and
    related metrics like sensitivity, as well as for optimizing gamma/hadron
    cuts. When installed, it enables the `ctapipe`_ IRF tools to work.

`ctapipe-io-zfits <https://github.com/cta-observatory/ctapipe_io_zfits>`_
    A `ctapipe`_ plugin that provides access to CTAO DL0 data as a ``ctapipe.io.EventSource``

Related packages:
=================

`datapipe-testbench <http://cta-computing.gitlab-pages.cta-observatory.org/dpps/datapipe/datapipe-testbench/latest/>`_
    provides a scientific test framework and a set of standard benchmarks that
    can be run on `datapipe` outputs to generate metrics, plots, and reports,
    for verification and comparison of analyses.


Development Guidelines
======================

Developers of the and related packages must follow the guidelines specified in
the `CTAO Developer Documentation
<http://cta-computing.gitlab-pages.cta-observatory.org/documentation/developer-documentation/>`_,
; more details are given in the `ctapipe developer guidelines
<https://ctapipe.readthedocs.io/en/latest/developer-guide/index.html>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
