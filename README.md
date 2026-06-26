# pytest api gateway
This is a pytest plugin allow you to add an interface for your pytest suite using http request

## Requests

### Run request
used to run a job
~~~
curl --request POST \
  --url {URL}/run \
  --header 'Content-Type: application/json' \
  --data '{"args":[{ARGS}}}'
~~~
args var here is writen the same way in yaml file for example:
~~~
{"args":["test/","-m","smoke","--json-report"]}
~~~
the response of this request is the following
~~~
{
	"id": {UUID},
	"status": "running"
}
~~~
the uuid var here is used as an id for this run that can be used in another request

### status Request
used to look at jobs status
~~~
curl --request GET \
  --url {URL}/status/{UUID} 
~~~
the response can be 
~~~
{
	"id": {UUID},
	"status": "running"
}
~~~
or
~~~
{
	"id": {UUID},
	"results": {EXITCODE},
	"status": "done"
}
~~~
the exitcode here is the same as pytest exit code
### status all Request
used to get all the run jobs
~~~
curl --request GET \
  --url {URL}/status/all 
~~~
