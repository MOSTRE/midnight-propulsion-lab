# Annotated bibliography — initial screen

- National Academies (2021), *Space Nuclear Propulsion for Human Mars
  Exploration*, DOI 10.17226/25977. Assesses NTP at at least 900 s and NEP at
  at least 1 MWe for a specified 2039 opposition-class Mars baseline. It calls
  for consistent figures of merit and notes that MWe-class integrated NEP testing
  had not occurred at the time of assessment. Use as a framing and limitation
  source, not as a claim of current status.
- Mulqueen et al. (2007), NASA NTRS 20070031964. NTP Mars vehicle concepts with
  parametric engine sensitivities and shield considerations. Relevant baseline;
  not a validation datum for the present generic scenario.
- Machemer, Duchek & Nikitaev (2023), NASA NTRS 20220017479. Shows radiator
  assumptions can dominate multi-MWe power-system specific mass. Supports
  retaining radiator terms explicitly.
- White (2011), MIT PhD thesis. Uses detailed power-plant mass modeling with
  low-thrust mission optimization. Strong evidence that integrated NEP trade
  studies are established, so this project cannot claim first coupling.
- Kokan et al. (2025), *Journal of Electric Propulsion*, DOI
  10.1007/s44205-025-00145-x. Parametric 10–40 kWe NEP Saturn/Enceladus
  missions; models power-system alpha and uses Copernicus. Closest modern
  mission-level comparison found in this first pass.

Full-text access varies; metadata and conclusions must be checked again before a
publication-grade claim.

## Software-method selection

- SciPy documentation, `solve_ivp` / DOP853. DOP853 is a documented explicit
  order-eight integrator, recommended by the documentation for high-precision
  non-stiff IVPs. Chosen because it installed on this Python 3.12 environment
  and is adequate for a transparent planar benchmark.
- TudatPy documentation. It is open source and distributed through Conda; it is
  the appropriate next upgrade for ephemeris-grade propagation, but was not added
  to this small reproducible environment.
- Dymos documentation. Dymos supports simple SciPy-optimizer problems but advises
  more capable sparse optimization paths for larger problems; its Windows setup
  has added constraints. Not justified before validating the smaller model.
