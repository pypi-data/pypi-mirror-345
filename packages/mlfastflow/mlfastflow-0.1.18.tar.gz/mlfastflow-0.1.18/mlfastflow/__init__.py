"""MLFastFlow - packages for fast dataflow and workflow processing."""

__version__ = "0.1.18"

# Import core components
from mlfastflow.core import Flow

# Import sourcing functionality
from mlfastflow.sourcing import Sourcing

# Import BigQueryClient
from mlfastflow.bigqueryclient import BigQueryClient

# Make these classes available at the package level
__all__ = ['Flow', 'Sourcing', 'BigQueryClient']
