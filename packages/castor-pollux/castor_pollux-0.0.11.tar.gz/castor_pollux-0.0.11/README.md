# castor-pollux
Castor-Pollux (the twin sons of Zeus, routinely called 'gemini') is a pure REST API library for interacting with Google Generative AI API.

## Without (!!!):
- any whiff of 'Vertex' or GCP;
- any signs of 'Pydantic' or unnecessary (and mostly useless) typing;
- any other dependencies of other google packages trashed into the dumpster `google-genai` package.

## Installation:
<pre>
  pip install castor-pollux
</pre>
Then:
```Python
  # Python
  import castor_pollux.rest as cp
```
## A text continuation request:
```Python
import castor_pollux.rest as cp
from yaml import safe_load as yl

kwargs = """  # this is a string in YAML format
  model:        gemini-2.5-pro-exp-03-25    # thingking model
  # system_instruction: ''                  # will prevail if put here
  mime_type:    text/plain                  #
  modalities:
    - TEXT                                  # text for text
  max_tokens:   10000
  n:            2                           # 1 is not mandatory
  stop_sequences:
    - STOP
    - "\nTitle"
  temperature:  0.5                         # 0 to 1.0
  top_k:        10                          # number of tokens to consider.
  top_p:        0.5                         # 0 to 1.0
  thinking:     24576                       # max thinking tokens budget; 
                                            # 0 to prevent 'thinking'
"""

instruction = 'You are Joseph Jacobs, you retell folk tales.'

text_to_continue = 'Once upon a time, when pigs drank wine '

machine_responses = cp.continuation(
    text=text_to_continue,
    instruction=instruction,
    **yl(kwargs)
)
```
## A multi-turn conversation continuation request:
```Python
import castor_pollux.rest as cp
from yaml import safe_load as yl

kwargs = """  # this is a string in YAML format
  model:        gemini-2.5-pro-exp-03-25    # thingking model
  # system_instruction: ''                  # will prevail if put here
  mime_type:    text/plain                  #
  modalities:
    - TEXT                                  # text for text
  max_tokens:   10000
  n:            1                           # 1 is not mandatory
  stop_sequences:
    - STOP
    - "\nTitle"
  temperature:  0.5                         # 0 to 1.0
  top_k:        10                          # number of tokens to consider.
  top_p:        0.5                         # 0 to 1.0
  thinking:     24576                       # max thinking tokens budget; 
                                            # 0 to prevent 'thinking'
"""

previous_turns = """
  - role: user
    parts:
      - text: Can we change human nature?
    
  - role: model
    parts:
      - text: Of course, nothing can be simpler. You just re-educate them.
"""

human_response_to_the_previous_turn = 'That is not true. Think again.'

instruction = 'I am an expert in critical thinking. I analyse.'

machine_responses = cp.continuation(
    text=human_response_to_the_previous_turn,
    contents=yl(previous_turns),
    instruction=instruction,
    **yl(kwargs)
)
``` 
## Recorder, logs, records and multi-turn conversations
`castor-pollux` can work with `grammateus` recorder if you pass an initialized instance of it in your calls.
```Python
from yaml import safe_load as yl
from grammateus import Grammateus
from castor_pollux import rest as cp

records = '/home/<user>/Documents/Fairytales/'

kwargs = """  # this is a string in YAML format
  model:        gemini-2.5-flash-preview-04-17
  mime_type:    text/plain
  modalities:
    - TEXT
  max_tokens:   32000
  n:            1  # no longer a mandatory 1
  stop_sequences:
    - STOP
    - "\nTitle"
  temperature:  0.5
  top_k:        10
  top_p:        0.5
  thinking:     24576  # thinking tokens budget. 24576
"""

instruction = 'I am Joseph Jacobs. I retell folk tales'

text_to_continue = 'Once upon a time, when pigs drank wine'

machine_text = cp.continuation(
    text=text_to_continue,
    instruction=instruction,
    recorder=Grammateus(records),    # https://pypi.org/project/grammateus/
    **yl(kwargs)
)
```
