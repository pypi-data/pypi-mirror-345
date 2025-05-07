======================================
SimPipe - the CTAO Simulation Pipeline
======================================

The **CTAO Simulation Production Pipeline (SimPipe)** provides the
software, workflows, and data models for generating accurate Monte Carlo
simulations of the CTAO observatory.


.. toctree::
    :maxdepth: 1
    :caption: Contents:
    :hidden:

    installation
    user-guide
    reference
    changelog
    chart


Components
==========

- `simtools`_ - toolkit for model parameter management, production configuration, setting, validation workflows.
  See: https://github.com/gammasim/simtools
- `CORSIKA`_ - air shower simulations.
  See: https://www.iap.kit.edu/corsika/
- `sim_telarray`_ - telescope simulations.
  See: https://gitlab.cta-observatory.org/Konrad.Bernloehr/sim_telarray
- simulation model database - mongoDB database for simulation model parameters and production model definitions

.. _ctao-simpipe: https://gitlab.cta-observatory.org/cta-computing/dpps/simpipe
.. _simtools: https://github.com/gammasim/simtools
.. _CORSIKA: https://www.iap.kit.edu/corsika/
.. _sim_telarray: https://gitlab.cta-observatory.org/Konrad.Bernloehr/sim_telarray


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
