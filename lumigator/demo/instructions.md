# Instructions for the SDK demo

* Clone the repo
  * `git clone git@github.com:mozilla-ai/lumigator.git`
  * `cd lumigator`
* Create the images
  * `make start-lumigator-build`
* Create and activate a new environment using `uv`
  * `cd lumigator/demo`
  * `uv venv demoenv`
  * `source demoenv/bin/activate`
* Copy the sample data
  * `cp ../python/mzai/sample_data/dialogsum_exc.csv .`
* Download the latest build SDK wheels (_note: it seems that wget or curl will get a 404, download them manually from the browser_)
  * SDK package present at `https://github.com/mozilla-ai/lumigator/actions/runs/11579739919/artifacts/2119216882`
  * `unzip "SDK packages.zip"`
* Install the wheels in the environment
  * `uv pip install lumigator_sdk-0.1.0rc1-py3-none-any.whl`
* Run the demo
  * `python demo.py`