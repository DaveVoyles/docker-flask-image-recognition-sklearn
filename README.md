
# Docker container running a flask web server for image classification using Scikit-Learn

#### Author(s): The team at TD Bank | Dave Voyles, MSFT | [@DaveVoyles](http://www.twitter.com/DaveVoyles)
#### URL: [www.DaveVoyles.com](http://www.davevoyles.com)

Create a docker container and host it in Azure with this tutorial
----------

### Buld the image & run it locally
In a terminal, navigate to the folder containing the .dockerfile.
This will create a new docker image and tag it with the name of your repository, name of the image, and the version
It will take a few minutes to download & install all of the required files
```
docker build -t davevoyles/flask-sklearn-classification:latest . 
```

Run the image locally in debug mode and expose ports 5000
```
docker run -d --name flask-sklearn-classification -p 5000:5000 davevoyles/flask-sklearn-classification
```


### Verify everything works locally, then remove the image
``docker ps
docker logs flask-sklearn-classification
docker rm -f docker logs flask-sklearn-classification```

Push to docker hub account name/repository. This may take a few minutes
```
docker push davevoyles/flask-sklearn-classification
```

### Login to Azure via CLI
```
az login 
```

### Create resource group (one time)
```
az group create -l eastus -n dv-containers-rg
```

### Create a container in Azure
Create a container in azure w/ a public IP so that we can make HTTP post requests and expose port 5000.
Pull image from dockerhub *account/repository/tag*
```
az container create --resource-group dv-containers-rg --name dv-flask-container --image davevoyles/flask-sklearn-classification:latest --ip-address public --location eastus --ports 5000
```

Check status of container by querying the ip address. You may have to wait a few minutes for it to complete.
```
az container show --resource-group dv-containers-rg --name dv-flask-container --query ipAddress
```

It should return with something like this:

```json
{
  "additionalProperties": {},
  "dnsNameLabel": null,
  "fqdn": null,
  "ip": "40.114.107.193",
  "ports": [
    {
      "additionalProperties": {},
      "port": 5000,
      "protocol": "TCP"
    }
  ]
}
```

### View the logs for your container      

``` 
az container logs --resource-group dv-containers-rg --name dv-flask-container
```


You can also log into the Azure portal in your browser to see if your container service is running.

![Azure Portal 1](/Images/az-portal-1.png)

![Azure Portal 2](/Images/az-portal-2.png)



## Example requests
Swap the IP address listed below with your own. These will return the label of the image you passed in. For example:

```json 
{"classification": "insulated_jackets"}
```

```json
curl -X POST \
  http://40.117.156.248:5000/classify \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
"url":"https://images.thenorthface.com/is/image/TheNorthFace/NF0A2VD5_KX7_hero?$638x745$"
}'
```

```json
curl -X POST \
  http://40.121.22.230:5000/classify \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
"url":"https://images.thenorthface.com/is/image/TheNorthFace/NF0A2VD5_KX7_hero?$638x745$"
}'
```

```json
curl -X POST \
  http://40.121.22.230:5000/classify \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
"url":"https://m.fortnine.ca/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/catalogimages/gmax/gm45-half-helmet-matte-black-xs.jpg"
}'
```

```json
curl -X POST \
  http://40.121.22.230:5000/classify \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
"url":"https://images.sportsdirect.com/images/products/90800440_l.jpg"
}'
```

```json
curl -X POST \
  http://40.121.22.230:5000/classify \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{
"url":"https://mec.imgix.net/medias/sys_master/high-res/high-res/8860680618014/5052314-SIL00.jpg?w=600&h=600&auto=format&q=60&fit=fill&bg=FFF"
}'
```


### Delete the container

```
az container delete --name ohmyservice2 --resource-group t9modelmgmt
```
