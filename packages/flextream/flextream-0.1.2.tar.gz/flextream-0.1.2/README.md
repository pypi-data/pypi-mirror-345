# Flextream 🏞️

Utility library forstreaming to Azure Event hubs. Handles background threaded process, and connection caching to minimise bottlenecks when streaming data over hubs.

Can be pip installed with `pip install flextream`.

To use, you'll mostly, just need a single function:

```python
from flextream import send_to_event_hub

send_to_event_hub(
  {"message": "hello world!", "also_some_numbers": [1, 2, 3]},
  namespace="namestapce-name.servicebus.windows.net",
  eventhub="my-first-eventhub",
  latency=10,
)
```

In the above example, bespoke credentials haven't been passed into the `credential` keyword, so it will fall back to authenticating with `DefaultAzureCredentials`. The `latency` parameter is the maximum amount of time in seconds that a message will be held onto before being sent in a background triggered thread.

Any other messages sent to the eventhub during the wait time will be bundled alongside in a batch for efficiency.
