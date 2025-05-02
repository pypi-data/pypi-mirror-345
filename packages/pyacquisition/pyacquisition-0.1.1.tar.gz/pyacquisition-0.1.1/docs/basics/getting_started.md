# Getting Started

On this page, we will run through a step-by-step example in which we will build an experiment from scratch. Much of the "out-of-the-box" functionality will be demonstrated.


## Experiment Setup

The simplest way start an experiment is to to instantiate an `Experiment` using the convenience `.from_config` classmethod that takes the path to a configuration file (`.toml`) as its only argument. Then, simply call `Experiment.run()` to begin the experiment:


```python
from pyacquisition import Experiment

my_experiment = Experiment.from_config('config.toml')
my_experiment.run()
```

## Simple Configuration

```toml
[main]
root_path = "C://Data"
```