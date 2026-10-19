# What the results mean — in plain English

The project compares three ways of moving a spacecraft: chemical rockets, nuclear thermal propulsion, and nuclear electric propulsion.

The baseline assumes a 20-tonne spacecraft, a 2-tonne payload, and a required equivalent change in velocity of 9 km/s. Those inputs are chosen for this model; they do not define a real approved mission.

Under those assumptions, the chemical and nuclear-thermal cases need more mass than the 20-tonne limit allows. The nuclear-electric case stays within the model's mass budget by about 3.28 tonnes. Its assumed electric power system and radiator are heavy, but the higher specific impulse reduces the propellant requirement in this simplified calculation.

That does **not** prove that nuclear electric propulsion would complete a real Mars mission. The first model does not calculate a complete trajectory. It uses an acceleration approximation to screen whether the available thrust might be sufficient for the chosen duration.

The random experiment varies the mission and some NEP system assumptions 2,000 times. NEP is selected 1,288 times, NTP 321 times, and none of the architectures passes in 391 cases. Those counts depend on the chosen ranges and distributions. They are not measured frequencies or real-world probabilities.

A separate trajectory experiment adds a simplified Sun-centered model. It uses circular, coplanar Earth and Mars orbits and loose arrival conditions. It is a useful step toward testing the acceleration approximation, but it leaves out important mission effects such as real planetary ephemerides, Earth escape, Mars capture, and planetary gravity. It is not a flight plan.

The honest conclusion is that the project currently demonstrates a reproducible way to explore propulsion trade-offs and uncertainty. It has not yet demonstrated a new propulsion invention. The next serious step is to improve and validate the trajectory optimizer against a published benchmark or an independent tool.
