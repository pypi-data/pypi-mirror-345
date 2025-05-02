# Honeybee-REVIVE:
### A Phius-REVIVE plugin for Honeybee and Ladybug-Tools

Honeybee-REVIVE is a free plugin for [Ladybug Tools](https://www.ladybug.tools/) which enables users to add detailed [Phius-REVIVE](https://www.phius.org/phius-revive-2024) style attributes to their models alongside the normal Honeybee inputs. 

This plugin is designed as a plugin for Honeybee v1.8. It can also be utilized by the Ladybug toolkit for building up models within [Rhino 3D v8+](https://www.rhino3d.com/) and Grasshopper using the [honeybee_grasshopper_revive](https://github.com/PH-Tools/honeybee_grasshopper_REVIVE) tools. This extension relies on the [PH-ADORB](https://github.com/PH-Tools/PH_ADORB) library to execute the actual carbon-cost calculations.


#### *Note: PH-Tools and this PH-ADORB library is in no way affiliated with Phius, and the library here is neither reviewed, nor approved by Phius for use in complying with the REVIVE program.*

<details>
<summary><strong>Packages:</strong></summary>

- **honeybee_revive:** Extend the basic Honeybee extension package with new Phius-REVIVE specific model elements.

- **honeybee_energy_revive:** Extend the Honeybee-Energy package with new Phius-REVIVE style attributes for elements such as windows, hvac and construction assemblies.

- **honeybee_revive_standards:** Helpful new standards for programs and assemblies which are especially relevant to Passive House practitioners.

</details>

<details>
<summary><strong>Installation:</strong></summary>

This package is [hosted on PyPi](https://pypi.org/project/honeybee-REVIVE/). To install the latests version of the package:

```python
>>> pip install honeybee-revive
```
</details>

<details>
<summary><strong>Development:</strong></summary>

### Development [Local]:
Honeybee-REVIVE is free and open-source. We welcome any and all thoughts, opinions, and contributions! To get setup for local development:
1. **Fork** this GitHub repository to your own GitHub account.
1. **Clone** the new repository-fork onto your own computer.
![Screenshot 2024-10-01 at 3 48 51 PM](https://github.com/user-attachments/assets/6b7e0853-4b90-4b05-9344-8ced9ff04de9)
1. Setup a **virtual environment** on your own computer.
1. Install the required **dependencies**: `>>> pip install '.[dev]'`
1. *Recommended* Create a new **Branch** for all your changes.
1. Make the changes to the code.
1. Add tests to cover your new changes.
1. Submit a **Pull-Request** to merge your new Branch and its changes into the main branch.

### Development [Tests]:
Note that Honeybee-REVIVE uses [`pytest`](https://docs.pytest.org/en/stable/#) to run all of the automated testing. Please be sure to include tests for any contributions or edits.

### Development [Deployment]:
This package is [published on PyPi](https://pypi.org/project/honeybee-REVIVE/). To deploy a new version:
1. Update the [pyproject.toml version number](https://github.com/PH-Tools/honeybee_REVIVE/blob/04039ea13f699cd81a76f036c44af628b9dba946/pyproject.toml#L3)
1. Publish a new release through the GitHub repository page:
![Screenshot 2024-09-26 at 10 05 14 AM](https://github.com/user-attachments/assets/8e831f39-03ee-4704-8a78-f3353960b3ea)
1. This is will trigger the [ci.yaml](https://github.com/PH-Tools/honeybee_REVIVE/blob/main/.github/workflows/ci.yaml) GitHub Action, build, and deploy the package.
</details>

<details>
<summary><strong>More Information:</strong></summary>

For more information on the use of these tools, check out the the Passive House Tools website:
[https://www.PassiveHouseTools.com](https://www.PassiveHouseTools.com)

### Contact:
For questions about Honeybee-REVIVE, feel free to reach out at: PHTools@bldgtyp.com

You can also post questions or comment to the Ladybug-Tools use forum at: [https://discourse.ladybug.tools/](https://discourse.ladybug.tools/)
</details>

![Tests](https://github.com/PH-Tools/honeybee_revive/actions/workflows/ci.yaml/badge.svg)
