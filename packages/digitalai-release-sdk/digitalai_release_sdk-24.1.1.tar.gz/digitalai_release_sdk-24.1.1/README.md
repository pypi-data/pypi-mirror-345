# Digital.ai Release SDK

The Digital.ai Release Python SDK (digitalai-release-sdk) is a set of tools that developers can use to create container-based tasks.  

Developers can use the `BaseTask` abstract class as a starting point to define their custom tasks and take advantage of the other methods and attributes provided by the SDK to interact with the task execution environment.

## Installation

```shell script
pip install digitalai-release-sdk
```
## Task Example: hello.py

```python
from digitalai.release.integration import BaseTask

class Hello(BaseTask):
    
    def execute(self) -> None:

        # Get the name from the input
        name = self.input_properties['yourName']
        if not name:
            raise ValueError("The 'yourName' field cannot be empty")

        # Create greeting
        greeting = f"Hello {name}"

        # Add greeting to the task's comment section in the UI
        self.add_comment(greeting)

        # Put greeting in the output of the task
        self.set_output_property('greeting', greeting)

 ```

## Documentation
Read more about Digital.ai Release Python SDK [here](https://docs.digital.ai/release/docs/category/python-sdk)