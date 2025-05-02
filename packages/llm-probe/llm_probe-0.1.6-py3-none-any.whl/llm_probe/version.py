"""LLM-Probe version information."""

import packaging.version

version = "0.1.6"
package_version = packaging.version.parse(version)
__version__ = str(package_version)
